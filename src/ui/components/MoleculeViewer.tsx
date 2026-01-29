import { useEffect, useRef, useState, useCallback } from 'react';
import { useDockingStore } from '../../store/dockingStore';
import { Dna } from 'lucide-react';
import '../styles/MoleculeViewer.css';

// Declare 3Dmol on window
declare global {
    interface Window {
        $3Dmol: any;
    }
}

export function MoleculeViewer() {
    // Use a separate ref for the 3Dmol container that React won't manage
    const containerRef = useRef<HTMLDivElement>(null);
    const viewerInstanceRef = useRef<any>(null);
    const scriptLoadedRef = useRef(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isReady, setIsReady] = useState(false);

    // Consume global state including VIEW CONTROL
    const {
        receptorFile,
        ligandFile,
        params,
        result,
        selectedPose,
        viewMode,
        resetViewTrigger,
        theme,
        showBox,
    } = useDockingStore();

    // Initialize the viewer
    const initializeViewer = useCallback(() => {
        if (!containerRef.current || !window.$3Dmol || viewerInstanceRef.current) return;

        try {
            // Transparent background for Grid visibility
            // 0x000000 with 0 alpha if supported, or just rely on CSS
            // 3Dmol.js: setBackgroundColor(color, alpha)

            const viewer = window.$3Dmol.createViewer(containerRef.current, {
                backgroundColor: 'black', // Default, but we will override with setBackgroundColor
                antialias: true,
                alpha: true // Enable alpha channel in WebGL
            });

            // Immediately set transparent
            viewer.setBackgroundColor(0x000000, 0);

            viewerInstanceRef.current = viewer;
            viewer.render();
            setIsReady(true);
        } catch (error) {
            console.error('Failed to initialize 3Dmol viewer:', error);
        }
    }, [theme]);

    // Load 3Dmol.js script only once
    useEffect(() => {
        if (window.$3Dmol) {
            setIsLoading(false);
            scriptLoadedRef.current = true;
            return;
        }

        const existingScript = document.querySelector('script[src="/3Dmol-min.js"]');
        if (existingScript) {
            const checkLoaded = setInterval(() => {
                if (window.$3Dmol) {
                    setIsLoading(false);
                    scriptLoadedRef.current = true;
                    clearInterval(checkLoaded);
                }
            }, 100);
            return () => clearInterval(checkLoaded);
        }

        const script = document.createElement('script');
        script.src = '/3Dmol-min.js';
        script.async = true;
        script.onload = () => {
            setIsLoading(false);
            scriptLoadedRef.current = true;
        };
        script.onerror = () => {
            console.error('Failed to load 3Dmol.js');
            setIsLoading(false);
        };
        document.head.appendChild(script);
        return () => { };
    }, []);

    // Initialize viewer when script is loaded
    useEffect(() => {
        if (!isLoading && containerRef.current && !viewerInstanceRef.current) {
            initializeViewer();
        }
    }, [isLoading, initializeViewer]);

    // Handle Theme Change
    useEffect(() => {
        if (viewerInstanceRef.current) {
            // Keep transparent, or maybe just slight tint?
            // For now, keep fully transparent to show the grid.
            viewerInstanceRef.current.setBackgroundColor(0x000000, 0);
            viewerInstanceRef.current.render();
        }
    }, [theme]);

    // Handle Reset View Trigger
    useEffect(() => {
        if (resetViewTrigger > 0 && viewerInstanceRef.current) {
            viewerInstanceRef.current.zoomTo();
            viewerInstanceRef.current.render();
        }
    }, [resetViewTrigger]);

    // Cleanup viewer on unmount
    useEffect(() => {
        return () => {
            if (viewerInstanceRef.current) {
                try {
                    viewerInstanceRef.current.clear();
                } catch (e) { }
                viewerInstanceRef.current = null;
            }
        };
    }, []);

    // EFFECT 1: UPDATE MODELS (Heavy Operation - Only run when files change)
    useEffect(() => {
        if (!isReady || !viewerInstanceRef.current) return;

        const viewer = viewerInstanceRef.current;
        // console.time('[MoleculeViewer] Update Models');

        try {
            // Check if we have results and a valid pose
            const hasResult = !!(result && result.poses && result.poses[selectedPose]);
            const ligandContent = hasResult
                ? result!.poses[selectedPose].pdbqt
                : ligandFile?.content;

            viewer.removeAllModels();
            viewer.removeAllSurfaces();

            // Add receptor
            let receptorModel: any = null;
            if (receptorFile?.content) {
                // If it's explicitly sdf or ends in .sdf, use sdf. Vina needs PDBQT but viewer can show others.
                let format = receptorFile.format || 'pdb';
                if (format === 'pdbqt') format = 'pdb'; // 3Dmol doesn't support pdbqt natively

                receptorModel = viewer.addModel(receptorFile.content, format);

                // Safe check: Ensure model exists AND has atoms
                if (receptorModel && typeof receptorModel.selectedAtoms === 'function' && receptorModel.selectedAtoms().length > 0) {
                    // atomCount available via receptorModel.selectedAtoms().length if needed

                    // Apply style based on view mode
                    try {
                        if (viewMode === 'cartoon') {
                            viewer.setStyle({ model: receptorModel }, { cartoon: { color: 'spectrum' } });
                        } else if (viewMode === 'sticks') {
                            viewer.setStyle({ model: receptorModel }, { stick: { colorscheme: 'Jmol' } });
                        } else if (viewMode === 'surface') {
                            // Surface Mode: Ghost cartoon + Teal VDW Surface
                            viewer.setStyle({ model: receptorModel }, { cartoon: { color: 'spectrum', opacity: 0.3 } });

                            // Force surface generation with a slight delay if needed, but direct call is usually better
                            // Use 'all' selection for safety
                            try {
                                const surfaceColor = theme === 'light' ? '#38BDF8' : '#2FACB2';
                                viewer.addSurface(window.$3Dmol.SurfaceType.VDW, {
                                    opacity: 0.85,
                                    color: surfaceColor,
                                    quality: 0 // set to 0 or 1. 0 might be safer for basic surface? Using 1 involves more compute.
                                }, { model: receptorModel });
                            } catch (surfaceErr) {
                                console.warn('[MoleculeViewer] Surface generation failed', surfaceErr);
                            }
                        }
                    } catch (styleErr) {
                        console.error('[MoleculeViewer] Error applying style to receptor:', styleErr);
                    }
                }
            }

            // ADD LIGAND
            if (ligandContent && ligandContent.trim().length > 0) {
                // Smart format detection
                let format = 'pdb'; // Default
                const contentLower = ligandContent.toLowerCase();
                const isSDF = contentLower.includes('m  end') ||
                    contentLower.includes('$$$$') ||
                    contentLower.includes('v2000') ||
                    contentLower.includes('v3000');
                const hasPdbAtoms = ligandContent.includes('ATOM') || ligandContent.includes('HETATM');

                if (isSDF && !hasPdbAtoms) format = 'sdf';
                else format = 'pdb'; // Force PDB for PDBQT content as 3Dmol handles it better

                const ligandModel = viewer.addModel(ligandContent, format);

                if (ligandModel && typeof ligandModel.selectedAtoms === 'function' && ligandModel.selectedAtoms().length > 0) {
                    try {
                        viewer.setStyle({ model: ligandModel }, {
                            stick: { colorscheme: 'greenCarbon', radius: 0.3 },
                            sphere: { colorscheme: 'greenCarbon', scale: 0.3 }
                        });
                    } catch (styleErr) { console.error(styleErr); }
                }
            }

            viewer.zoomTo();
            viewer.render();
            // console.timeEnd('[MoleculeViewer] Update Models');

        } catch (error) {
            console.error('Error updating viewer models:', error);
        }
    }, [receptorFile, ligandFile, viewMode, isReady, result, selectedPose]); // Removed params/showBox from dependency

    // EFFECT 2: UPDATE BOX/SHAPES (Light Operation - Runs when box params change)
    useEffect(() => {
        if (!isReady || !viewerInstanceRef.current) return;
        const viewer = viewerInstanceRef.current;

        try {
            viewer.removeAllShapes(); // Only clears box/cylinders

            // Add docking box visualization
            if (showBox && params.sizeX > 0 && params.sizeY > 0 && params.sizeZ > 0) {
                const { centerX, centerY, centerZ, sizeX, sizeY, sizeZ } = params;
                const halfX = sizeX / 2, halfY = sizeY / 2, halfZ = sizeZ / 2;

                const corners = [
                    [centerX - halfX, centerY - halfY, centerZ - halfZ],
                    [centerX + halfX, centerY - halfY, centerZ - halfZ],
                    [centerX + halfX, centerY + halfY, centerZ - halfZ],
                    [centerX - halfX, centerY + halfY, centerZ - halfZ],
                    [centerX - halfX, centerY - halfY, centerZ + halfZ],
                    [centerX + halfX, centerY - halfY, centerZ + halfZ],
                    [centerX + halfX, centerY + halfY, centerZ + halfZ],
                    [centerX - halfX, centerY + halfY, centerZ + halfZ],
                ];

                const edges = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];

                for (const [i, j] of edges) {
                    viewer.addCylinder({
                        start: { x: corners[i][0], y: corners[i][1], z: corners[i][2] },
                        end: { x: corners[j][0], y: corners[j][1], z: corners[j][2] },
                        radius: 0.05,
                        color: '#00d9ff',
                        fromCap: true,
                        toCap: true,
                    });
                }

                viewer.addBox({
                    center: { x: centerX, y: centerY, z: centerZ },
                    dimensions: { w: sizeX, h: sizeY, d: sizeZ },
                    color: theme === 'dark' ? '#00ffff' : '#00d9ff', // Brighter cyan in dark mode
                    opacity: theme === 'dark' ? 0.6 : 0.45           // Higher opacity in dark mode
                });
            }
            viewer.render();

        } catch (error) {
            console.error('Error updating viewer shapes:', error);
        }
    }, [params, showBox, isReady]);

    return (
        <div className="molecule-viewer">
            <div className="viewer-container-wrapper">
                {/* 3Dmol container - no React children inside */}
                <div
                    className="viewer-canvas"
                    ref={containerRef}
                    style={{
                        width: '100%',
                        height: '100%',
                        position: 'absolute',
                        left: 0,
                        backgroundColor: 'transparent'
                    }}
                />

                {isLoading && (
                    <div className="viewer-overlay">
                        <div className="loading-spinner" />
                        <p>Loading 3D Viewer...</p>
                    </div>
                )}

                {isReady && !receptorFile && !ligandFile && (
                    <div className={`viewer-overlay viewer-placeholder ${theme}`}>
                        <span className="placeholder-icon"><Dna size={80} strokeWidth={1} /></span>
                        <p>SimDock 3D Space</p>
                    </div>
                )}
            </div>
        </div>
    );
}
