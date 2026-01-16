import React, { useEffect, useRef } from 'react';
// @ts-ignore
import * as $3Dmol from '3dmol';

interface MoleculeViewerProps {
    receptor: string;
    ligand: string;
}

export const MoleculeViewer: React.FC<MoleculeViewerProps> = ({ receptor, ligand }) => {
    const viewerRef = useRef<HTMLDivElement>(null);
    const viewerInstance = useRef<any>(null);

    useEffect(() => {
        if (!viewerRef.current) return;

        // Initialize viewer
        if (!viewerInstance.current) {
            const config = { backgroundColor: '#1a1a1a' };
            viewerInstance.current = $3Dmol.createViewer(viewerRef.current, config);
        }

        const viewer = viewerInstance.current;
        viewer.clear();

        if (receptor) {
            viewer.addModel(receptor, "pdbqt");
            viewer.setStyle({ model: -1 }, { cartoon: { color: 'spectrum' } });
        }

        if (ligand) {
            viewer.addModel(ligand, "pdbqt");
            viewer.setStyle({ model: -1 }, { stick: { colorscheme: 'greenCarbon' } });
        }

        viewer.zoomTo();
        viewer.render();

    }, [receptor, ligand]);

    return (
        <div className="w-full h-96 bg-gray-800 rounded-lg overflow-hidden relative">
            <div ref={viewerRef} className="w-full h-full" />
        </div>
    );
};
