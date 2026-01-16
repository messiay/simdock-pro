import type { IVinaParams, WebinaCallbacks } from "./types";

const WASM_BASE = "/Webina/";

export class WebinaService {
    private static instance: WebinaService;

    private constructor() { }

    public static getInstance(): WebinaService {
        if (!WebinaService.instance) {
            WebinaService.instance = new WebinaService();
        }
        return WebinaService.instance;
    }

    public async start(
        vinaParams: IVinaParams,
        receptorPDBQTTxt: string,
        ligandPDBQTTxt: string,
        callbacks: WebinaCallbacks
    ): Promise<void> {
        let initializedObj: any = undefined;
        let stdOut = "";
        let stdErr = "";

        console.log("WebinaService: start() called");

        try {
            // Load vina.js as a module from public folder
            console.log(`WebinaService: Importing ${WASM_BASE}vina.js...`);

            // @ts-ignore
            /* @vite-ignore */
            const mod = await import(`${WASM_BASE}vina.js`);
            console.log("WebinaService: Module imported", mod);

            const moduleFactory = mod.default;
            if (!moduleFactory) {
                console.error("WebinaService: WEBINA_MODULE default export not found in imported module.");
                throw new Error("WEBINA_MODULE default export not found.");
            }

            console.log("WebinaService: Calling module factory...");
            const webinaMod = await moduleFactory({
                logReadFiles: true,
                noInitialRun: true,
                locateFile: (path: string) => {
                    console.log(`WebinaService: locateFile(${path}) -> ${WASM_BASE}${path}`);
                    return `${WASM_BASE}${path}`;
                },
                preRun: [
                    (This: any) => {
                        console.log("WebinaService: preRun callback");
                        try {
                            console.log("WebinaService: Writing receptor.pdbqt (" + receptorPDBQTTxt.length + " bytes)");
                            This.FS.writeFile("/receptor.pdbqt", receptorPDBQTTxt);
                            console.log("WebinaService: Writing ligand.pdbqt (" + ligandPDBQTTxt.length + " bytes)");
                            This.FS.writeFile("/ligand.pdbqt", ligandPDBQTTxt);
                            initializedObj = This;
                        } catch (e) {
                            console.error("WebinaService: Error writing files to Vina FS", e);
                            if (callbacks.onError) callbacks.onError(e);
                        }
                    },
                ],
                print: (text: string) => {
                    console.log("Webina STDOUT:", text);
                    stdOut += text + "\n";
                    if (callbacks.onStdout) callbacks.onStdout(text);
                },
                printErr: (text: string) => {
                    console.warn("Webina STDERR:", text);
                    stdErr += text + "\n";
                    if (callbacks.onStderr) callbacks.onStderr(text);
                },
                onExit: (_code: number) => {
                    console.log("Webina exited with code", _code);
                    if (initializedObj) {
                        try {
                            console.log("WebinaService: Reading output file...");
                            const outTxt = initializedObj.FS.readFile(
                                "/ligand_out.pdbqt",
                                { encoding: "utf8" }
                            );
                            console.log("WebinaService: Output file read (" + outTxt.length + " bytes)");
                            callbacks.onDone(outTxt, stdOut, stdErr);
                        } catch (e) {
                            console.warn("WebinaService: Could not read output file", e);
                            callbacks.onDone("", stdOut, stdErr);
                        }
                    } else {
                        console.warn("WebinaService: initializedObj is undefined on exit");
                        callbacks.onDone("", stdOut, stdErr);
                    }
                },
                onError: (e: any) => {
                    console.error("Webina Internal Error:", e);
                    if (callbacks.onError) callbacks.onError(e);
                }
            });

            console.log("WebinaService: Webina Module initialized", webinaMod);

            // Wait for ready
            if (webinaMod.ready) {
                console.log("WebinaService: Waiting for ready promise...");
                await webinaMod.ready;
                console.log("WebinaService: Ready promise resolved");
            }

            // Args
            const cmdLineParams: string[] = [];
            Object.keys(vinaParams).forEach((key) => {
                const val = (vinaParams as any)[key];
                if (val === false || val === undefined) return;
                if (val === true) {
                    cmdLineParams.push(`--${key}`);
                    return;
                }
                cmdLineParams.push(`--${key}`);
                cmdLineParams.push(val.toString());
            });

            cmdLineParams.push(
                "--receptor", "/receptor.pdbqt",
                "--ligand", "/ligand.pdbqt",
                "--out", "/ligand_out.pdbqt"
            );

            console.log("WebinaService: Calling main with args:", cmdLineParams);
            webinaMod.callMain(cmdLineParams);

        } catch (e) {
            console.error("WebinaService: Critical error in start():", e);
            if (callbacks.onError) callbacks.onError(e);
        }
    }
}
