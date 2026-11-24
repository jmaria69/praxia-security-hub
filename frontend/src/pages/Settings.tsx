import React from 'react';
import { Settings as SettingsIcon, Server, Shield, Key } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings & Infrastructure</h2>
          <p className="text-sm text-slate-500 mt-1">
            Configuración de enrutamiento LLM, adaptadores de OmniRoute / Headroom y parámetros de seguridad de Praxia Labs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Server className="w-5 h-5 text-[#0A66C2]" />
            <h3 className="font-bold text-slate-900">Enrutamiento LLM Upstream</h3>
          </div>
          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-500 block">Headroom Optimizer Proxy:</span>
              <span className="font-mono font-semibold text-slate-800">http://127.0.0.1:8787</span>
            </div>
            <div>
              <span className="text-slate-500 block">OmniRoute Multi-Provider Gateway:</span>
              <span className="font-mono font-semibold text-slate-800">http://127.0.0.1:20128</span>
            </div>
            <div>
              <span className="text-slate-500 block">Praxia Privacy Gateway (Interceptor):</span>
              <span className="font-mono font-semibold text-[#0A66C2]">http://127.0.0.1:8888</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Shield className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-slate-900">Políticas Globales de Seguridad</h3>
          </div>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-600">Fail-Closed en Fuga de Secretos:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">HABILITADO</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-600">Preservación Inmutable de Artefactos:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">HABILITADO</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-600">Restauración de Respuestas LLM:</span>
              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">SESIÓN AUTORIZADA</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
