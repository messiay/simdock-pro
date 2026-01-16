import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const BackgroundGrid = () => {
    const mountRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // 1. Scene Setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000); // Pure Black
        scene.fog = new THREE.FogExp2(0x000000, 0.03); // Deep fog for infinite look

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 2, 12); // Slightly elevated

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Clear old canvas if exists
        mountRef.current.innerHTML = '';
        mountRef.current.appendChild(renderer.domElement);

        // --- GRID CONFIG (MONOCHROME - High Visibility) ---
        const gridColor = 0xffffff; // Pure White
        const gridOpacity = 0.3;    // Increased from 0.15 for visibility

        // Helper to create transparent grids
        const createGrid = (yPosition: number, opacity: number) => {
            const grid = new THREE.GridHelper(100, 50, gridColor, gridColor);
            grid.position.y = yPosition;

            const material = grid.material as THREE.LineBasicMaterial;
            material.transparent = true;
            material.opacity = opacity;

            return grid;
        };

        // 1. Floor Grid
        const gridBottom = createGrid(-4, gridOpacity);
        scene.add(gridBottom);

        // 2. Ceiling Grid (Mirror)
        const gridTop = createGrid(4, gridOpacity * 0.5);
        scene.add(gridTop);

        // 3. Vertical Grid (Horizon)
        const gridBack = new THREE.GridHelper(100, 50, gridColor, gridColor);
        gridBack.rotation.x = Math.PI / 2;
        gridBack.position.z = -30;
        (gridBack.material as THREE.LineBasicMaterial).transparent = true;
        (gridBack.material as THREE.LineBasicMaterial).opacity = gridOpacity * 0.3;
        scene.add(gridBack);

        // Animation variables
        let time = 0;

        // Animation Loop
        const animate = () => {
            requestAnimationFrame(animate);

            time += 0.002;

            // Subtle movement
            gridBottom.position.z = (time * 2) % 2;
            gridTop.position.z = (time * 2) % 2;

            renderer.render(scene, camera);
        };
        animate();

        // Handle Resize
        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            if (mountRef.current) {
                mountRef.current.innerHTML = '';
            }
            renderer.dispose();
        };
    }, []);

    return (
        <div
            ref={mountRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                zIndex: 0, /* Set to 0 to be just behind UI (UI is usually z-10+) */
                pointerEvents: 'none' /* Passthrough clicks */
            }}
        />
    );
};

export default BackgroundGrid;
