// API Client for Praxia Security Hub Dashboard
export interface ProjectConfig {
  id: string;
  name: string;
  description: string;
  root_path: string;
  technology: {
    frontend?: string;
    backend?: string;
    build_output?: string;
  };
  protection: {
    enabled: boolean;
    engine: string;
    intensity: string;
    preserve_originals: boolean;
    verify_invariants: boolean;
  };
  privacy: {
    enabled: boolean;
    classification_default: string;
    fail_closed: boolean;
  };
  allowed_providers: string[];
  status: string;
}

export interface AuditEvent {
  id: number;
  timestamp: string;
  event_type: string;
  project_id?: string;
  severity: string;
  user: string;
  action: string;
  details_json: string;
}

export interface SecurityIncident {
  id: number;
  timestamp: string;
  project_id?: string;
  category: string;
  severity: string;
  summary: string;
  details_json: string;
  status: string;
}

const API_BASE = '/api';

export const api = {
  async getHealth() {
    const res = await fetch('/health');
    return res.json();
  },
  async getProjects(): Promise<ProjectConfig[]> {
    const res = await fetch(`${API_BASE}/projects`);
    return res.json();
  },
  async getProject(id: string): Promise<ProjectConfig> {
    const res = await fetch(`${API_BASE}/projects/${id}`);
    return res.json();
  },
  async getBlaDoctor() {
    const res = await fetch(`${API_BASE}/protection/doctor`);
    return res.json();
  },
  async auditProject(projectId: string, subpath?: string) {
    const res = await fetch(`${API_BASE}/protection/audit?project_id=${projectId}${subpath ? `&target_subpath=${subpath}` : ''}`, {
      method: 'POST'
    });
    return res.json();
  },
  async scanPrivacy(text: string, projectId: string = 'default') {
    const res = await fetch(`${API_BASE}/privacy/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, project_id: projectId, session_id: 'web_session' })
    });
    return res.json();
  },
  async getTokenVaultStatus() {
    const res = await fetch(`${API_BASE}/privacy/token-vault/status`);
    return res.json();
  },
  async getAuditEvents(limit: number = 50, projectId?: string): Promise<AuditEvent[]> {
    const url = `${API_BASE}/audit/events?limit=${limit}${projectId ? `&project_id=${projectId}` : ''}`;
    const res = await fetch(url);
    return res.json();
  },
  async getIncidents(limit: number = 50, projectId?: string): Promise<SecurityIncident[]> {
    const url = `${API_BASE}/audit/incidents?limit=${limit}${projectId ? `&project_id=${projectId}` : ''}`;
    const res = await fetch(url);
    return res.json();
  }
};
