import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const PAGE_SIZE = 6;
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || "";

console.log("Configured API base URL:", configuredBaseUrl);

// Gemini credentials and calls belong to the BFF. Never let a mistaken local
// environment value route browser requests directly to Gemini.
const apiBaseUrl = (() => {
  if (
    !configuredBaseUrl ||
    configuredBaseUrl.includes("api.openai.com") ||
    configuredBaseUrl.includes("generativelanguage.googleapis.com")
  ) {
    return "";
  }

  return configuredBaseUrl;
})();

export const promptApi = createApi({
  reducerPath: "promptApi",
  baseQuery: fetchBaseQuery({
    baseUrl: apiBaseUrl,
  }),
  keepUnusedDataFor: 300,
  endpoints: (builder) => ({
    submitPrompt: builder.mutation({
      query: (body) => ({
        url: "/api/prompts",
        method: "POST",
        body,
      }),
    }),
    getInsights: builder.query({
      query: ({ requestId, page = 1, limit = PAGE_SIZE }) => ({
        url: `/api/prompts/${requestId}/insights`,
        params: { page, limit },
      }),
    }),
  }),
});

export const { useSubmitPromptMutation, useGetInsightsQuery } = promptApi;
