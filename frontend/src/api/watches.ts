import client from "./client";

export interface Watch {
  watch_id: string;
  user_id: string;
  source_url: string;
  category: string;
  criteria: Record<string, unknown>;
  baseline_post_ids: string[];
  status: "active" | "paused";
  created_at: string;
  last_scanned_at: string | null;
  note: string;
}

export interface CreateWatchPayload {
  source_url: string;
  category: string;
  criteria: Record<string, unknown>;
  note: string;
}

export const watchesApi = {
  list: () => client.get<Watch[]>("/watches").then((r) => r.data),

  get: (watchId: string) =>
    client.get<Watch>(`/watches/${watchId}`).then((r) => r.data),

  create: (payload: CreateWatchPayload) =>
    client.post<Watch>("/watches", payload).then((r) => r.data),

  delete: (watchId: string) => client.delete(`/watches/${watchId}`),

  scan: (watchId: string) =>
    client.post(`/watches/${watchId}/scan`).then((r) => r.data),

  updateStatus: (watchId: string, status: "active" | "paused") =>
    client.patch(`/watches/${watchId}/status`, { status }).then((r) => r.data),
};
