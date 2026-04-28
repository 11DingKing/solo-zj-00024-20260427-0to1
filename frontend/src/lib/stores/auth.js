import { writable } from "svelte/store";

function createAuthStore() {
  const { subscribe, set, update } = writable({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  });

  const storedAccessToken =
    typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
  const storedRefreshToken =
    typeof window !== "undefined" ? localStorage.getItem("refreshToken") : null;
  const storedUser =
    typeof window !== "undefined" ? localStorage.getItem("user") : null;

  if (storedAccessToken && storedUser) {
    try {
      set({
        user: JSON.parse(storedUser),
        accessToken: storedAccessToken,
        refreshToken: storedRefreshToken,
        isAuthenticated: true,
      });
    } catch (e) {
      console.error("Error parsing stored user:", e);
    }
  }

  return {
    subscribe,

    login: async (username, password) => {
      const response = await fetch("http://localhost:8000/api/token/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const tokens = await response.json();

      const userResponse = await fetch(
        "http://localhost:8000/api/accounts/profile/",
        {
          headers: {
            Authorization: `Bearer ${tokens.access}`,
          },
        },
      );

      if (!userResponse.ok) {
        throw new Error("Failed to get user profile");
      }

      const user = await userResponse.json();

      localStorage.setItem("accessToken", tokens.access);
      localStorage.setItem("refreshToken", tokens.refresh);
      localStorage.setItem("user", JSON.stringify(user));

      set({
        user,
        accessToken: tokens.access,
        refreshToken: tokens.refresh,
        isAuthenticated: true,
      });

      return { user, tokens };
    },

    register: async (userData) => {
      const response = await fetch(
        "http://localhost:8000/api/accounts/register/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        },
      );

      if (!response.ok) {
        let errorMessage = "Registration failed";
        try {
          const error = await response.json();
          if (error.detail) {
            errorMessage = error.detail;
          } else if (error.username) {
            errorMessage = `Username: ${error.username[0]}`;
          } else if (error.email) {
            errorMessage = `Email: ${error.email[0]}`;
          } else if (error.password) {
            errorMessage = `Password: ${error.password[0]}`;
          } else if (typeof error === 'object') {
            const firstKey = Object.keys(error)[0];
            if (firstKey && Array.isArray(error[firstKey])) {
              errorMessage = error[firstKey][0];
            }
          }
        } catch (e) {
          errorMessage = "Registration failed. Please try again.";
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      set({
        user: data.user,
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
      });

      return data;
    },

    logout: () => {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");

      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
      });
    },

    refreshToken: async () => {
      const refreshToken = localStorage.getItem("refreshToken");

      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await fetch("http://localhost:8000/api/token/refresh/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        throw new Error("Token refresh failed");
      }

      const tokens = await response.json();

      localStorage.setItem("accessToken", tokens.access);
      if (tokens.refresh) {
        localStorage.setItem("refreshToken", tokens.refresh);
      }

      update((state) => ({
        ...state,
        accessToken: tokens.access,
        refreshToken: tokens.refresh || state.refreshToken,
      }));

      return tokens.access;
    },

    updateProfile: async (userData) => {
      const accessToken = localStorage.getItem("accessToken");

      const response = await fetch(
        "http://localhost:8000/api/accounts/profile/",
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to update profile");
      }

      const user = await response.json();
      localStorage.setItem("user", JSON.stringify(user));

      update((state) => ({
        ...state,
        user,
      }));

      return user;
    },
  };
}

export const auth = createAuthStore();
