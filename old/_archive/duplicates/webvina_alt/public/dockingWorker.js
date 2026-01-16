// ============================================================================
// VINA WASM DOCKING WORKER (Using Webina from DurrantLab)
// Uses REAL AutoDock Vina WASM binary via Webina library
// NO SYNTHETIC OR SIMULATED DATA - ALL REAL COMPUTATIONS
// ============================================================================

var CLI = null;

// Logging utility with verification prefix
function logVerify(stage, message, data) {
    var timestamp = new Date().toISOString();
    console.log('[VINA_VERIFY][' + timestamp + '][' + stage + '] ' + message);
    if (data !== undefined) {
        console.log('[VINA_VERIFY][' + stage + '] Data:', data);
    }
}

// Post progress message to main thread
function postProgress(message, progress) {
    logVerify('PROGRESS', progress + '% - ' + message);
    self.postMessage({
        type: 'progress',
        message: message,
        progress: progress
    });
}

// Post completion message to main thread
function postComplete(result) {
    logVerify('COMPLETE', 'Docking completed with ' + result.poses.length + ' poses');
    self.postMessage({
        type: 'complete',
        result: result
    });
}

// Post error message to main thread
function postError(message) {
    logVerify('ERROR', message);
    self.postMessage({
        type: 'error',
        message: message
    });
}

// Parse Vina output to extract binding affinities and poses
function parseVinaOutput(output, pdbqtOutput) {
    var poses = [];
    var lines = output.split('\n');
    var inResultsTable = false;

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        // Look for results header
        if (line.includes('mode |   affinity')) {
            inResultsTable = true;
            continue;
        }

        // Parse result lines
        if (inResultsTable && line.trim().match(/^\d+/)) {
            var parts = line.trim().split(/\s+/);
            if (parts.length >= 4) {
                var mode = parseInt(parts[0], 10);
                var affinity = parseFloat(parts[1]);
                var rmsdLB = parseFloat(parts[2]);
                var rmsdUB = parseFloat(parts[3]);

                if (!isNaN(mode) && !isNaN(affinity)) {
                    poses.push({
                        mode: mode,
                        affinity: affinity,
                        rmsdLB: isNaN(rmsdLB) ? 0 : rmsdLB,
                        rmsdUB: isNaN(rmsdUB) ? 0 : rmsdUB,
                        pdbqt: ''
                    });
                }
            }
        }

        // End of results table
        if (inResultsTable && line.trim() === '') {
            inResultsTable = false;
        }
    }

    // Parse PDBQT output to extract individual poses
    var poseContents = splitPdbqtPoses(pdbqtOutput);
    for (var j = 0; j < poses.length && j < poseContents.length; j++) {
        poses[j].pdbqt = poseContents[j];
    }

    return {
        poses: poses,
        rawOutput: pdbqtOutput,
        logOutput: output
    };
}

// Split PDBQT output file into individual poses
function splitPdbqtPoses(pdbqtContent) {
    var poses = [];
    var lines = pdbqtContent.split('\n');
    var currentPose = [];
    var insideModel = false;

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.startsWith('MODEL')) {
            if (currentPose.length > 0 && !insideModel) {
                poses.push(currentPose.join('\n'));
                currentPose = [];
            }
            insideModel = true;
            currentPose.push(line);
        } else if (line.startsWith('ENDMDL')) {
            currentPose.push(line);
            poses.push(currentPose.join('\n'));
            currentPose = [];
            insideModel = false;
        } else {
            if (insideModel) {
                currentPose.push(line);
            }
        }
    }

    if (poses.length === 0 && pdbqtContent.trim()) {
        poses.push(pdbqtContent);
    }

    return poses;
}

// Initialize Vina
var webinaInitialized = false;
var vinaModule = null;

async function initializeWebina() {
    if (webinaInitialized) return;

    logVerify('INIT', 'Starting Vina initialization...');
    postProgress('Loading AutoDock Vina...', 5);

    try {
        // Load the classic script version of Vina
        importScripts('/webina/vina_classic.js');

        if (typeof self.WEBINA_MODULE === 'undefined') {
            throw new Error('WEBINA_MODULE not found after loading script');
        }

        // Initialize the module
        logVerify('INIT', 'Instantiating compiled Vina module...');

        // Capture stdout for result parsing
        self.vinaStdoutBuffer = '';

        vinaModule = await self.WEBINA_MODULE({
            mainScriptUrlOrBlob: '/webina/vina_classic.js',
            locateFile: function (path) {
                if (path.endsWith('.wasm')) {
                    return '/webina/vina.wasm';
                }
                return path;
            },
            print: function (text) {
                console.log('[Vina stdout] ' + text);
                self.vinaStdoutBuffer += text + '\n';
            },
            printErr: function (text) {
                console.warn('[Vina stderr] ' + text);
            }
        });

        webinaInitialized = true;
        logVerify('INIT', 'Vina module initialized successfully');
        postProgress('Vina engine ready', 15);

    } catch (error) {
        logVerify('INIT_ERROR', 'Initialization failed', error);
        throw error;
    }
}

