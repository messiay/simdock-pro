# WASM Binaries - Canonical Source

This directory contains the canonical WASM (WebAssembly) binaries for SimDock Pro.

## Structure

```
wasm/
├── vina/           # AutoDock Vina WASM
│   ├── vina.wasm
│   ├── vina.js
│   └── vina.worker.js
├── openbabel/      # OpenBabel WASM
│   └── openbabel.wasm
├── rdkit/          # RDKit.js
│   └── RDKit_minimal.wasm
└── README.md
```

## Usage

These are the **source of truth** WASM files for the project. The web application (`new/webvina/public/`) has its own copies for serving, but this directory serves as the canonical reference.

## Licenses

| Module | Source | License |
|--------|--------|---------|
| AutoDock Vina WASM | webvina project | Apache 2.0 |
| RDKit.js | @rdkit/rdkit | BSD |
| OpenBabel WASM | openbabel-wasm | GPL |

---

*Reorganized as part of repository cleanup on January 16, 2026*
