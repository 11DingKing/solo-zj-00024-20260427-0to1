import { auth } from "$lib/stores/auth";
import { get } from "svelte/store";

const API_BASE_URL = "http://localhost:8000/api";

async function fetchWithAuth(url, options = {}) {
  const authState = get(auth);
  let accessToken = authState.accessToken;

  if (!accessToken) {
    accessToken = localStorage.getItem("accessToken");
  }

  const headers = {
    ...options.headers,
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  let response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    try {
      accessToken = await auth.refreshToken();
      headers["Authorization"] = `Bearer ${accessToken}`;
      response = await fetch(url, {
        ...options,
        headers,
      });
    } catch (e) {
      auth.logout();
      throw new Error("Authentication failed");
    }
  }

  return response;
}

export const api = {
  get: async (endpoint) => {
    const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  },

  post: async (endpoint, data, isFormData = false) => {
    const options = {
      method: "POST",
      body: isFormData ? data : JSON.stringify(data),
    };

    if (!isFormData) {
      options.headers = {
        "Content-Type": "application/json",
      };
    }

    const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, options);

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  put: async (endpoint, data) => {
    const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  patch: async (endpoint, data) => {
    const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  delete: async (endpoint) => {
    const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
      method: "DELETE",
    });

    if (!response.ok && response.status !== 204) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.status === 204 ? null : response.json();
  },

  upload: async (endpoint, formData, onProgress) => {
    const authState = get(auth);
    let accessToken = authState.accessToken;

    if (!accessToken) {
      accessToken = localStorage.getItem("accessToken");
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable && onProgress) {
          const percent = (e.loaded / e.total) * 100;
          onProgress(percent);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve(data);
          } catch (e) {
            resolve(xhr.responseText);
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || `HTTP ${xhr.status}`));
          } catch (e) {
            reject(new Error(`HTTP ${xhr.status}`));
          }
        }
      });

      xhr.addEventListener("error", () => {
        reject(new Error("Network error"));
      });

      xhr.open("POST", `${API_BASE_URL}${endpoint}`);

      if (accessToken) {
        xhr.setRequestHeader("Authorization", `Bearer ${accessToken}`);
      }

      xhr.send(formData);
    });
  },
};

export default api;
