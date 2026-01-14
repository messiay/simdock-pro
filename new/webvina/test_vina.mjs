import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Mock Worker for Node.js environment
global.Worker = class Worker {
    constructor(url) {
        console.log(`[MockWorker] Created worker for ${url}`);
    }
    postMessage(msg) {
        console.log(`[MockWorker] postMessage:`, msg);
        if (msg.cmd === 'load') {
            console.log("[MockWorker] Simulating 'loaded' response...");
            setTimeout(() => {
                if (this.onmessage) {
                    this.onmessage({ data: { cmd: 'loaded' } });
                }
            }, 50);
        }
    }
    terminate() {
        console.log(`[MockWorker] terminate`);
    }
    on(event, handler) {
        // Node worker style? No, Vina uses browser style 'onmessage' etc usually
    }
};

async function run() {
    console.log("Starting Vina Node.js Test...");

    // Mock Worker environment
    global.self = global;
    global.self.location = { href: 'http://localhost/dockingWorker.js' }; // Mock href for _scriptDir

    // Load vina_classic.js script content
    const vinaClassicPath = path.join(__dirname, 'public/webina/vina_classic.js');
    const vinaClassicScript = fs.readFileSync(vinaClassicPath, 'utf8');

    // Eval the script to define WEBINA_MODULE on global/self
    // This simulates importScripts behavior
    (0, eval)(vinaClassicScript);

    if (typeof global.WEBINA_MODULE === 'undefined') {
        throw new Error("WEBINA_MODULE not defined after loading vina_classic.js");
    }

    const receptorPath = path.join(__dirname, 'public/examples/receptor.pdbqt');
    const ligandPath = path.join(__dirname, 'public/examples/ligand.pdbqt');
    const wasmPath = path.join(__dirname, 'public/webina/vina.wasm');

    if (!fs.existsSync(receptorPath) || !fs.existsSync(ligandPath)) {
        console.error("Input files not found!");
        return;
    }

    const receptor = fs.readFileSync(receptorPath, 'utf8');
    const ligand = fs.readFileSync(ligandPath, 'utf8');

    console.log("Input files read.");

    const wasmBinary = fs.readFileSync(wasmPath);

    try {
        const mod = await global.WEBINA_MODULE({
            wasmBinary: wasmBinary,
            print: (text) => console.log(`[Vina STDOUT]: ${text}`),
            printErr: (text) => console.warn(`[Vina STDERR]: ${text}`),
            stdout: (code) => process.stdout.write(String.fromCharCode(code)),
            stderr: (code) => process.stderr.write(String.fromCharCode(code)),
            onRuntimeInitialized: () => console.log("Runtime initialized."),
            PTHREAD_POOL_SIZE: 0,
            PTHREAD_POOL_SIZE_STRICT: 0,
        });

        console.log("Module Factory completed. Vina loaded.");

        // Write files to virtual FS
        mod.FS.writeFile('/receptor.pdbqt', receptor);
        mod.FS.writeFile('/ligand.pdbqt', ligand);

        console.log("Files written to Virtual FS. Running main...");

        // Run Vina
        // Using center from PARP-1 (4RV6)
        // Center: (-41.81, 3.09, -8.18), Size: (72, 65, 62)
        mod.callMain([
            '--receptor', '/receptor.pdbqt',
            '--ligand', '/ligand.pdbqt',
            '--center_x', '-41.81',
            '--center_y', '3.09',
            '--center_z', '-8.18',
            '--size_x', '72',
            '--size_y', '65',
            '--size_z', '62',
            '--exhaustiveness', '8',
            '--cpu', '1',
            '--out', '/output.pdbqt'
        ]);

        console.log("Main execution finished.");

        if (mod.FS.analyzePath('/output.pdbqt').exists) {
            console.log("Success! Output generated.");
            const output = mod.FS.readFile('/output.pdbqt', { encoding: 'utf8' });
            console.log("--- Output Preview ---");
            console.log(output.substring(0, 500));
            console.log("...");
        } else {
            console.error("Failure! No output file found.");
        }

    } catch (e) {
        console.error("CRITICAL ERROR during execution:", e);
    }
}

run();
