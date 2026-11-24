import React, { useEffect, useState } from 'react';
import { EyeOff, Key, Lock, ShieldAlert, Check } from 'lucide-react';
import { api } from '../services/api';

export const PrivacyCenter: React.FC = () => {
  const [vaultStatus, setVaultStatus] = useState<any>(null);
  const [promptText, setPromptText] = useState('Secret token: sk-ant-api03-example98765432109876543210');
  const [scanOutput, setScanOutput] = useState<any>(null);

  useEffect(() => {
    api.getTokenVaultStatus().then(setVaultStatus);
  }, []);

  const handleTestScan = async () => {
    try {
      const res = await api.scanPrivacy(promptText);
      setScanOutput(res);
    } catch (e: any) {
      setScanOutput({ error: "Fail-Closed triggered: " + e.message });
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">LLM Privacy & Token Vault Center</h2>
          <p className="text-sm text-slate-500 mt-1">
            Detección de PII con Presidio, escaneo de secretos de alta entropía y seudonimización reversible AES-256-GCM.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          Fail-Closed Enforcement Activo
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Token Vault Status */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Key className="w-5 h-5 text-[#0A66C2]" />
            <h3 className="font-bold text-slate-900 text-sm">Token Vault Criptográfico</h3>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Algoritmo:</span>
              <span className="font-mono font-bold text-slate-800">AES-256-GCM</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Mapeos Activos:</span>
              <span className="font-mono font-bold text-emerald-600">{vaultStatus?.active_tokens_count || 0}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Aislamiento:</span>
              <span className="font-mono font-bold text-slate-800">Por Proyecto & Sesión</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">TTL Tokens:</span>
              <span className="font-mono font-bold text-slate-800">24 Horas</span>
            </div>
          </div>
        </div>

        {/* Classification Matrix */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4 md:col-span-2">
          <div className="flex items-center space-x-2">
            <Lock className="w-5 h-5 text-[#0052CC]" />
            <h3 className="font-bold text-slate-900 text-sm">Matriz de Clasificación y Políticas de Tratamiento</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="font-bold text-slate-700">PUBLIC</span>
              <p className="text-[11px] text-slate-500 mt-1">Sin restricciones. Pasarela transparente.</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="font-bold text-blue-700">INTERNAL</span>
              <p className="text-[11px] text-slate-500 mt-1">Auditoría básica. Filtrado de identificadores.</p>
            </div>
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
              <span className="font-bold text-amber-700">CONFIDENTIAL</span>
              <p className="text-[11px] text-slate-500 mt-1">Seudonimización obligatoria mediante Token Vault.</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <span className="font-bold text-red-700">RESTRICTED</span>
              <p className="text-[11px] text-slate-500 mt-1">Bloqueo automático si contiene secretos (Fail-Closed).</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
