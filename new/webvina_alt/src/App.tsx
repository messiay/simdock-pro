import { useEffect } from 'react';
import { useDockingStore } from './store/dockingStore';
import { Sidebar } from './ui/components/Sidebar';
import { PrepPanel } from './ui/components/PrepPanel';
import { InputPanel } from './ui/components/InputPanel';
import { ExistingOutputPanel } from './ui/components/ExistingOutputPanel';
import { RunningPanel } from './ui/components/RunningPanel';
import { OutputPanel } from './ui/components/OutputPanel';
import { ProjectPanel } from './ui/components/ProjectPanel';
import { BatchPanel } from './ui/components/BatchPanel';
import { LandingPanel } from './ui/components/LandingPanel';
import { MoleculeViewer } from './ui/components/MoleculeViewer';
import { DraggablePanel } from './ui/components/DraggablePanel';
import { FloatingToolbar } from './ui/components/FloatingToolbar'; // Keep toolbar
import BackgroundGrid from './ui/components/BackgroundGrid';
import { calculateBlindDockingBox } from './utils/gridboxCalculator';
import './App.css';

function App() {
  const { activeTab, theme, setReceptorFile, setLigandFile, receptorFile, setParams } = useDockingStore();

  // DEBUG: Auto-load example data for testing (ENABLED for debugging)
  useEffect(() => {
    const loadExampleData = async () => {
      if (receptorFile) return;
      try {
        console.log("[AutoLoad] Fetching example data...");
        const [rRes, lRes] = await Promise.all([
          fetch('/examples/receptor.pdbqt'),
          fetch('/examples/ligand.pdbqt')
        ]);

        if (rRes.ok && lRes.ok) {
          const rText = await rRes.text();
          const lText = await lRes.text();
          setReceptorFile({ name: 'receptor.pdbqt', content: rText, format: 'pdbqt' });
          setLigandFile({ name: 'ligand.pdbqt', content: lText, format: 'pdbqt' });

          // Calculate valid grid box for the loaded receptor (blind docking default)
          const box = calculateBlindDockingBox(rText);
          setParams({
            ...box,
            exhaustiveness: 8,
            cpus: 4
          });

          console.log("[AutoLoad] Example data and PARAMS loaded into store.");
        } else {
          console.error("[AutoLoad] Failed to fetch examples", rRes.status, lRes.status);
        }
      } catch (e) {
        console.error("[AutoLoad] Error loading examples:", e);
      }
    };
    loadExampleData();
  }, []);

  // Sync theme to body class for global CSS variables
  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light-mode');
    } else {
      document.body.classList.remove('light-mode');
    }
  }, [theme]);


  const renderActivePanel = () => {
    switch (activeTab) {
      case 'prep':
        return (
          <DraggablePanel title="Molecule Import" width="500px" initialX={60} initialY={80}>
            <PrepPanel />
          </DraggablePanel>
        );
      case 'input':
        return (
          <DraggablePanel title="Input Parameters" width="450px" initialX={60} initialY={80}>
            <InputPanel />
          </DraggablePanel>
        );
      case 'batch':
        return (
          <DraggablePanel title="Batch Docking" width="600px" initialX={60} initialY={80}>
            <BatchPanel />
          </DraggablePanel>
        );
      case 'existing':
        return (
          <DraggablePanel title="Load Results" width="400px" initialX={60} initialY={200}>
            <ExistingOutputPanel />
          </DraggablePanel>
        );
      case 'running':
        return (
          <DraggablePanel title="Docking Status" width="600px" initialX={window.innerWidth / 2 - 300} initialY={window.innerHeight / 2 - 200}>
            <RunningPanel />
          </DraggablePanel>
        );
      case 'output':
        return (
          <DraggablePanel title="Docking Results" width="450px" initialX={window.innerWidth - 500} initialY={80}>
            <OutputPanel />
          </DraggablePanel>
        );
      case 'projects':
        return (
          <DraggablePanel title="Mission Log" width="400px" initialX={60} initialY={80}>
            <ProjectPanel />
          </DraggablePanel>
        );
      default:
        return null;
    }
  };

  return (
    <div className="app spatial-mode">
      {/* LAYER 0: GLOBAL VIEWER */}
      <div className="global-viewer-layer">
        <MoleculeViewer />
      </div>

      {/* LAYER 1: UI OVERLAY */}
      <div className="ui-overlay-layer">
        {activeTab === 'landing' ? (
          <LandingPanel />
        ) : (
          <>
            <Sidebar />
            <FloatingToolbar />
            {renderActivePanel()}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
