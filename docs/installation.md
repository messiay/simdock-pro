# Installation Guide

## Prerequisites

- **Node.js** v18 or higher ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- A modern web browser (Chrome, Firefox, Edge)

## Quick Install

```bash
# Clone the repository
git clone https://github.com/messiay/simdock-new.git
cd simdock-new

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

## Production Build

```bash
# Create optimized production build
npm run build

# Preview the production build
npm run preview
```

The production files will be in the `dist/` folder.

## Server Requirements

SimDock uses WebAssembly with SharedArrayBuffer, which requires specific HTTP headers:

```
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
```

The development server (`npm run dev`) and the included `server.js` already set these headers.

## Troubleshooting

### WASM Won't Load
- Ensure you're using a modern browser (Chrome 89+, Firefox 79+, Edge 89+)
- Check that the server is sending the correct COOP/COEP headers
- Try clearing browser cache and reloading

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Use a different port
npm run dev -- --port 3000
```
