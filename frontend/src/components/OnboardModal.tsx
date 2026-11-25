import React, { useState } from 'react';
import {
  X,
  Shield,
  Globe,
  GitBranch,
  Rocket,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ExternalLink,
  FolderOpen
} from 'lucide-react';
import { api } from '../services/api';

interface OnboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const OnboardModal: React.FC<OnboardModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [projectPath, setProjectPath] = useState('');
  const [projectName, setProjectName] = useState('');
  const [subdomain, setSubdomain] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [intensity, setIntensity] = useState('balanced');
  const [dryRun, setDryRun] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  if (!isOpen) return null;

  const handlePathChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setProjectPath(val);

    // Auto-extraer nombre de carpeta para sugerir nombre y subdominio
    const trimmed = val.replace(/\/+$/, '');
    const parts = trimmed.split('/');
    const last = parts[parts.length - 1];
    if (last && (!projectName || projectName === last)) {
      setProjectName(last);
    }
    if (last && (!subdomain || subdomain === last.toLowerCase())) {
      setSubdomain(last.toLowerCase().replace(/[^a-z0-9-]/g, '-'));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectPath.trim()) {
      setError('Por favor indica la ruta del proyecto en WSL/Linux.');
      return;
    }

    const cleanSubdomain = (subdomain.trim() || projectName.trim() || 'app').toLowerCase();
    const finalDomain = cleanSubdomain.endsWith('.praxialabs.com')
      ? cleanSubdomain
      : `${cleanSubdomain}.praxialabs.com`;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.onboardProject({
        project_path: projectPath.trim(),
        name: projectName.trim() || undefined,
        domain: finalDomain,
        repo_name: projectName.trim() || undefined,
        is_private: isPrivate,
        intensity,
        dry_run: dryRun
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Error durante la ejecución del onboarding.');
    } finally {
      setLoading(false);
    }
  };

  const handleFinish = () => {
    onSuccess();
    onClose();
  };

  const cleanSubdomain = (subdomain.trim() || projectName.trim() || 'mi-app').toLowerCase();
  const previewDomain = cleanSubdomain.endsWith('.praxialabs.com')
    ? cleanSubdomain
    : `${cleanSubdomain}.praxialabs.com`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-900 via-slate-800 to-[#0A66C2] text-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center border border-white/20">
              <Rocket className="w-5 h-5 text-blue-300" />
            </div>
            <div>
              <h3 className="text-lg font-bold">Añadir Proyecto a Producción</h3>
              <p className="text-xs text-blue-200">
                Pipeline automático: Blind LLM Agent + DNS + GitHub + Vercel
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start space-x-3 text-rose-800 text-sm">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Error al procesar el onboarding</p>
                <p className="text-xs mt-0.5 text-rose-700">{error}</p>
              </div>
            </div>
          )}

          {result ? (
            /* Results Screen */
            <div className="space-y-5 animate-fade-in">
              <div className="p-5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start space-x-4">
                <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-emerald-950">
                    {dryRun ? '¡Simulación Completada con Éxito!' : '¡Proyecto Desplegado y Protegido!'}
                  </h4>
                  <p className="text-xs text-emerald-800 mt-1">
                    Se han ejecutado todas las etapas de seguridad y aprovisionamiento.
                  </p>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    URL de Producción / DNS
                  </span>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 font-bold text-[#0A66C2] flex items-center hover:underline truncate"
                  >
                    {result.url}
                    <ExternalLink className="w-3.5 h-3.5 ml-1 shrink-0" />
                  </a>
                  <span className="text-[11px] text-emerald-600 font-medium mt-1 block">
                    ✓ DNS verificado en praxialabs.com
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Repositorio GitHub
                  </span>
                  {result.github_repo ? (
                    <a
                      href={result.github_repo}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-1 font-bold text-slate-800 flex items-center hover:underline truncate"
                    >
                      {result.github_repo}
                      <ExternalLink className="w-3.5 h-3.5 ml-1 shrink-0" />
                    </a>
                  ) : (
                    <p className="mt-1 font-mono text-xs text-slate-600">Sincronizado</p>
                  )}
                  <span className="text-[11px] text-slate-500 mt-1 block">
                    ✓ Commits y ramas publicadas
                  </span>
                </div>
              </div>

              {/* Hardening & Registry details */}
              <div className="p-4 rounded-xl bg-slate-900 text-slate-200 font-mono text-xs space-y-2">
                <div className="text-emerald-400 font-bold border-b border-slate-800 pb-2">
                  // REPORTE DE EJECUCIÓN PRAXIA
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Blind LLM Agent (BLA):</span>
                  <span className="text-emerald-400">ACTIVO (scripts/praxia-harden.js)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Source Maps (.map):</span>
                  <span className="text-emerald-400">Eliminados automáticamente</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Postbuild Hook:</span>
                  <span className="text-emerald-400">Configurado en package.json</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Registro en Security Hub:</span>
                  <span className="text-emerald-400">
                    {result.praxia_registered ? 'MONITOREADO' : 'SIMULADO'}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            /* Input Form */
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Ruta WSL / Linux */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  1. Ruta del proyecto (en tu WSL / Linux) *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={projectPath}
                    onChange={handlePathChange}
                    placeholder="/home/jmari/proyectosIA/mi-nuevo-saas"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A66C2] focus:border-transparent text-sm font-mono text-slate-800 placeholder-slate-400"
                  />
                  <FolderOpen className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Ruta absoluta a la raíz de tu proyecto donde se encuentra <code>package.json</code>.
                </p>
              </div>

              {/* Subdominio / DNS deseado */}
              <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 space-y-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-blue-950">
                  2. ¿Qué DNS / Subdominio le vamos a dar? *
                </label>
                <div className="flex items-center">
                  <div className="relative flex-1">
                    <input
                      type="text"
                      required
                      value={subdomain}
                      onChange={(e) => setSubdomain(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                      placeholder="minuevoapp"
                      className="w-full px-3.5 py-2 rounded-l-xl border border-blue-300 focus:outline-none focus:ring-2 focus:ring-[#0A66C2] text-sm font-semibold text-slate-900 bg-white"
                    />
                  </div>
                  <span className="px-3.5 py-2 bg-blue-600 text-white font-mono text-sm font-bold rounded-r-xl border border-blue-600 select-none">
                    .praxialabs.com
                  </span>
                </div>
                <div className="flex items-center text-xs text-blue-800 font-medium pt-1">
                  <Globe className="w-3.5 h-3.5 mr-1 text-blue-600 shrink-0" />
                  <span>URL pública final: </span>
                  <span className="font-mono font-bold ml-1 text-blue-900">
                    https://{previewDomain}
                  </span>
                </div>
              </div>

              {/* Opciones Avanzadas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Nombre de Proyecto & Repo */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Nombre del Repositorio GitHub
                  </label>
                  <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="mi-nuevo-saas"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A66C2] text-sm text-slate-800"
                  />
                  <div className="mt-2 flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="isPrivate"
                      checked={isPrivate}
                      onChange={(e) => setIsPrivate(e.target.checked)}
                      className="rounded text-[#0A66C2] focus:ring-blue-500 h-4 w-4"
                    />
                    <label htmlFor="isPrivate" className="text-xs text-slate-600 select-none">
                      Repositorio privado en GitHub
                    </label>
                  </div>
                </div>

                {/* Intensidad BLA */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Intensidad de Blind LLM Agent (BLA)
                  </label>
                  <select
                    value={intensity}
                    onChange={(e) => setIntensity(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A66C2] text-sm text-slate-800 bg-white"
                  >
                    <option value="balanced">Balanced (Recomendado)</option>
                    <option value="maximum">Maximum (Alta ofuscación)</option>
                    <option value="paranoid">Paranoid (Máximo blindaje)</option>
                    <option value="fast">Fast (Rápido / Bundles ligeros)</option>
                  </select>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Protege contra LLM decompilers y robo de código fuente.
                  </p>
                </div>
              </div>

              {/* Dry-run option */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dryRun}
                    onChange={(e) => setDryRun(e.target.checked)}
                    className="rounded text-[#0A66C2] focus:ring-blue-500 h-4 w-4"
                  />
                  <span className="text-xs text-slate-600">
                    Modo Simulación (Dry Run) — valida sin alterar recursos remotos
                  </span>
                </label>
              </div>

              {/* Pipeline summary checklist */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1.5">
                <div className="font-semibold text-slate-700 mb-1">
                  Acciones que se ejecutarán automáticamente:
                </div>
                <div className="flex items-center text-slate-700">
                  <Shield className="w-3.5 h-3.5 text-emerald-600 mr-2 shrink-0" />
                  Inyección de <code>scripts/praxia-harden.js</code> + eliminación de mapas <code>.map</code>
                </div>
                <div className="flex items-center text-slate-700">
                  <GitBranch className="w-3.5 h-3.5 text-purple-600 mr-2 shrink-0" />
                  Inicialización Git y publicación en GitHub (<code>jmaria69</code>)
                </div>
                <div className="flex items-center text-slate-700">
                  <Globe className="w-3.5 h-3.5 text-blue-600 mr-2 shrink-0" />
                  Configuración de DNS en <code>praxialabs.com</code> (Vercel DNS)
                </div>
                <div className="flex items-center text-slate-700">
                  <Rocket className="w-3.5 h-3.5 text-amber-600 mr-2 shrink-0" />
                  Despliegue a producción en Vercel y verificación HTTP 200
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-sm font-semibold transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#0A66C2] hover:bg-[#0052CC] text-white text-sm font-semibold shadow-md transition disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Ejecutando Onboarding...</span>
                    </>
                  ) : (
                    <>
                      <Rocket className="w-4 h-4" />
                      <span>Iniciar Onboarding y Despliegue</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Modal Footer (when finished) */}
        {result && (
          <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
            <button
              onClick={handleFinish}
              className="px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold transition shadow-sm"
            >
              Cerrar y Actualizar Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
