import { config } from '../config';
import type { DockingParams, DockingResult } from '../core/types';

export interface JobStatus {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    error?: string;
    result?: {
        output_file: string;
        scores: Array<{
            Mode: number;
            'Affinity (kcal/mol)': number;
            'RMSD L.B.': number;
            'RMSD U.B.': number;
        }>;
    };
}

export const apiService = {
    async createProject(name: string) {
        const response = await fetch(`${config.API_BASE_URL}/projects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) throw new Error('Failed to create project');
        return response.json();
    },

    async uploadFile(projectName: string, file: File, category: 'receptor' | 'ligand') {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${config.API_BASE_URL}/projects/${projectName}/upload?category=${category}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`Failed to upload ${category}`);
        return response.json();
    },

    async submitJob(projectName: string, configData: {
        engine: 'vina' | 'smina'; // Restricted as requested
        receptor_file: string;
        ligand_file: string;
        config: {
            center_x: number; center_y: number; center_z: number;
            size_x: number; size_y: number; size_z: number;
        };
        exhaustiveness: number;
    }) {
        const response = await fetch(`${config.API_BASE_URL}/docking/${projectName}/dock`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Job submission failed');
        }
        return response.json();
    },

    async getJobStatus(jobId: string): Promise<JobStatus> {
        const response = await fetch(`${config.API_BASE_URL}/docking/jobs/${jobId}`);
        if (!response.ok) throw new Error('Failed to check job status');
        return response.json();
    },

    getDownloadUrl(relativePath: string) {
        // Cleaning the path to ensure it maps correctly to static mount
        // Backend mounts 'SimDock_Projects' at '/files'
        // relativePath usually comes as full absolute path or relative from project root
        // We need to extract the project-relative part. 
        // A simple heuristic if the path is absolute: find 'SimDock_Projects' and take substring

        // However, backend usually returns absolute path.
        // Let's assume standard structure: .../SimDock_Projects/ProjectName/results/file.pdbqt

        const key = 'SimDock_Projects';
        if (relativePath.includes(key)) {
            const part = relativePath.split(key)[1];
            // Normalize slashes
            const cleanPart = part.replace(/\\/g, '/');
            return `${config.API_BASE_URL}/files${cleanPart}`;
        }
        return relativePath; // Fallback
    }
};
