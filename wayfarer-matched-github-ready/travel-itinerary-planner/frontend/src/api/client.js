const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

const OWNER_KEY_STORAGE = "wanderplan_owner_key";
const OWNER_KEY_HEADER = "X-WanderPlan-Owner-Key";

/**
 * Stable per-browser owner key used until Supabase Auth is added.
 * Sent only to our FastAPI backend — never a Supabase service-role key.
 */
export function getOwnerKey() {
  let key = localStorage.getItem(OWNER_KEY_STORAGE);
  if (!key) {
    key = crypto.randomUUID();
    localStorage.setItem(OWNER_KEY_STORAGE, key);
  }
  return key;
}

function ownerHeaders(extra = {}) {
  return {
    Accept: "application/json",
    [OWNER_KEY_HEADER]: getOwnerKey(),
    ...extra,
  };
}

async function parseJsonSafe(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function errorMessageFromPayload(payload, status) {
  const detail = payload?.detail;
  let message = `Request failed (${status})`;

  if (typeof detail === "string") {
    message = detail;
  } else if (Array.isArray(detail)) {
    message = detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  } else if (detail && typeof detail === "object") {
    message = JSON.stringify(detail);
  }

  return message;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const payload = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(errorMessageFromPayload(payload, response.status));
  }

  if (response.status === 204) {
    return null;
  }

  return payload;
}

/**
 * Call the FastAPI health endpoint.
 */
export async function checkHealth() {
  return request("/health");
}

/**
 * Request an itinerary from the FastAPI backend.
 */
export async function generateItinerary(tripData) {
  return request("/api/itineraries/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(tripData),
  });
}

export async function saveTrip({ preferences, itinerary, title }) {
  return request("/api/trips", {
    method: "POST",
    headers: ownerHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ preferences, itinerary, title }),
  });
}

export async function listTrips() {
  return request("/api/trips", {
    method: "GET",
    headers: ownerHeaders(),
  });
}

export async function getTrip(tripId) {
  return request(`/api/trips/${encodeURIComponent(tripId)}`, {
    method: "GET",
    headers: ownerHeaders(),
  });
}

export async function updateTrip(tripId, updates) {
  return request(`/api/trips/${encodeURIComponent(tripId)}`, {
    method: "PATCH",
    headers: ownerHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(updates),
  });
}

export async function deleteTrip(tripId) {
  return request(`/api/trips/${encodeURIComponent(tripId)}`, {
    method: "DELETE",
    headers: ownerHeaders(),
  });
}

export { API_BASE_URL, OWNER_KEY_HEADER };
export const API_URL = API_BASE_URL;
