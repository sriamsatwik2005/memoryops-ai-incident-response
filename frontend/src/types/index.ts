export type Incident = {
  id: number;
  external_id: string;
  service: string;
  severity: string;
  status: string;
  summary: string;
  logs: string;
  metrics: string;
  deployment: string;
  root_cause?: string | null;
  resolution?: string | null;
  created_at: string;
};

export type Investigation = {
  incident_id: string;
  root_cause: string;
  confidence: number;
  recommendation: string;
  reasoning: string;
  memories: { id?: string; text: string; type?: string; context?: string }[];
};
