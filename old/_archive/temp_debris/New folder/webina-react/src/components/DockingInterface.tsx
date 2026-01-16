import React, { useState } from 'react';
import { WebinaService } from '../services/WebinaService';
import type { IVinaParams } from '../services/types';
import { ConfigPanel } from './ConfigPanel';
import { InputPanel } from './InputPanel';
import { MoleculeViewer } from './MoleculeViewer';

export const DockingInterface: React.FC = () => {
    const [receptor, setReceptor] = useState('');
    const [ligand, setLigand] = useState('');
    const [params, setParams] = useState<IVinaParams>({
        center_x: 0, center_y: 0, center_z: 0,
        size_x: 20, size_y: 20, size_z: 20,
        exhaustiveness: 8
    });
    const [logs, setLogs] = useState<string>('');
    const [output, setOutput] = useState<string>('');
    const [running, setRunning] = useState(false);

    const handleParamChange = (key: keyof IVinaParams, value: any) => {
        console.log(`Param changed: ${key} = ${value}`);
        setParams(prev => ({ ...prev, [key]: value }));
    };

    const runDocking = async () => {
        console.log("Run Docking clicked");
        console.log("Receptor length:", receptor.length);
        console.log("Ligand length:", ligand.length);

        if (!receptor.trim() || !ligand.trim()) {
            console.error("Validation failed: Receptor or Ligand missing");
            alert("Please provide both receptor and ligand PDBQT data.");
            return;
        }

        // Basic PDBQT validation to prevent worker crash (Uncaught 280280)
        const isValidPDBQT = (text: string) => {
            return text.includes("ATOM") || text.includes("HETATM");
        };

        if (!isValidPDBQT(receptor)) {
            alert("Invalid Receptor Data: Must contain ATOM records.");
            return;
        }
        if (!isValidPDBQT(ligand)) {
            alert("Invalid Ligand Data: Must contain ATOM or HETATM records.");
            return;
        }

        setRunning(true);
        setLogs("Starting docking...\n");
        setOutput("");

        const service = WebinaService.getInstance();
        console.log("WebinaService instance retrieved:", service);

        try {
            await service.start(params, receptor, ligand, {
                onDone: (outTxt, stdOut, stdErr) => {
                    console.log("Docking callback: DONE");
                    setRunning(false);
                    setLogs(prev => prev + "\n--- DONE ---\n" + stdOut + "\nErrors:\n" + stdErr);
                    setOutput(outTxt);
                },
                onError: (err) => {
                    console.error("Docking callback: ERROR", err);
                    setRunning(false);
                    setLogs(prev => prev + "\nERROR: " + err);
                },
                onStdout: (txt) => {
                    // console.log("Docking callback: STDOUT", txt); 
                    setLogs(prev => prev + txt + "\n");
                },
                onStderr: (txt) => {
                    // console.warn("Docking callback: STDERR", txt);
                    setLogs(prev => prev + "[ERR] " + txt + "\n");
                }
            });
        } catch (e) {
            console.error("Error invoking service.start", e);
            setRunning(false);
        }
    };

    const downloadOutput = () => {
        const blob = new Blob([output], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'docked_ligand.pdbqt';
        a.click();
    };

    return (
        <div className="container mx-auto p-4 flex flex-col gap-4">
            <h1 className="text-3xl font-bold text-center mb-8">Webina React</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <InputPanel label="Receptor" value={receptor} onChange={setReceptor} />
                    <InputPanel label="Ligand" value={ligand} onChange={setLigand} />
                </div>
                <div>
                    <MoleculeViewer receptor={receptor} ligand={ligand} />
                    <ConfigPanel params={params} onChange={handleParamChange} />

                    <div className="mt-4 p-4 bg-gray-800 rounded-lg">
                        <button
                            onClick={runDocking}
                            disabled={running}
                            className={`w-full py-3 rounded font-bold text-lg ${running ? 'bg-gray-600' : 'bg-blue-600 hover:bg-blue-500'}`}
                        >
                            {running ? 'Docking...' : 'Start Docking'}
                        </button>
                    </div>

                    {output && (
                        <div className="mt-4 p-4 bg-green-900 rounded-lg">
                            <h3 className="font-bold">Docking Complete</h3>
                            <button onClick={downloadOutput} className="mt-2 text-white underline">Download Output PDBQT</button>
                        </div>
                    )}
                </div>
            </div>

            <div className="p-4 bg-black text-green-400 font-mono text-xs h-64 overflow-auto rounded-lg whitespace-pre-wrap">
                {logs}
            </div>
        </div>
    );
};
