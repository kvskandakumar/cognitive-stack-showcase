import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const submitPromptRequest = async (payload, signal) => {
  const response = await apiClient.post("/api/prompts", payload, {
    signal,
  });

  return response.data;
};