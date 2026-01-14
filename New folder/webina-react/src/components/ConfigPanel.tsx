import React from 'react';
import type { IVinaParams } from '../services/types';

interface ConfigPanelProps {
    params: IVinaParams;
    onChange: (key: keyof IVinaParams, value: any) => void;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ params, onChange }) => {
    return (
        <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="text-xl font-bold mb-4">Configuration</h3>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm">Center X</label>
                    <input type="number" step="0.1" value={params.center_x}
                        onChange={(e) => onChange('center_x', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Center Y</label>
                    <input type="number" step="0.1" value={params.center_y}
                        onChange={(e) => onChange('center_y', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Center Z</label>
                    <input type="number" step="0.1" value={params.center_z}
                        onChange={(e) => onChange('center_z', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Size X</label>
                    <input type="number" step="1" value={params.size_x}
                        onChange={(e) => onChange('size_x', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Size Y</label>
                    <input type="number" step="1" value={params.size_y}
                        onChange={(e) => onChange('size_y', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Size Z</label>
                    <input type="number" step="1" value={params.size_z}
                        onChange={(e) => onChange('size_z', parseFloat(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
                <div>
                    <label className="block text-sm">Exhaustiveness</label>
                    <input type="number" step="1" value={params.exhaustiveness}
                        onChange={(e) => onChange('exhaustiveness', parseInt(e.target.value))}
                        className="w-full bg-gray-700 p-1 rounded" />
                </div>
            </div>
        </div>
    );
};
