import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File as FileIcon, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const API_BASE = 'http://localhost:8000'; // Assume localhost for now

const FileDrop = ({ projectName, onUploadComplete }) => {
    const [uploads, setUploads] = useState({}); // { filename: { status: 'pending'|'uploading'|'done'|'error', steps: [], progress: 0 } }
    const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'fetch'
    const [fetchId, setFetchId] = useState('');
    const [fetchSource, setFetchSource] = useState('pdb'); // 'pdb' | 'uniprot'

    const onDrop = useCallback((acceptedFiles) => {
        // 1. Validate Limit (Frontend check)
        if (acceptedFiles.length > 5) {
            alert("Student Guard: You can only upload up to 5 ligands at a time!");
            return;
        }

        const newUploads = {};
        acceptedFiles.forEach(file => {
            newUploads[file.name] = { file, status: 'pending', steps: [], progress: 0 };
        });

        setUploads(prev => ({ ...prev, ...newUploads }));
        processUploads(acceptedFiles);
    }, [projectName]);

    const processUploads = async (files) => {
        for (const file of files) {
            updateStatus(file.name, 'uploading', 0, ["STARTING_UPLOAD"]);
            const formData = new FormData();
            formData.append('file', file);

            // Heuristic for category: Simple check
            let category = 'auto';
            if (file.name.endsWith('.pdb')) category = 'receptor';

            try {
                const response = await axios.post(`${API_BASE}/projects/${projectName}/upload?category=${category}`, formData, {
                    onUploadProgress: (progressEvent) => {
                        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    }
                });

                const steps = response.data.processing_steps || ["UPLOAD_COMPLETE"];
                for (const step of steps) {
                    updateStatus(file.name, 'processing', 100, [step]);
                    await new Promise(r => setTimeout(r, 500));
                }

                updateStatus(file.name, 'done', 100, ["READY"]);
                if (onUploadComplete && file.name.endsWith('.pdb')) {
                    onUploadComplete(response.data.path);
                }

            } catch (error) {
                console.error(error);
                updateStatus(file.name, 'error', 0, [error.response?.data?.detail || "Upload Failed"]);
            }
        }
    };

    const handleFetch = async () => {
        // DEBUG: Alert to confirm click
        console.log(`Fetch triggered: ${fetchSource} ${fetchId}`);

        if (!fetchId) return;

        let targetFilename = '';
        if (fetchSource === 'pubchem') {
            // For PubChem, we don't know the exact filename until we get CID, but we can guess or rely on backend return
            // Standardizing on query for now
            targetFilename = `PubChem_Search_${fetchId}.sdf`;
        } else {
            targetFilename = fetchSource === 'pdb' ? `${fetchId.toUpperCase()}.pdb` : `AF-${fetchId.toUpperCase()}.pdb`;
        }

        // Initialize status
        setUploads(prev => ({
            ...prev,
            [targetFilename]: { status: 'uploading', steps: ["CONNECTING_TO_DATABASE"], progress: 0 }
        }));

        try {
            let url = '';
            if (fetchSource === 'pubchem') {
                url = `${API_BASE}/projects/${projectName}/fetch/ligand?query=${fetchId}`;
            } else {
                url = `${API_BASE}/projects/${projectName}/fetch?source=${fetchSource}&id=${fetchId}`;
            }

            console.log("Request URL:", url);

            // Call Fetch Endpoint
            const response = await axios.post(url);
            console.log("Response:", response.data);

            // If filename changed (backend returned actual filename), update it
            const actualFilename = response.data.filename;
            if (actualFilename && actualFilename !== targetFilename) {
                // Move status to new key
                setUploads(prev => {
                    const { [targetFilename]: old, ...rest } = prev;
                    return { ...rest, [actualFilename]: { ...old, status: 'processing', steps: ["FOUND_RECORD"] } };
                });
                targetFilename = actualFilename;
            }

            // Replay Steps
            const steps = response.data.processing_steps || ["DOWNLOAD_COMPLETE"];
            for (const step of steps) {
                updateStatus(targetFilename, 'processing', 100, [step]);
                await new Promise(r => setTimeout(r, 400));
            }

            updateStatus(targetFilename, 'done', 100, ["READY"]);
            if (onUploadComplete) {
                // Return path. If receptor, Viewer needs it. If ligand, it just adds to list.
                onUploadComplete(response.data.path);
            }
            setFetchId('');

        } catch (error) {
            console.error("Fetch Logic Error:", error);
            const msg = error.response?.data?.detail || error.message || "Fetch Failed";
            updateStatus(targetFilename, 'error', 0, [msg]);
        }
    };

    const updateStatus = (filename, status, progress, newSteps = []) => {
        setUploads(prev => {
            const current = prev[filename] || {};
            const oldSteps = current.steps || [];
            return {
                ...prev,
                [filename]: {
                    ...current,
                    status,
                    progress,
                    steps: [...oldSteps, ...newSteps]
                }
            };
        });
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    return (
        <div className="w-full max-w-2xl mx-auto p-4">
            {/* Tabs */}
            <div className="flex gap-4 mb-4 justify-center">
                <button
                    onClick={() => setActiveTab('upload')}
                    className={clsx("px-4 py-2 rounded-full text-sm font-bold transition-all", activeTab === 'upload' ? "bg-neon-blue text-white shadow-neon" : "text-gray-400 hover:text-white")}
                >
                    UPLOAD FILE
                </button>
                <button
                    onClick={() => setActiveTab('fetch')}
                    className={clsx("px-4 py-2 rounded-full text-sm font-bold transition-all", activeTab === 'fetch' ? "bg-neon-pink text-white shadow-neon" : "text-gray-400 hover:text-white")}
                >
                    FETCH ID
                </button>
            </div>

            {/* Content Area */}
            {activeTab === 'upload' ? (
                <div
                    {...getRootProps()}
                    className={clsx(
                        "border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer glass-panel",
                        isDragActive ? "border-neon-green bg-neon-green/10" : "border-white/20 hover:border-white/40"
                    )}
                >
                    <input {...getInputProps()} />
                    <Upload className="w-12 h-12 mx-auto mb-4 text-neon-blue" />
                    <p className="text-xl font-bold mb-2">Drop your molecules here</p>
                    <p className="text-sm text-gray-400">PDB, SDF, MOL2 (Max 5 Ligands)</p>
                </div>
            ) : (
                <div className="glass-panel p-8 rounded-xl border border-white/20">
                    <div className="flex gap-2 mb-4">
                        <select
                            value={fetchSource}
                            onChange={(e) => setFetchSource(e.target.value)}
                            className="bg-black/50 border border-white/20 rounded p-2 text-white text-sm outline-none focus:border-neon-pink"
                        >
                            <option value="pdb">RCSB PDB (Receptor)</option>
                            <option value="uniprot">AlphaFold DB (Receptor)</option>
                            <option value="pubchem">PubChem (Ligand)</option>
                        </select>
                        <input
                            type="text"
                            placeholder={
                                fetchSource === 'pdb' ? "Enter PDB ID (e.g. 1CBS)" :
                                    fetchSource === 'uniprot' ? "Enter UniProt ID (e.g. P04637)" :
                                        "Enter Name (e.g. Aspirin) or CID"
                            }
                            value={fetchId}
                            onChange={(e) => setFetchId(e.target.value)}
                            className="flex-1 bg-black/50 border border-white/20 rounded p-2 text-white text-sm outline-none focus:border-neon-pink font-mono uppercase"
                        />
                    </div>
                    <button
                        onClick={handleFetch}
                        disabled={!fetchId}
                        className="w-full bg-neon-pink/20 border border-neon-pink text-neon-pink py-2 rounded hover:bg-neon-pink hover:text-white transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {fetchSource === 'pubchem' ? 'SEARCH & DOWNLOAD LIGAND' : 'FETCH RECEPTOR'}
                    </button>
                </div>
            )}

            <div className="mt-8 space-y-4">
                <AnimatePresence>
                    {Object.entries(uploads).map(([filename, data]) => (
                        <motion.div
                            key={filename}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className="glass-panel p-4 flex items-center gap-4"
                        >
                            <div className="p-2 bg-white/10 rounded-lg">
                                {data.status === 'uploading' || data.status === 'processing' ? (
                                    <Loader2 className="w-6 h-6 animate-spin text-neon-pink" />
                                ) : data.status === 'done' ? (
                                    <CheckCircle className="w-6 h-6 text-neon-green" />
                                ) : (
                                    <AlertCircle className="w-6 h-6 text-red-500" />
                                )}
                            </div>

                            <div className="flex-1">
                                <h4 className="font-mono font-bold">{filename}</h4>
                                <div className="flex flex-wrap gap-2 mt-1">
                                    {data.steps.slice(-1).map((step, i) => (
                                        <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-neon-blue/20 text-neon-blue font-mono">
                                            {step}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Processing Ring / Progress Bar logic preserved */}
                            {data.status === 'uploading' && (
                                <div className="w-24 h-1 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-neon-green transition-all duration-300"
                                        style={{ width: `${data.progress}%` }}
                                    />
                                </div>
                            )}

                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* PyRx-Style Project Library */}
            {library && (library.receptors?.length > 0 || library.ligands?.length > 0) && (
                <div className="mt-6 pt-6 border-t border-white/10">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Project Library</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Receptors */}
                        {library.receptors?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="text-xs font-mono text-neon-blue mb-2">Macromolecules</h4>
                                {library.receptors.map(file => (
                                    <div
                                        key={file}
                                        onClick={() => onUploadComplete(`SimDock_Projects/${projectName}/receptors/${file}`)}
                                        className="p-3 bg-white/5 hover:bg-white/10 rounded cursor-pointer border border-transparent hover:border-neon-blue/30 transition-all flex items-center gap-2 group"
                                    >
                                        <FileIcon className="w-4 h-4 text-neon-blue group-hover:text-white" />
                                        <span className="text-sm font-mono truncate">{file}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                        {/* Ligands */}
                        {library.ligands?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="text-xs font-mono text-neon-pink mb-2">Ligands</h4>
                                {library.ligands.map(file => (
                                    <div
                                        key={file}
                                        onClick={() => onUploadComplete(`SimDock_Projects/${projectName}/ligands/${file}`)}
                                        className="p-3 bg-white/5 hover:bg-white/10 rounded cursor-pointer border border-transparent hover:border-neon-pink/30 transition-all flex items-center gap-2 group"
                                    >
                                        <FileIcon className="w-4 h-4 text-neon-pink group-hover:text-white" />
                                        <span className="text-sm font-mono truncate">{file}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileDrop;
