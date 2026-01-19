# SimDock Pro 🧬

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.1-green.svg)](CHANGELOG.md)
[![Node](https://img.shields.io/badge/node-18+-brightgreen.svg)](https://nodejs.org/)

**Browser-based molecular docking powered by WebAssembly**

Run AutoDock Vina directly in your browser—no installation, no server, complete privacy.

---

## ✨ Features

- 🔬 **Client-Side Docking** — AutoDock Vina runs entirely in your browser via WebAssembly
- 🔒 **Privacy First** — All calculations happen locally, no data leaves your device
- 📦 **Zero Install** — Just open the URL in any modern browser
- 🎨 **Beautiful UI** — Dark/Light themes with glassmorphism design
- 📚 **Project Library** — Save and manage docking projects with IndexedDB

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/messiay/simdock-new.git
cd simdock-new

# 2. Install
npm install

# 3. Run
npm run dev
```

Open `http://localhost:5173` in your browser.

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Installation](docs/installation.md) | Setup & prerequisites |
| [Usage](docs/usage.md) | Workflow guide |
| [Configuration](docs/configuration.md) | Advanced settings |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19 + TypeScript + Vite |
| **State** | Zustand |
| **Docking** | AutoDock Vina (WASM) |
| **Chemistry** | RDKit.js, OpenBabel.js |
| **Visualization** | NGL Viewer |
| **Storage** | IndexedDB |

## 📁 Project Structure

```
simdock-new/
├── src/           # Application source code
│   ├── components/  # React UI components
│   ├── services/    # WASM integration
│   └── store/       # State management
├── public/        # Static assets & WASM binaries
├── docs/          # Documentation
└── dist/          # Production build
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## ⚠️ Known Limitations

- **Single-threaded** — Browser security limits WASM to one CPU core
- **Large molecules** — Complex ligands may take longer to dock

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Powered by AutoDock Vina, Emscripten, and React*
