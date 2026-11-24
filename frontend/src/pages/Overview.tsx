import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, Lock, EyeOff, CheckCircle2, Activity, Play } from 'lucide-react';
import { api, ProjectConfig, SecurityIncident } from '../services/api';

export const Overview: React.FC = () => {
  const [projects, setProjects] = useState<ProjectConfig[]>([]);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scanText, setScanText] = useState('Consulta médica para Juan Pérez con DNI 12345678Z sobre tratamiento de cardiología');
  const [scanResult, setScanResult] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [projRes, incRes, hlthRes] = await Promise.all([
          api.getProjects(),
          api.getIncidents(10),
          api.getHealth()
        ]);
        setProjects(projRes);
        setIncidents(incRes);
        setHealth(hlthRes);
      } catch (e) {
        console.error("Error loading overview data", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleQuickScan = async () => {
    if (!scanText.trim()) return;
    setScanning(true);
    try {
      const res = await api.scanPrivacy(scanText, 'default');
      setScanResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Security Overview</h2>
          <p className="text-sm text-slate-500 mt-1">
            Plataforma centralizada de protección de software y privacidad LLM para Praxia Labs.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            Motor A (BLA) & Motor B (Privacy) Operativos
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Proyectos Registrados</span>
            <Shield className="w-5 h-5 text-[#0A66C2]" />
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900">{projects.length}</span>
            <span className="text-xs text-slate-500 ml-2">SaaS monitorizados</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">BLA Hardening Shield</span>
            <Lock className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-emerald-600">Activo</span>
            <span className="text-xs text-slate-500 ml-2">Preserva originales</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Incidencias de Seguridad</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900">{incidents.length}</span>
            <span className="text-xs text-amber-600 ml-2">Fail-Closed activo</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Privacy Gateway</span>
            <EyeOff className="w-5 h-5 text-[#0052CC]" />
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900">AES-GCM</span>
            <span className="text-xs text-slate-500 ml-2">Token Vault cifrado</span>
          </div>
        </div>
      </div>

      {/* Interactive Quick Scan Simulator */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center space-x-2 mb-3">
          <Activity className="w-5 h-5 text-[#0A66C2]" />
          <h3 className="text-base font-bold text-slate-900">Simulador de Inspección de Privacidad en Vivo</h3>
        </div>
        <p className="text-xs text-slate-500 mb-4">
          Prueba el motor de clasificación y detección de PII/Secretos antes de que las peticiones se reenvíen a Headroom u OmniRoute.
        </p>

        <div className="space-y-3">
          <textarea
            value={scanText}
            onChange={(e) => setScanText(e.target.value)}
            rows={3}
            className="w-full text-sm p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-[#0A66C2] focus:outline-none font-mono bg-slate-50 text-slate-900"
            placeholder="Introduce texto con PII o secretos para probar la detección..."
          />
          <div className="flex justify-end">
            <button
              onClick={handleQuickScan}
              disabled={scanning}
              className="flex items-center space-x-2 bg-[#0A66C2] hover:bg-[#0052CC] text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow"
            >
              <Play className="w-4 h-4" />
              <span>{scanning ? 'Analizando...' : 'Ejecutar Privacy Scan'}</span>
            </button>
          </div>
        </div>

        {scanResult && (
          <div className="mt-5 p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase">Resultado de Clasificación:</span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                scanResult.classification.level === 'RESTRICTED' ? 'bg-red-100 text-red-800' :
                scanResult.classification.level === 'CONFIDENTIAL' ? 'bg-amber-100 text-amber-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {scanResult.classification.level}
              </span>
            </div>
            <div className="text-xs text-slate-600">
              <span className="font-semibold">Razón:</span> {scanResult.classification.reason}
            </div>
            <div className="text-xs font-mono bg-white p-3 rounded border border-slate-200 text-slate-800">
              <div className="text-slate-400 mb-1 text-[11px]">// Texto seudonimizado con Token Vault:</div>
              {scanResult.processed_text}
            </div>
          </div>
        )}
      </div>

      {/* Projects Status Summary */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h3 className="text-base font-bold text-slate-900 mb-4">Ecosistema SaaS Praxia Labs</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 text-xs uppercase font-semibold">
                <th className="pb-3">Proyecto</th>
                <th className="pb-3">Tecnología</th>
                <th className="pb-3">BLA Shield</th>
                <th className="pb-3">Política Privacidad</th>
                <th className="pb-3">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/50">
                  <td className="py-3 font-semibold text-slate-800">{p.name}</td>
                  <td className="py-3 text-slate-600 text-xs">
                    {p.technology.backend || p.technology.frontend || 'General'}
                  </td>
                  <td className="py-3">
                    <span className="inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      {p.protection.intensity}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="text-xs font-mono font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      {p.privacy.classification_default}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="inline-flex items-center text-xs font-semibold text-emerald-600">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      Protegido
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
