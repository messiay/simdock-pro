export interface IVinaParams {
    receptor?: string;
    ligand?: string;
    center_x: number;
    center_y: number;
    center_z: number;
    size_x: number;
    size_y: number;
    size_z: number;
    local_only?: boolean;
    score_only?: boolean;
    randomize_only?: boolean;
    cpu?: number;
    exhaustiveness?: number;
    seed?: number;
    num_modes?: number;
    energy_range?: number;
    weight_gauss1?: number;
    weight_gauss2?: number;
    weight_repulsion?: number;
    weight_hydrophobic?: number;
    weight_hydrogen?: number;
    weight_rot?: number;
}

export interface WebinaCallbacks {
    onDone: (outTxt: string, stdOut: string, stdErr: string) => void;
    onError: (error: any) => void;
    onStdout?: (text: string) => void;
    onStderr?: (text: string) => void;
}
