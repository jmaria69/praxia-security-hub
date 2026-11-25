import React, { useEffect, useState } from 'react';
import { Layers, Folder, Shield, ArrowUpRight, Search, FileCode, Plus } from 'lucide-react';
import { api, ProjectConfig } from '../services/api';
import { OnboardModal } from '../components/OnboardModal';

export const ProjectSecurity: React.FC = () => {
  const [projects, setProjects] = useState<ProjectConfig[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectConfig | null>(null);
  const [auditReport, setAuditReport] = useState<any>(null);
  const [auditing, setAuditing] = useState(false);
  const [isOnboardOpen, setIsOnboardOpen] = useState(false);

  useEffect(() => {
    api.getProjects().then(data => {
      setProjects(data);
      if (data.length > 0) setSelectedProject(data[0]);
    });
  }, []);

  const handleAudit = async (proj: ProjectConfig) => {
    setAuditing(true);
    setAuditReport(null);
    try {
      const res = await api.auditProject(proj.id);
      setAuditReport(res);
    } catch (e) {
      console.error(e);
    } finally {
      setAuditing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Project Security Registry</h2>
          <p className="text-sm text-slate-500 mt-1">
            Gestión individual de políticas de protección BLA y privacidad LLM para cada producto de Praxia Labs.
          </p>
        </div>
        <button
          onClick={() => setIsOnboardOpen(true)}
          className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold shadow-sm transition"
        >
          <Plus className="w-4 h-4" />
          <span>+ Añadir Proyecto (Onboard)</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project List */}
        <div className="lg:col-span-1 space-y-3">
          {projects.map((p) => {
            const isSelected = selectedProject?.id === p.id;
            return (
              <div
                key={p.id}
                onClick={() => { setSelectedProject(p); setAuditReport(null); }}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-white border-[#0A66C2] shadow-md ring-2 ring-blue-500/20'
                    : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                }`}
              >
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-slate-900 text-sm">{p.name}</h4>
                  <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {p.id}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 line-clamp-1">{p.description}</p>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-mono text-[11px] truncate max-w-[170px]">
                    {p.root_path}
                  </span>
                  <span className="text-[#0A66C2] font-semibold flex items-center">
                    Ver ficha <ArrowUpRight className="w-3 h-3 ml-0.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Project Detail Card */}
        {selectedProject && (
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
            <div className="flex justify-between items-start border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900">{selectedProject.name}</h3>
                <p className="text-xs text-slate-500 font-mono mt-0.5">{selectedProject.root_path}</p>
              </div>
              <button
                onClick={() => handleAudit(selectedProject)}
                disabled={auditing}
                className="flex items-center space-x-2 bg-[#0A66C2] hover:bg-[#0052CC] text-white px-3.5 py-2 rounded-lg text-xs font-semibold transition"
              >
                <Search className="w-3.5 h-3.5" />
                <span>{auditing ? 'Auditoría en curso...' : 'Ejecutar Auditoría BLA'}</span>
              </button>
            </div>

            {/* Properties Grid */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-400 font-semibold uppercase">Stack Tecnológico</span>
                <p className="font-medium text-slate-800 mt-1">
                  {selectedProject.technology.frontend || 'Sin frontend'} / {selectedProject.technology.backend || 'Sin backend'}
                </p>
                <span className="text-xs text-slate-500">Output: {selectedProject.technology.build_output || 'dist'}</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-400 font-semibold uppercase">Protección BLA</span>
                <p className="font-medium text-emerald-700 mt-1 flex items-center">
                  <Shield className="w-3.5 h-3.5 mr-1" />
                  Intensidad: {selectedProject.protection.intensity}
                </p>
                <span className="text-xs text-slate-500">Invariantes & Rollback activos</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-400 font-semibold uppercase">Nivel de Clasificación</span>
                <p className="font-medium text-[#0052CC] mt-1">
                  {selectedProject.privacy.classification_default}
                </p>
                <span className="text-xs text-slate-500">Fail-Closed: {selectedProject.privacy.fail_closed ? 'Sí' : 'No'}</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-400 font-semibold uppercase">Proveedores Autorizados</span>
                <p className="font-medium text-slate-800 mt-1 font-mono text-xs">
                  {selectedProject.allowed_providers.join(', ')}
                </p>
                <span className="text-xs text-slate-500">Token Vault: Habilitado</span>
              </div>
            </div>

            {/* Audit Results Panel */}
            {auditReport && (
              <div className="mt-4 p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-xs space-y-3">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <span className="text-emerald-400 font-bold">// INFORME DE EXPOSICIÓN REA (BLA AUDIT)</span>
                  <span className="text-amber-400">Puntuación: {auditReport.exposureScore || 0}/100</span>
                </div>
                <div>Formato: {auditReport.detectedFormat || 'Desconocido'}</div>
                <div>Hash SHA-256: {auditReport.sha256 || 'N/A'}</div>
                <div>Advertencia: {auditReport.headlineWarning || 'Sin advertencias críticas'}</div>
              </div>
            )}
          </div>
        )}
      </div>

      <OnboardModal
        isOpen={isOnboardOpen}
        onClose={() => setIsOnboardOpen(false)}
        onSuccess={() => {
          api.getProjects().then(data => {
            setProjects(data);
            if (data.length > 0) setSelectedProject(data[data.length - 1]);
          });
        }}
      />
    </div>
  );
};
