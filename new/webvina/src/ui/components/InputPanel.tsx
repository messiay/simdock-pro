import { useState } from 'react';
import { useDockingStore } from '../../store/dockingStore';
import { ReceptorUpload, LigandUpload, CorrectPoseUpload } from './FileUpload';
import { DockingBoxPanel } from './DockingBoxPanel';
import { VinaOptionsPanel } from './VinaOptionsPanel';
import { vinaService } from '../../services/vinaService';
import { apiService } from '../../services/apiService';
import { calculateGridboxFromReceptor } from '../../utils/gridboxCalculator';
import { isValidPdbqt } from '../../utils/pdbqtParser';
import { Crosshair, AlertTriangle, PlayCircle } from 'lucide-react';
import '../styles/InputPanel.css';

export function InputPanel() {
    const {
        receptorFile,
        ligandFile,
        params,
        setParams,
        setRunning,
        setProgress,
        setStatusMessage,
        addConsoleOutput,
        clearConsoleOutput,
        setResult,
        setActiveTab,
        dockingEngine,
        setDockingEngine
    } = useDockingStore();

    const [autoRemoveNonProtein, setAutoRemoveNonProtein] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const canRun = receptorFile && ligandFile;

    const handleAutoBox = () => {
        if (!ligandFile?.content) return;

        const gridbox = calculateGridboxFromReceptor(
            receptorFile?.content || '',
            ligandFile.content,
            5
        );

        setParams(gridbox);
    };

    const handleRunDocking = async () => {
        if (!receptorFile?.content || !ligandFile?.content) {
            setError('Please upload both receptor and ligand files');
            return;
        }

        setError(null);
        setRunning(true);
        setStatusMessage('Initializing...');
        setActiveTab('running');
        clearConsoleOutput();

        // Immediate feedback
        addConsoleOutput("=== Starting Docking Job ===");
        addConsoleOutput("Input validation passed.");


        try {
            // Prepare files (convert to PDBQT if needed)
            let receptorPdbqt = receptorFile.content;
            let ligandPdbqt = ligandFile.content;

            // Convert PDB to PDBQT via backend API
            if (receptorFile.format === 'pdb' && !isValidPdbqt(receptorPdbqt)) {
                addConsoleOutput('Converting receptor to PDBQT via API...');
                try {
                    receptorPdbqt = await apiService.convertPdbToPdbqt(receptorPdbqt);
                    addConsoleOutput('Receptor conversion successful.');
                } catch (convErr: any) {
                    addConsoleOutput(`ERROR: Receptor conversion failed: ${convErr.message}`);
                    throw new Error(`Receptor conversion failed: ${convErr.message}`);
                }
            }

            // Convert SDF/MOL to PDBQT via backend API
            if (ligandFile.format === 'sdf' || ligandPdbqt.includes('V2000') || ligandPdbqt.includes('$$$$') || ligandPdbqt.includes('M  END')) {
                addConsoleOutput('Converting ligand SDF to PDBQT via API...');
                try {
                    ligandPdbqt = await apiService.convertSdfToPdbqt(ligandPdbqt);
                    addConsoleOutput('Ligand conversion successful.');
                } catch (convErr: any) {
                    addConsoleOutput(`Warning: SDF conversion failed: ${convErr.message}`);
                }
            } else if (ligandFile.format === 'pdb' && !isValidPdbqt(ligandPdbqt)) {
                addConsoleOutput('Converting ligand PDB to PDBQT via API...');
                try {
                    ligandPdbqt = await apiService.convertPdbToPdbqt(ligandPdbqt);
                    addConsoleOutput('Ligand conversion successful.');
                } catch (convErr: any) {
                    addConsoleOutput(`Warning: PDB conversion failed: ${convErr.message}`);
                }
            }

            // Final validation - ensure we have content
            if (!ligandPdbqt || ligandPdbqt.trim().length === 0) {
                throw new Error('Ligand content is empty after conversion');
            }
            addConsoleOutput(`Ligand ready: ${ligandPdbqt.length} characters`);

            // Run docking
            const result = await vinaService.runDocking(
                receptorPdbqt,
                ligandPdbqt,
                params,
                (message, progress) => {
                    setProgress(progress);
                    setStatusMessage(message);
                    addConsoleOutput(message);
                }
            );

            setResult(result);
            setActiveTab('output');
            addConsoleOutput('\n=== Docking Complete ===');
            addConsoleOutput(`Found ${result.poses.length} binding modes`);

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Docking failed';
            setError(errorMessage);
            addConsoleOutput(`ERROR: ${errorMessage}`);
        } finally {
            setRunning(false);
            setProgress(0);
            setStatusMessage('');
        }
    };

    // Example files removed as per user request


    return (
        <div className="input-panel">
            <div className="input-section">
                <div className="section-header">
                    <h2>Input Files</h2>
                </div>

                <div className="files-grid">
                    <div className="file-column">
                        <ReceptorUpload />

                        <div className="file-option">
                            <input
                                type="checkbox"
                                id="autoRemove"
                                checked={autoRemoveNonProtein}
                                onChange={(e) => setAutoRemoveNonProtein(e.target.checked)}
                            />
                            <label htmlFor="autoRemove">
                                Auto-remove non-protein atoms
                            </label>
                        </div>
                    </div>

                    <div className="file-column">
                        <LigandUpload />
                        <CorrectPoseUpload />

                        {ligandFile && (
                            <button className="auto-box-btn" onClick={handleAutoBox}>
                                <Crosshair size={16} /> Auto-calculate box from ligand
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* ENGINE SELECTION */}
            <div className="engine-section">
                <div className="section-header">
                    <h2>Docking Engine</h2>
                </div>
                <div className="engine-toggle-group">
                    <button
                        className={`engine-btn ${dockingEngine === 'vina' ? 'active' : ''}`}
                        onClick={() => setDockingEngine('vina')}
                    >
                        AutoDock Vina
                    </button>
                    <button
                        className={`engine-btn ${dockingEngine === 'smina' ? 'active' : ''}`}
                        onClick={() => setDockingEngine('smina')}
                    >
                        Smina (Vinardo)
                    </button>
                </div>
            </div>

            <div className="params-section">
                <div className="params-grid">
                    <DockingBoxPanel />
                    <VinaOptionsPanel />
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <span><AlertTriangle size={16} /></span> {error}
                </div>
            )}

            <div className="run-section">
                <button
                    className="run-btn"
                    onClick={handleRunDocking}
                    disabled={!canRun}
                >
                    <span className="run-icon"><PlayCircle size={20} /></span>
                    Start Docking
                </button>

                {!canRun && (
                    <p className="run-hint">
                        Upload both receptor and ligand files to start docking
                    </p>
                )}
            </div>
        </div>
    );
}
