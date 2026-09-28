import type { Incident, Investigation } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getIncidents(): Promise<Incident[]> {
  const r = await fetch(`${API}/api/incidents`);
  if (!r.ok) throw new Error('Failed to load incidents');
  return r.json();
}

export async function investigate(id: string): Promise<Investigation> {
  const r = await fetch(`${API}/api/incidents/${id}/investigate`, { method: 'POST' });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function resolveIncident(id: string, resolution: string): Promise<Incident> {
  const r = await fetch(`${API}/api/incidents/${id}/resolve?resolution=${encodeURIComponent(resolution)}`, { method: 'POST' });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
