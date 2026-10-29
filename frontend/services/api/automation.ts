import API from "./client";

/** Turn a FastAPI error body into a readable, non-technical message. */
function detailMessage(data: any): string {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d: any) => (typeof d?.msg === "string" ? d.msg : JSON.stringify(d)))
      .join("; ");
  }
  return "Request failed";
}

function getToken() {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface TriggerConfig {
  time?: string;           // "08:00"
  days?: string[];         // ["mon","tue","wed","thu","fri"]
  day_of_month?: number;
  cron?: string;
  interval_minutes?: number;
  event_type?: string;     // "task.completed"
  deadline_hours?: number;
  run_at?: string;         // ISO-8601 for one-time
  [key: string]: unknown;
}

export interface ConditionRule {
  field: string;
  operator: string;
  value: unknown;
}

export interface ConditionGroup {
  op: "and" | "or" | "not";
  rules: Array<ConditionRule | ConditionGroup>;
}

export type ConditionNode = ConditionRule | ConditionGroup;

export interface ActionStep {
  tool_name: string;
  arguments?: Record<string, unknown>;
  description?: string;
  confirmation_policy?: "default" | "preapproved";
}

export interface Automation {
  id: number;
  name: string;
  description?: string;
  trigger_type: string;
  trigger_config?: TriggerConfig;
  conditions?: ConditionNode[];
  actions?: ActionStep[];
  timezone: string;
  failure_policy: string;
  enabled: boolean;
  max_retries?: number;
  retry_delay_seconds?: number;
  next_run_at?: string;
  last_run_at?: string;
  created_at: string;
  updated_at?: string;
  // Legacy
  trigger?: string;
  action?: string;
}

export interface AutomationCreate {
  name: string;
  description?: string;
  trigger_type: string;
  trigger_config?: TriggerConfig;
  conditions?: ConditionNode[];
  actions?: ActionStep[];
  timezone?: string;
  failure_policy?: string;
  max_retries?: number;
  retry_delay_seconds?: number;
}

export interface AutomationUpdate {
  name?: string;
  description?: string;
  trigger_type?: string;
  trigger_config?: TriggerConfig;
  conditions?: ConditionNode[];
  actions?: ActionStep[];
  timezone?: string;
  failure_policy?: string;
  enabled?: boolean;
  max_retries?: number;
  retry_delay_seconds?: number;
}

export type RunStatus =
  | "running"
  | "completed"
  | "failed"
  | "partial"
  | "skipped"
  | "cancelled";

export interface AutomationRun {
  id: string;
  automation_id: number;
  user_id: number;
  status: RunStatus;
  trigger_source?: string;
  actions_attempted: number;
  actions_completed: number;
  execution_log?: Array<Record<string, unknown>>;
  error_message?: string;
  execution_key?: string;
  started_at: string;
  completed_at?: string;
}

export interface AutomationPreview {
  automation_id: number;
  next_run_at?: string;
  actions: ActionStep[];
  conditions: ConditionNode[];
  estimated_action_count: number;
  timezone: string;
}

/** Preview response for a draft that has not been saved yet. */
export interface DraftPreview {
  valid: boolean;
  name: string;
  trigger_type: string;
  trigger_config: TriggerConfig;
  timezone: string;
  next_run_at?: string | null;
  actions: ActionStep[];
  conditions: ConditionNode[];
  estimated_action_count: number;
  failure_policy: string;
}

// ─── CRUD ─────────────────────────────────────────────────────────────────────

export async function listAutomations(): Promise<Automation[]> {
  const res = await fetch(`${API}/automation/`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to fetch automations");
  return data;
}

export async function getAutomation(id: number): Promise<Automation> {
  const res = await fetch(`${API}/automation/${id}`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Automation not found");
  return data;
}

export async function createAutomation(payload: AutomationCreate): Promise<Automation> {
  const res = await fetch(`${API}/automation/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to create automation");
  return data;
}

export async function updateAutomation(
  id: number,
  payload: AutomationUpdate
): Promise<Automation> {
  const res = await fetch(`${API}/automation/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to update automation");
  return data;
}

export async function deleteAutomation(id: number): Promise<{ message: string }> {
  const res = await fetch(`${API}/automation/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok && res.status !== 404) throw new Error(detailMessage(data) || "Failed to delete");
  return data;
}

// ─── Enable / Disable ─────────────────────────────────────────────────────────

export async function enableAutomation(id: number): Promise<Automation> {
  const res = await fetch(`${API}/automation/${id}/enable`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to enable automation");
  return data;
}

export async function disableAutomation(id: number): Promise<Automation> {
  const res = await fetch(`${API}/automation/${id}/disable`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to disable automation");
  return data;
}

// ─── Manual Run ───────────────────────────────────────────────────────────────

export async function runAutomation(id: number): Promise<AutomationRun> {
  const res = await fetch(`${API}/automation/${id}/run`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to run automation");
  return data;
}

export async function cancelAutomation(
  id: number
): Promise<{ automation_id: number; cancelled_runs: number; message: string }> {
  const res = await fetch(`${API}/automation/${id}/cancel`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to cancel automation");
  return data;
}

// ─── History ──────────────────────────────────────────────────────────────────

export async function getAutomationRuns(
  id: number,
  limit = 50
): Promise<AutomationRun[]> {
  const res = await fetch(`${API}/automation/${id}/runs?limit=${limit}`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to fetch runs");
  return data;
}

// ─── Preview ──────────────────────────────────────────────────────────────────

export async function previewAutomation(id: number): Promise<AutomationPreview> {
  const res = await fetch(`${API}/automation/${id}/preview`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to preview automation");
  return data;
}

/**
 * Validate an unsaved automation draft and show what RajOS would do.
 * The backend re-validates everything on create, so the preview is advisory.
 */
export async function previewDraftAutomation(
  payload: AutomationCreate
): Promise<DraftPreview> {
  const res = await fetch(`${API}/automation/preview`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data));
  return data;
}

// ─── Event ────────────────────────────────────────────────────────────────────

export async function fireEvent(
  eventType: string,
  payload?: Record<string, unknown>
): Promise<{ event_type: string; automations_triggered: number; run_ids: string[] }> {
  const res = await fetch(`${API}/automation/event`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ type: eventType, payload }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(detailMessage(data) || "Failed to fire event");
  return data;
}
