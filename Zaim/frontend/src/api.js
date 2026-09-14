async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(body.detail || "Не удалось выполнить запрос.");
  }

  return body;
}

export function listApplications(status = "") {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/api/applications/${query}`);
}

export function createApplication(payload) {
  return request("/api/applications/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateApplicationStatus(id, nextStatus) {
  return request(`/api/applications/${id}/status/`, {
    method: "PATCH",
    body: JSON.stringify({ status: nextStatus }),
  });
}
