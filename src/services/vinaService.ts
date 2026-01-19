
import type { DockingParams, DockingResult } from '../types';
import { apiService } from './apiService';
import { useDockingStore } from '../store/dockingStore';

/**
 * VinaService - Replaced with Backend API Integration
 * 
 * Previously: WASM (Aioli/Webina)
 * Now: Python Backend (API) via apiService
 */
class VinaService {

    /**
     * Run molecular docking via Backend API
     */
    async runDocking(
        receptorPdbqt: string,
        ligandPdbqt: string,
        params: DockingParams,
        onProgress?: (message: string, progress: number) => void
    ): Promise<DockingResult> {

        const store = useDockingStore.getState();

        // 1. Create a logical project/session for this run
        const projectName = `WebSession_${Date.now()}`;
        store.addConsoleOutput(`[API] Creating session: ${projectName}...`);

        try {
            await apiService.createProject(projectName);
        } catch (e) {
            // Project might exist (unlikely with timestamp), or just continue
            console.warn("Project creation check:", e);
        }

        // 2. Upload Files
        store.addConsoleOutput(`[API] Uploading input files...`);
        onProgress?.("Uploading files to server...", 10);

        // Convert strings to File objects
        const receptorFile = new File([receptorPdbqt], "receptor.pdbqt", { type: "text/plain" });
        const ligandFile = new File([ligandPdbqt], "ligand.pdbqt", { type: "text/plain" });

        await apiService.uploadFile(projectName, receptorFile, 'receptor');
        await apiService.uploadFile(projectName, ligandFile, 'ligand');

        // 3. Submit Job
        store.addConsoleOutput(`[API] Submitting docking job (Vina)...`);
        onProgress?.("Submitting job to backend...", 20);

        const job = await apiService.submitJob(projectName, {
            engine: 'vina', // Hardcoded as per restriction
            receptor_file: 'receptor.pdbqt',
            ligand_file: 'ligand.pdbqt',
            config: {
                center_x: params.centerX,
                center_y: params.centerY,
                center_z: params.centerZ,
                size_x: params.sizeX,
                size_y: params.sizeY,
                size_z: params.sizeZ
            },
            exhaustiveness: params.exhaustiveness
        });

        store.addConsoleOutput(`[API] Job started: ${job.job_id}`);

        // 4. Poll for Completion
        let status = 'pending';
        let resultData = null;

        while (status === 'pending' || status === 'running') {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Poll every 1s
            const jobStatus = await apiService.getJobStatus(job.job_id);
            status = jobStatus.status;

            if (status === 'running') {
                onProgress?.("Docking in progress on server...", 50);
            }

            if (status === 'completed') {
                resultData = jobStatus.result;
                break;
            }
            if (status === 'failed') {
                throw new Error(jobStatus.error || "Docking failed on server");
            }
        }

        // 5. Download Result
        store.addConsoleOutput(`[API] Job completed! Fetching results...`);
        onProgress?.("Downloading results...", 90);

        if (!resultData?.output_file) {
            throw new Error("No output file in result");
        }

        const downloadUrl = apiService.getDownloadUrl(resultData.output_file);
        const resp = await fetch(downloadUrl);
        if (!resp.ok) throw new Error("Failed to download output PDBQT");

        const outputPdbqt = await resp.text();

        // 6. Map to DockingResult
        const poses = (resultData.scores || []).map((score: any) => ({
            mode: score.Mode,
            affinity: score['Affinity (kcal/mol)'],
            rmsdLB: score['RMSD L.B.'],
            rmsdUB: score['RMSD U.B.'],
            pdbqt: '' // Populated on demand
        }));

        store.addConsoleOutput(`[API] Received ${poses.length} poses.`);

        return {
            poses,
            rawOutput: outputPdbqt,
            logOutput: 'API docking complete'
        };
    }

    abort(): void {
        console.warn("[API] Abort not implemented for server-side jobs yet.");
    }
}

export const vinaService = new VinaService();
