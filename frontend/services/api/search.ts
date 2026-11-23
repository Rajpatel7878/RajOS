import API from "./client";

export type ResourceType =
  | "tasks"
  | "notes"
  | "documents"
  | "conversations"
  | "memories"
  | "knowledge";

export type SortOption = "relevance" | "newest" | "oldest";

export interface SearchItem {
  id: string;
  resource_id: string;
  resource_type: ResourceType;
  title: string;
  snippet: string;
  url: string | null;
  matched_fields: string[];
  created_at: string | null;
  updated_at: string | null;
  relevance_score: number;
  metadata: Record<string, unknown>;
}

export interface SearchPagination {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ProviderStatus {
  resource_type: ResourceType | string;
  display_name: string;
  status: "ok" | "error" | "disabled" | "skipped";
  result_count: number;
  duration_ms: number;
  error: string | null;
}

export interface SearchResponse {
  query: string;
  items: SearchItem[];
  pagination: SearchPagination;
  filters: {
    resource_types: ResourceType[];
    date_from: string | null;
    date_to: string | null;
    sort: SortOption;
    semantic: boolean;
  };
  providers: ProviderStatus[];
  took_ms: number;
}

export interface SearchSuggestion {
  text: string;
  kind: "history" | "resource";
  resource_type: ResourceType | null;
  resource_id: string | null;
  url: string | null;
}

export interface SearchHistoryItem {
  id: number;
  query: string;
  resource_types: string[];
  result_count: number;
  searched_at: string;
}

export interface SearchFilterOptions {
  resource_types: {
    value: ResourceType;
    label: string;
    available: boolean;
    reason: string | null;
  }[];
  sorts: { value: SortOption; label: string }[];
  semantic_available: boolean;
  max_limit: number;
  max_query_length: number;
}

export interface SearchParams {
  q: string;
  types?: ResourceType[];
  sort?: SortOption;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
  semantic?: boolean;
}

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      return data.detail
        .map((entry: { msg?: string }) => entry?.msg)
        .filter(Boolean)
        .join("; ") || fallback;
    }
  } catch {
    // Ignore malformed error bodies.
  }
  return fallback;
}

export async function searchWorkspace(
  params: SearchParams,
  signal?: AbortSignal
): Promise<SearchResponse> {
  const query = new URLSearchParams();
  query.set("q", params.q);
  if (params.types && params.types.length > 0) query.set("types", params.types.join(","));
  if (params.sort) query.set("sort", params.sort);
  if (params.dateFrom) query.set("date_from", `${params.dateFrom}T00:00:00`);
  if (params.dateTo) query.set("date_to", `${params.dateTo}T23:59:59`);
  if (params.page) query.set("page", String(params.page));
  if (params.limit) query.set("limit", String(params.limit));
  if (params.semantic) query.set("semantic", "true");

  const res = await fetch(`${API}/search?${query.toString()}`, {
    headers: authHeaders(),
    signal,
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await parseError(res, "Search failed"));
  return res.json();
}

export async function getSearchSuggestions(
  q: string,
  limit = 8,
  signal?: AbortSignal
): Promise<SearchSuggestion[]> {
  const query = new URLSearchParams({ q, limit: String(limit) });
  const res = await fetch(`${API}/search/suggestions?${query.toString()}`, {
    headers: authHeaders(),
    signal,
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await parseError(res, "Failed to load suggestions"));
  const data = await res.json();
  return data.suggestions ?? [];
}

export async function getSearchHistory(limit = 8): Promise<SearchHistoryItem[]> {
  const res = await fetch(`${API}/search/history?limit=${limit}`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await parseError(res, "Failed to load search history"));
  const data = await res.json();
  return data.items ?? [];
}

export async function clearSearchHistory(): Promise<number> {
  const res = await fetch(`${API}/search/history`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res, "Failed to clear search history"));
  const data = await res.json();
  return data.cleared ?? 0;
}

export async function getSearchFilterOptions(): Promise<SearchFilterOptions> {
  const res = await fetch(`${API}/search/filters`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await parseError(res, "Failed to load search filters"));
  return res.json();
}
