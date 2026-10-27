import { getAccessToken } from "./auth";
import type { components } from "./api-schema";

export type Curriculum = components["schemas"]["CurriculumRead"];
export type Lesson = components["schemas"]["LessonRead"];
export type Me = components["schemas"]["MeRead"];
export type ChatResponse = components["schemas"]["ChatResponse"];

export async function api<T>(path: string, schoolId?: string, body?: unknown): Promise<T> {
  const token = await getAccessToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (schoolId) headers["X-School-ID"] = schoolId;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  let response: Response;
  try {
    response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/v1${path}`,
      {
        method: body === undefined ? "GET" : "POST",
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        cache: "no-store",
      },
    );
  } catch {
    throw new Error("Could not reach the school service. Check that the API is running.");
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Please check your entries and try again.",
    );
  }
  return response.json() as Promise<T>;
}
