import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const BackgroundGrid = () => {
    const mountRef = useRef(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // 1. Scene Setup
        const scene = new THREE.Scene();
        // Dark background for original theme
        scene.background = new THREE.Color(0x0f1014);
        scene.fog = new THREE.FogExp2(0x0f1014, 0.02);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 2, 12);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        mountRef.current.innerHTML = '';
        mountRef.current.appendChild(renderer.domElement);

        // --- GRID CONFIG (SCI-FI CYAN) ---
        const gridColor = 0x2FACB2; // Cyan to match SimDock original
        const gridOpacity = 0.4;    // Visible

        // Helper to create transparent grids
        const createGrid = (yPosition, opacity) => {
            const grid = new THREE.GridHelper(100, 50, gridColor, gridColor);
            grid.position.y = yPosition;

            const material = grid.material;
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

        // 3. Vertical Grid
        const gridBack = new THREE.GridHelper(100, 50, gridColor, gridColor);
        gridBack.rotation.x = Math.PI / 2;
        gridBack.position.z = -30;
        gridBack.material.transparent = true;
        gridBack.material.opacity = gridOpacity * 0.3;
        scene.add(gridBack);

        // Animation loop
        let time = 0;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            time += 0.002;
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

        return () => {
            window.removeEventListener('resize', handleResize);
            if (animationId) cancelAnimationFrame(animationId);
            if (mountRef.current) mountRef.current.innerHTML = '';
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
                zIndex: -1, /* Behind everything */
                pointerEvents: 'none'
            }}
        />
    );
};

export default BackgroundGrid;
