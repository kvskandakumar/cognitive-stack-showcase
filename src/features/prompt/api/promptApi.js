import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const PAGE_SIZE = 6;

export const promptApi = createApi({
  reducerPath: "promptApi",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
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
