import client from "./client";

export interface Alert {
  alert_id: string;
  watch_id: string;
  user_id: string;
  post_id: string;
  post_url: string;
  title: string;
  verdict: "worth_checking" | "needs_checking";
  extracted_fields: Record<string, unknown>;
  summary: string;
  is_read: boolean;
  created_at: string;
}

export const alertsApi = {
  list: (watchId?: string) =>
    client
      .get<Alert[]>("/alerts", { params: watchId ? { watch_id: watchId } : {} })
      .then((r) => r.data),

  get: (alertId: string) =>
    client.get<Alert>(`/alerts/${alertId}`).then((r) => r.data),

  markAsRead: (alertId: string) => client.patch(`/alerts/${alertId}/read`),

  delete: (alertId: string) => client.delete(`/alerts/${alertId}`),
};
