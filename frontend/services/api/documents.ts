import API from "./client";

function getToken() {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}

export interface DocumentItem {
  id: number;
  user_id: number;
  filename: string;
  title?: string | null;
  content: string;
  mime_type: string;
  file_size: number;
  status: "uploaded" | "processing" | "ready" | "failed" | "archived" | string;
  processed_at?: string | null;
  error_message?: string | null;
  metadata_json?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreate {
  filename: string;
  content: string;
  title?: string;
  mime_type?: string;
}

export interface DocumentUpdate {
  filename?: string;
  title?: string;
  content?: string;
}

export interface SearchHit {
  chunk_id: string;
  document_id: number;
  filename: string;
  heading: string;
  content: string;
  score: number;
}

export interface KnowledgeStats {
  total_documents: number;
  ready_documents: number;
  processing_documents: number;
  failed_documents: number;
  total_chunks: number;
  total_file_size_bytes: number;
}

export async function getDocuments(statusFilter?: string): Promise<DocumentItem[]> {
  const url = `${API}/documents/${statusFilter ? `?status=${statusFilter}` : ""}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch documents");
  return data;
}

export async function getDocument(id: number): Promise<DocumentItem> {
  const res = await fetch(`${API}/documents/${id}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch document");
  return data;
}

export async function uploadDocument(doc: DocumentCreate): Promise<DocumentItem> {
  const res = await fetch(`${API}/documents/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(doc),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to upload document");
  return data;
}

export async function updateDocument(id: number, doc: DocumentUpdate): Promise<DocumentItem> {
  const res = await fetch(`${API}/documents/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(doc),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to update document");
  return data;
}

export async function deleteDocument(id: number) {
  const res = await fetch(`${API}/documents/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to delete document");
  return data;
}

export async function searchKnowledge(query: string, limit = 5): Promise<SearchHit[]> {
  const res = await fetch(`${API}/documents/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ query, limit }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to execute knowledge search");
  return data.results || [];
}

export async function getKnowledgeStats(): Promise<KnowledgeStats> {
  const res = await fetch(`${API}/documents/stats`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch knowledge stats");
  return data;
}
