
import { useState } from 'react'
import { Beaker } from 'lucide-react'
import BackgroundGrid from './components/BackgroundGrid'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-10 flex flex-col items-center justify-center relative overflow-hidden">
      <BackgroundGrid />
      <Beaker className="w-16 h-16 text-red-500 mb-4 z-10" />
      <h1 className="text-4xl text-emerald-400">Icons Test Passed</h1>
      <p>If you see this, icons are working.</p>
    </div>
  )
}