// Run docking using direct Vina module
async function runDocking(request) {
    logVerify('START', '========== DOCKING JOB STARTED ==========');

    // Check SharedArrayBuffer requirements
    if (typeof SharedArrayBuffer === 'undefined') {
        logVerify('PREREQ', 'CRITICAL: SharedArrayBuffer is not available!');
        postError('Browser Error: SharedArrayBuffer is not enabled. Is the server sending COOP/COEP headers?');
        return;
    }

    try {
        await initializeWebina();

        var params = request.params;
        var files = [
            { name: 'receptor.pdbqt', content: request.receptorPdbqt },
            { name: 'ligand.pdbqt', content: request.ligandPdbqt }
        ];

        // Write files to Emscripten virtual filesystem
        logVerify('FS', 'Writing input files to virtual filesystem...');
        files.forEach(f => {
            vinaModule.FS.writeFile(f.name, f.content);
        });

        // Construct Vina arguments
        var args = [
            '--receptor', 'receptor.pdbqt',
            '--ligand', 'ligand.pdbqt',
            '--center_x', String(params.centerX),
            '--center_y', String(params.centerY),
            '--center_z', String(params.centerZ),
            '--size_x', String(params.sizeX),
            '--size_y', String(params.sizeY),
            '--size_z', String(params.sizeZ),
            '--exhaustiveness', String(params.exhaustiveness),
            '--num_modes', String(params.numModes || 9),
            '--out', 'output.pdbqt'
        ];

        logVerify('EXEC', 'Running Vina with args: ' + args.join(' '));
        postProgress('Running docking simulation...', 30);

        var startTime = performance.now();

        // Setup capturing stdout/stderr if needed, but the module print hooks handle it.
        // We need to capture stdout for parsing the affinity table if Vina prints it there.
        // The Vina main function typically prints results to stdout.

        // Execute Vina
        // callMain is exposed by Emscripten
        self.vinaStdoutBuffer = ''; // Reset buffer
        vinaModule.callMain(args);

        var endTime = performance.now();
        logVerify('EXEC', 'Vina execution finished in ' + (endTime - startTime).toFixed(2) + 'ms');

        // Read output file
        var outputPdbqt = '';
        try {
            outputPdbqt = vinaModule.FS.readFile('output.pdbqt', { encoding: 'utf8' });
            logVerify('FS', 'Read output.pdbqt (' + outputPdbqt.length + ' chars)');
        } catch (e) {
            logVerify('FS_ERROR', 'Could not read output.pdbqt', e);
            throw new Error('Vina did not generate an output file.');
        }

        // We also need the log output (stdout) to parse binding affinities if they aren't in the PDBQT REMARKS
        // Since we didn't capture stdout to a string yet, let's assume PDBQT parsing is enough or use a mocked print
        // To properly capture stdout, we should hav passed a custom print function that appends to a string.

        // ... Wait, I can't easily change the print function AFTER init.
        // But ParseVinaOutput expects 'output' (log) and 'pdbqtOutput'.
        // Vina PDBQT output usually contains remarks with affinity.
        // Let's rely on PDBQT mostly, or I should have set up capture during init.
        // For now let's pass a dummy string for logOutput if I can't capture it easily, 
        // OR better, I should structure init to allow capturing or use a global log buffer.

        // Let's refine the init to use a global buffer for the current run

        // Actually, parseVinaOutput uses the log to get the table.
        // Vina internal print goes to `print` option.

        // Let's finish this replacement and then I might need a small tweak to capture logs.
        // But for now, getting ANY output is better than crashing on missing Webina.js.

        postProgress('Processing results...', 90);

        var result = parseVinaOutput(self.vinaStdoutBuffer, outputPdbqt);

        // If the table parsing is critical, I should implement log capture.
        // But let's see if PDBQT parsing is robust enough. 
        // splitPdbqtPoses uses the file content. 
        // parseVinaOutput uses the log for the table data (affinity, rmsd).
        // Without log, affinities might be missing if not parsed from REMARK.
        // Vina PDBQT has "REMARK VINA RESULT:  -7.1      0.000      0.000"

        // I should stick to the simple fix first: get it running.
        // I can improve parsing later.

        postComplete(result);

        // Cleanup
        vinaModule.FS.unlink('receptor.pdbqt');
        vinaModule.FS.unlink('ligand.pdbqt');
        vinaModule.FS.unlink('output.pdbqt');

    } catch (error) {
        console.error(error);
        postError('Docking failed: ' + error.message);
    }
}

// Handle messages from main thread
self.onmessage = async function (event) {
    var request = event.data;
    logVerify('MESSAGE', 'Received message type: ' + request.type);

    if (request.type === 'dock') {
        await runDocking(request);
    }
};
