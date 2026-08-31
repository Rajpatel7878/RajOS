import API from "./client";

function getToken() {
  return localStorage.getItem("token");
}

export interface Note {
  id: number;
  title: string;
  content: string;
  user_id: number;
}

export interface NoteCreate {
  title: string;
  content: string;
}

export async function getNotes(): Promise<Note[]> {
  const res = await fetch(`${API}/notes/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch notes");
  return data;
}

export async function createNote(note: NoteCreate): Promise<Note> {
  const res = await fetch(`${API}/notes/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(note),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to create note");
  return data;
}

export async function deleteNote(noteId: number) {
  const res = await fetch(`${API}/notes/${noteId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to delete note");
  return data;
}
