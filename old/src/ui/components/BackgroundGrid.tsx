import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const BackgroundGrid = () => {
    const mountRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // 1. Scene Setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f1014); // Deep Dark Blue-Black (Original Theme Background)
        scene.fog = new THREE.FogExp2(0x0f1014, 0.02);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 2, 12);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        mountRef.current.innerHTML = '';
        mountRef.current.appendChild(renderer.domElement);

        // --- GRID CONFIG (SCI-FI CYAN) ---
        // Using Cyan to match the original "SimDock" aesthetic
        const gridColor = 0x2FACB2;
        const gridOpacity = 0.4;    // High opacity for visibility

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

        // 2. Ceiling Grid
        const gridTop = createGrid(4, gridOpacity * 0.5);
        scene.add(gridTop);

        // 3. Vertical Grid (Horizon)
        const gridBack = new THREE.GridHelper(100, 50, gridColor, gridColor);
        gridBack.rotation.x = Math.PI / 2;
        gridBack.position.z = -30;
        (gridBack.material as THREE.LineBasicMaterial).transparent = true;
        (gridBack.material as THREE.LineBasicMaterial).opacity = gridOpacity * 0.3;
        scene.add(gridBack);

        // Animation variable
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
                zIndex: 0, /* Background Layer */
                pointerEvents: 'none'
            }}
        />
    );
};

export default BackgroundGrid;
