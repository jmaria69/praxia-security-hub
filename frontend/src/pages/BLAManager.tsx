import React, { useEffect, useState } from 'react';
import { Lock, ShieldCheck, Terminal, Cpu, CheckCircle2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const BLAManager: React.FC = () => {
  const [doctorData, setDoctorData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getBlaDoctor().then(data => {
      setDoctorData(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">BLA Software Protection Engine</h2>
          <p className="text-sm text-slate-500 mt-1">
            Integración de Blind LLM Agents (BLA) v1.1.0 (v3.6.0 npm) para neutralizar agentes de ingeniería inversa con IA.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          Shield Engine Activo
        </span>
      </div>

      {doctorData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Engines Readiness Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Cpu className="w-5 h-5 text-[#0A66C2]" />
              <h3 className="font-bold text-slate-900 text-base">Motores de Protección Compilados</h3>
            </div>
            <div className="space-y-2.5">
              {Object.entries(doctorData.engines || {}).map(([engine, status]: [string, any]) => (
                <div key={engine} className="flex justify-between items-center text-xs p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                  <span className="font-mono text-slate-700 font-semibold">{engine}</span>
                  <span className="inline-flex items-center text-emerald-600 font-medium font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                    {status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Connected AI Agents */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Terminal className="w-5 h-5 text-[#0052CC]" />
              <h3 className="font-bold text-slate-900 text-base">Integración MCP & Agentes Detectados</h3>
            </div>
            <div className="space-y-2.5">
              {(doctorData.agentClients || []).map((client: any) => (
                <div key={client.id} className="flex justify-between items-center text-xs p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                  <div>
                    <span className="font-semibold text-slate-800">{client.displayName}</span>
                    <span className="text-slate-400 font-mono text-[10px] ml-2">({client.id})</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                    client.detected ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {client.detected ? 'Detectado en Sistema' : 'No instalado'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Counter-REA Strategy explanation */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h3 className="font-bold text-slate-900 text-base mb-3">Mecanismos Defensivos Activos (Poison → Exhaust → Hallucinate)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 space-y-2">
            <h4 className="font-bold text-[#0A66C2] uppercase">1. Inyección de Señuelos (Poison)</h4>
            <p className="text-slate-600">
              Generación de tablas trampa, esquemas RPC dinámicos y telemetría sintética que guían a los modelos de descompilación a inferencias erróneas.
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 space-y-2">
            <h4 className="font-bold text-[#0052CC] uppercase">2. Tarpit Algorítmico (Exhaust)</h4>
            <p className="text-slate-600">
              Expansión combinatoria de llamadas opacas y ramificaciones recursivas que saturan la ventana de contexto de los agentes de análisis (&gt;1,200x amplificación de tokens).
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 space-y-2">
            <h4 className="font-bold text-emerald-700 uppercase">3. Equivalencia de Ejecución (Preserve)</h4>
            <p className="text-slate-600">
              El comportamiento en tiempo de ejecución para los usuarios finales se conserva al 100%. Los artefactos originales se preservan inmutables con hash SHA-256.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
