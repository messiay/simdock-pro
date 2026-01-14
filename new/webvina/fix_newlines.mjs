import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const examplesDir = path.join(__dirname, 'public', 'examples');

function fixFile(filename) {
    const filePath = path.join(examplesDir, filename);
    if (!fs.existsSync(filePath)) {
        console.error(`File not found: ${filePath}`);
        return;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    const originalSize = content.length;

    // Check if CRLF exists
    if (!content.includes('\r\n')) {
        console.log(`[OK] ${filename} already has LF line endings.`);
        return;
    }

    // Replace CRLF with LF
    content = content.replace(/\r\n/g, '\n');
    fs.writeFileSync(filePath, content, 'utf8');

    console.log(`[FIXED] ${filename}: Converted CRLF to LF. Size: ${originalSize} -> ${content.length}`);
}

console.log("Fixing PDBQT line endings...");
fixFile('receptor.pdbqt');
fixFile('ligand.pdbqt');
console.log("Done.");
