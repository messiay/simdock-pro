import React, { useState, useEffect } from 'react';
import { Download, ChevronRight, Share, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';
import Viewer from './Viewer'; // Reuse Viewer for small previews?

const API_BASE = 'http://localhost:8000';

const ResultsGrid = ({ projectId, jobId, onBack, onPoseSelect }) => {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPose, setSelectedPose] = useState(null);

    useEffect(() => {
        const fetchResults = async () => {
            try {
                // Poll job status until complete
                // For simplicity in Day 1, assume job is already passed in completed state or we just fetch history
                // But better: Fetch job details
                const response = await axios.get(`${API_BASE}/docking/jobs/${jobId}`);
                if (response.data.status === 'completed') {
                    // Extract results from batch or single
                    let data = [];
                    if (response.data.batch_results) {
                        data = response.data.batch_results;
                    } else if (response.data.result) {
                        // Single job
                        data = [{
                            ligand: response.data.result.docking_run?.ligand || "Ligand",
                            score: response.data.result.scores ? response.data.result.scores[0]['Affinity (kcal/mol)'] : 'N/A',
                            success: response.data.result.success
                        }];
                        // If we have modes (Top 9), we should parse them. 
                        // But the current API structure might return 'scores' as a list.
                        // Let's assume for single docking we want to show the modes?
                        // The req says "Top 9 poses" for comparison.
                        // If api returns list of modes, we map them.
                        if (response.data.result.scores) {
                            data = response.data.result.scores.map((s, i) => ({
                                ligand: `Mode ${s['Mode']}`,
                                score: s['Affinity (kcal/mol)'],
                                success: true,
                                isPixel: true // Flag to treat as mode
                            }));
                        }
                    }
                    setResults(data);
                }
                setLoading(false);
            } catch (e) {
                console.error("Failed to fetch results", e);
                setLoading(false);
            }
        };

        if (jobId) fetchResults();
    }, [jobId]);

    // Color code scores
    const getScoreColor = (score) => {
        const s = parseFloat(score);
        if (s < -9.0) return "text-neon-green"; // Excellent
        if (s < -7.0) return "text-blue-400";   // Good
        if (s < -5.0) return "text-yellow-400"; // Moderate
        return "text-red-500"; // Poor
    };

    if (loading) return <div className="p-10 text-center animate-pulse text-neon-blue">RETRIEVING DATA...</div>;

    return (
        <div className="h-full flex flex-col">
            <h3 className="text-lg font-bold mb-4 flex justify-between items-center text-white">
                <span>DOCKING RESULTS</span>
                <span className="text-xs bg-neon-blue/20 text-neon-blue px-2 py-1 rounded">
                    JOB: {jobId.slice(0, 8)}
                </span>
            </h3>

            {/* The Top 9 Grid */}
            <div className="grid grid-cols-3 gap-2 flex-1 overflow-y-auto p-2">
                {results.slice(0, 9).map((res, idx) => (
                    <div
                        key={idx}
                        onClick={() => {
                            setSelectedPose(res);
                            if (onPoseSelect && res.pose_file) {
                                onPoseSelect(res.pose_file);
                            }
                        }}
                        className={`
                            relative bg-black/80 border rounded p-2 cursor-pointer transition-all hover:scale-105
                            ${selectedPose === res ? 'border-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.5)]' : 'border-white/10 hover:border-white/30'}
                        `}
                    >
                        <div className="aspect-square bg-deep-space/50 rounded flex items-center justify-center flex-col">
                            {/* Mini Viz Placeholder - Implementing vivid thumbnails is complex for Day 1 without specialized renderer */}
                            <div className="text-3xl font-mono font-bold opacity-30">{idx + 1}</div>
                            <div className={`font-mono text-sm font-bold mt-1 ${getScoreColor(res.score)}`}>
                                {res.score}
                            </div>
                        </div>
                        <div className="absolute top-1 right-1">
                            {res.success ? <CheckCircle className="w-3 h-3 text-neon-green" /> : <XCircle className="w-3 h-3 text-red-500" />}
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-4 pt-4 border-t border-white/10 flex justify-between">
                <button
                    onClick={onBack}
                    className="px-4 py-2 rounded bg-white/5 hover:bg-white/10 text-sm transition-colors"
                >
                    BACK
                </button>
                <button className="flex items-center gap-2 px-4 py-2 rounded bg-neon-green text-black font-bold text-sm hover:bg-green-400 transition-colors">
                    <Download className="w-4 h-4" /> EXPORT REPORT
                </button>
            </div>
        </div>
    );
};

export default ResultsGrid;
