import React, { useEffect, useRef, useState } from 'react';
import * as NGL from 'ngl';
import { Layers, Box, ZoomIn, Maximize } from 'lucide-react';

const Viewer = ({ filePath, config }) => {
    const stageRef = useRef(null);
    const containerRef = useRef(null);
    const shapeCompRef = useRef(null);
    const [style, setStyle] = useState('surface'); // cartoon, surface, ball+stick

    // Initialize NGL Stage
    useEffect(() => {
        if (!containerRef.current) return;
        if (!stageRef.current) {
            stageRef.current = new NGL.Stage(containerRef.current, {
                backgroundColor: '#1e293b', // Slate-900 ChimeraX-like background
                tooltip: true,
                ambientOcclusion: true, // ChimeraX-style shadows
                ambientIntensity: 0.4,
                lightIntensity: 0.8
            });
            window.addEventListener('resize', () => stageRef.current.handleResize());
        }
    }, []);

    // Load Structure
    useEffect(() => {
        if (!stageRef.current || !filePath) return;

        console.log("Loading path into NGL:", filePath);

        try {
            stageRef.current.removeAllComponents();
            shapeCompRef.current = null; // Clear reference as it's removed
        } catch (e) {
            console.warn("Cleanup error:", e);
        }

        stageRef.current.loadFile(filePath).then(o => {
            try {
                // ChimeraX Style Presets
                if (style === 'cartoon') {
                    o.addRepresentation("cartoon", { colorScheme: "chainindex", quality: "high" });
                    o.addRepresentation("ball+stick", { sele: "ligand", colorValue: "#00ffcc", radiusScale: 2 });
                } else if (style === 'surface') {
                    o.addRepresentation("surface", {
                        opacity: 0.8,
                        colorScheme: "chainindex",
                        surfaceType: "av",
                        smooth: 2,
                        probeRadius: 1.4,
                        quality: "medium" // Performance optimization
                    });
                    o.addRepresentation("ball+stick", { sele: "ligand", colorValue: "#ff00ff", radiusScale: 3 });
                } else {
                    o.addRepresentation("ball+stick", { colorScheme: "element", quality: "high" });
                }

                o.autoView();

                // Force redraw of gridbox if config exists
                // We fake a dependency update or just manually call logic? 
                // Better to let the gridbox effect handle it, but we need to signal it.
                // For now, let's just leave it (user might need to touch slider to show box again if it disappears)

            } catch (err) {
                console.error("Representation Error:", err);
            }
        }).catch(e => console.error("NGL Load Error:", e));

    }, [filePath, style]);

    // Draw Gridbox (Wireframe)
    useEffect(() => {
        if (!stageRef.current || !config) return;

        try {
            // Remove old shape safely
            if (shapeCompRef.current) {
                try {
                    stageRef.current.removeComponent(shapeCompRef.current);
                } catch (e) { /* ignore if already removed */ }
                shapeCompRef.current = null;
            }

            const { center, size } = config;

            // Validate that center and size exist
            if (!center || !size) return;

            // NGL Shape for Gridbox
            const shape = new NGL.Shape("gridbox");

            // Calculate corners
            const x = parseFloat(center.x);
            const y = parseFloat(center.y);
            const z = parseFloat(center.z);
            const dx = parseFloat(size.x) / 2;
            const dy = parseFloat(size.y) / 2;
            const dz = parseFloat(size.z) / 2;

            // Define 8 corners
            const c1 = [x - dx, y - dy, z - dz]; const c2 = [x + dx, y - dy, z - dz];
            const c3 = [x - dx, y + dy, z - dz]; const c4 = [x + dx, y + dy, z - dz];
            const c5 = [x - dx, y - dy, z + dz]; const c6 = [x + dx, y - dy, z + dz];
            const c7 = [x - dx, y + dy, z + dz]; const c8 = [x + dx, y + dy, z + dz];

            const color = [1, 0, 1]; // Magenta/Cyan-ish wireframe

            // Draw 12 edges
            shape.addLine(c1, c2, color); shape.addLine(c3, c4, color);
            shape.addLine(c1, c3, color); shape.addLine(c2, c4, color);

            shape.addLine(c5, c6, color); shape.addLine(c7, c8, color);
            shape.addLine(c5, c7, color); shape.addLine(c6, c8, color);

            shape.addLine(c1, c5, color); shape.addLine(c2, c6, color);
            shape.addLine(c3, c7, color); shape.addLine(c4, c8, color);

            const comp = stageRef.current.addComponentFromObject(shape);
            if (comp) {
                comp.addRepresentation("buffer", { opacity: 1.0, depthTest: false, linewidth: 5 });
                shapeCompRef.current = comp;
            } else {
                console.warn("Failed to add gridbox component");
            }

        } catch (error) {
            console.error("Gridbox Draw Error:", error);
        }

    }, [config]);

    return (
        <div className="relative w-full h-full min-h-[500px] bg-slate-900 overflow-hidden group rounded-lg">
            <div ref={containerRef} className="w-full h-full" />

            {/* ChimeraX-style Floating Toolbar */}
            <div className="absolute top-4 right-4 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="bg-slate-800/90 p-2 rounded-lg border border-slate-600 backdrop-blur shadow-xl">
                    <div className="flex flex-col gap-2">
                        <button
                            onClick={() => setStyle({ cartoon: 'surface', surface: 'stick', stick: 'cartoon' }[style] || 'cartoon')}
                            className="p-2 hover:bg-slate-700 rounded text-cyan-400"
                            title="Toggle Style"
                        >
                            <Layers className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => stageRef.current?.autoView()}
                            className="p-2 hover:bg-slate-700 rounded text-cyan-400"
                            title="Recenter"
                        >
                            <Maximize className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Gridbox Status Label */}
            {config && (
                <div className="absolute bottom-4 left-4 bg-slate-800/80 px-3 py-1.5 rounded border border-cyan-500/30 text-xs font-mono text-cyan-400 backdrop-blur">
                    BOX: [{config.center.x}, {config.center.y}, {config.center.z}]
                </div>
            )}
        </div>
    );
};

export default Viewer;
