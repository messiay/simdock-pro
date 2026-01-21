# SimDock Pro 🧬

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.1-green.svg)](CHANGELOG.md)
[![Node](https://img.shields.io/badge/node-18+-brightgreen.svg)](https://nodejs.org/)

**Cloud-Powered Molecular Docking Platform**

Professional molecular docking powered by FastAPI backend with AutoDock Vina integration.

---

## ✨ Features

- 🔬 **FastAPI Backend** — High-performance docking via cloud API with AutoDock Vina
- ⚡ **Scalable Architecture** — Cloud-based processing for reliable docking computations
- 📦 **Easy Integration** — RESTful API for seamless integration with your workflow
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
| **Backend** | FastAPI + Python |
| **Docking** | AutoDock Vina (API) |
| **Chemistry** | RDKit, OpenBabel |
| **Visualization** | NGL Viewer |
| **Storage** | IndexedDB |

## 📁 Project Structure

```
simdock-new/
├── src/           # Application source code
│   ├── components/  # React UI components
│   ├── services/    # API integration
│   └── store/       # State management
├── public/        # Static assets
├── docs/          # Documentation
└── dist/          # Production build
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Powered by AutoDock Vina, FastAPI, and React*
