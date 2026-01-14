import React, { useState, useEffect } from 'react';
import { Settings, Crosshair, Box, Cpu, Zap, Target } from 'lucide-react';
import { motion } from 'framer-motion';

const ConfigPanel = ({ config, onConfigChange, onAutoPocket }) => {
    const [localConfig, setLocalConfig] = useState(config);

    useEffect(() => {
        setLocalConfig(config);
    }, [config]);

    const updateConfig = (key, value) => {
        const newConfig = { ...localConfig, [key]: value };
        setLocalConfig(newConfig);
        onConfigChange(newConfig);
    };

    const updateCenter = (axis, value) => {
        updateConfig('center', { ...localConfig.center, [axis]: parseFloat(value) });
    };

    const updateSize = (axis, value) => {
        updateConfig('size', { ...localConfig.size, [axis]: parseFloat(value) });
    };

    return (
        <div className="space-y-4">
            {/* Engine Selection */}
            <div className="bg-slate-900/60 border border-cyan-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    <h3 className="font-semibold text-sm uppercase tracking-wide text-slate-300">Engine</h3>
                </div>
                <select
                    value={localConfig.engine || 'vina'}
                    onChange={(e) => updateConfig('engine', e.target.value)}
                    className="w-full bg-slate-950 border border-cyan-500/30 rounded px-3 py-2.5 text-slate-200 text-sm focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 font-medium"
                >
                    <option value="vina">AutoDock Vina</option>
                    <option value="gnina">GNINA (CNN Scoring)</option>
                </select>
                <div className="mt-2 text-xs text-slate-500 font-medium">
                    Student Tier: CPU engines only
                </div>
            </div>

            {/* Gridbox Controls */}
            <div className="bg-slate-900/60 border border-cyan-500/20 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Box className="w-4 h-4 text-teal-400" />
                        <h3 className="font-semibold text-sm uppercase tracking-wide text-slate-300">Search Space</h3>
                    </div>
                    <button
                        onClick={onAutoPocket}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 rounded text-xs transition-colors text-teal-400 font-medium"
                    >
                        <Target className="w-3 h-3" />
                        Auto-Detect
                    </button>
                </div>

                {/* Center Controls */}
                <div className="space-y-2.5 mb-4">
                    <div className="text-xs text-cyan-400/70 font-medium uppercase tracking-wider mb-2">Center (Å)</div>
                    {['x', 'y', 'z'].map(axis => (
                        <div key={axis} className="flex items-center gap-2">
                            <span className="text-xs font-mono text-teal-400 w-4 uppercase font-semibold">{axis}</span>
                            <input
                                type="range"
                                min="-50"
                                max="50"
                                step="0.5"
                                value={localConfig.center[axis]}
                                onChange={(e) => updateCenter(axis, e.target.value)}
                                className="flex-1 h-1.5 bg-slate-800 rounded appearance-none cursor-pointer slider"
                            />
                            <input
                                type="number"
                                value={localConfig.center[axis]}
                                onChange={(e) => updateCenter(axis, e.target.value)}
                                className="w-16 bg-slate-950 border border-cyan-500/30 rounded px-2 py-1.5 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
                            />
                        </div>
                    ))}
                </div>

                {/* Size Controls */}
                <div className="space-y-2.5">
                    <div className="text-xs text-cyan-400/70 font-medium uppercase tracking-wider mb-2">Size (Å)</div>
                    {['x', 'y', 'z'].map(axis => (
                        <div key={axis} className="flex items-center gap-2">
                            <span className="text-xs font-mono text-teal-400 w-4 uppercase font-semibold">{axis}</span>
                            <input
                                type="range"
                                min="5"
                                max="40"
                                step="1"
                                value={localConfig.size[axis]}
                                onChange={(e) => updateSize(axis, e.target.value)}
                                className="flex-1 h-1.5 bg-slate-800 rounded appearance-none cursor-pointer slider"
                            />
                            <input
                                type="number"
                                value={localConfig.size[axis]}
                                onChange={(e) => updateSize(axis, e.target.value)}
                                className="w-16 bg-slate-950 border border-cyan-500/30 rounded px-2 py-1.5 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Exhaustiveness */}
            <div className="bg-slate-900/60 border border-cyan-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-4 h-4 text-amber-400" />
                    <h3 className="font-semibold text-sm uppercase tracking-wide text-slate-300">Exhaustiveness</h3>
                </div>
                <div className="flex items-center gap-3">
                    <input
                        type="range"
                        min="1"
                        max="8"
                        value={localConfig.exhaustiveness || 8}
                        onChange={(e) => updateConfig('exhaustiveness', parseInt(e.target.value))}
                        className="flex-1 h-1.5 bg-slate-800 rounded appearance-none cursor-pointer slider"
                    />
                    <span className="text-2xl font-mono font-bold w-8 text-amber-400">
                        {localConfig.exhaustiveness || 8}
                    </span>
                </div>
                <div className="mt-2 text-xs text-slate-500 font-medium">
                    Student Max: 8 (Pro: 32)
                </div>
            </div>
        </div>
    );
};

export default ConfigPanel;
