import React, { useRef } from 'react';

interface InputPanelProps {
    label: string;
    value: string;
    onChange: (val: string) => void;
}

export const InputPanel: React.FC<InputPanelProps> = ({ label, value, onChange }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const text = await file.text();
        onChange(text);
    };

    return (
        <div className="p-4 bg-gray-800 rounded-lg mb-4">
            <h3 className="text-xl font-bold mb-2">{label}</h3>
            <div className="mb-2">
                <input type="file" ref={fileInputRef} onChange={handleFileChange} className="text-sm" />
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full h-32 bg-gray-900 font-mono text-xs p-2 rounded"
                placeholder={`Paste ${label} PDBQT content here...`}
            />
        </div>
    );
};
