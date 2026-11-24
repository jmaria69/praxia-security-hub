import React, { useEffect, useState } from 'react';
import { FileText, AlertOctagon, CheckCircle } from 'lucide-react';
import { api, AuditEvent, SecurityIncident } from '../services/api';

export const AuditCenter: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);

  useEffect(() => {
    Promise.all([api.getAuditEvents(50), api.getIncidents(50)]).then(([evs, incs]) => {
      setEvents(evs);
      setIncidents(incs);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Audit & Incident Center</h2>
          <p className="text-sm text-slate-500 mt-1">
            Registro inmutable de eventos de seguridad, operaciones de protección BLA e incidencias interceptadas.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Incidents Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center">
            <AlertOctagon className="w-4 h-4 text-red-500 mr-2" />
            Incidencias de Seguridad Interceptadas
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 uppercase font-semibold">
                  <th className="pb-2">Fecha</th>
                  <th className="pb-2">Categoría</th>
                  <th className="pb-2">Severidad</th>
                  <th className="pb-2">Proyecto</th>
                  <th className="pb-2">Resumen</th>
                  <th className="pb-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {incidents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-4 text-center text-slate-400">
                      No hay incidencias abiertas. La plataforma está operando normalmente.
                    </td>
                  </tr>
                ) : (
                  incidents.map((inc) => (
                    <tr key={inc.id} className="hover:bg-slate-50">
                      <td className="py-2.5 font-mono text-slate-500">{inc.timestamp}</td>
                      <td className="py-2.5 font-medium text-slate-800">{inc.category}</td>
                      <td className="py-2.5">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700">
                          {inc.severity}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono">{inc.project_id || 'global'}</td>
                      <td className="py-2.5 text-slate-600">{inc.summary}</td>
                      <td className="py-2.5 font-semibold text-emerald-600">{inc.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Audit Events */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center">
            <FileText className="w-4 h-4 text-[#0A66C2] mr-2" />
            Registro de Operaciones Administrativas (Audit Log)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 uppercase font-semibold">
                  <th className="pb-2">Fecha</th>
                  <th className="pb-2">Tipo de Evento</th>
                  <th className="pb-2">Acción</th>
                  <th className="pb-2">Usuario</th>
                  <th className="pb-2">Proyecto</th>
                  <th className="pb-2">Severidad</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50">
                    <td className="py-2 font-mono text-slate-500">{ev.timestamp}</td>
                    <td className="py-2 font-medium text-slate-800">{ev.event_type}</td>
                    <td className="py-2 text-slate-700 font-mono text-[11px]">{ev.action}</td>
                    <td className="py-2 text-slate-600">{ev.user}</td>
                    <td className="py-2 font-mono">{ev.project_id || '-'}</td>
                    <td className="py-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        ev.severity === 'WARNING' ? 'bg-amber-100 text-amber-700' :
                        ev.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {ev.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
