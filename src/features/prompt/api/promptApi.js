import { createApi } from "@reduxjs/toolkit/query/react";

const PAGE_SIZE = 6;

const insightTemplates = [
  ["Audience alignment", "Define the target audience before selecting a response format.", { category: "strategy", priority: "high" }],
  ["Make the outcome measurable", "Add a concrete success metric so the result can be evaluated.", { category: "measurement", priority: "high" }],
  ["Add supporting context", "Include relevant constraints and background information in the request.", { category: "context", priority: "medium" }],
  ["Prefer clear instructions", "Use direct, unambiguous language for each requested task.", { category: "quality", priority: "medium" }],
  ["Separate complex tasks", "Break multi-part work into ordered steps with explicit deliverables.", { category: "workflow", priority: "medium" }],
  ["Specify the output shape", "Describe the expected structure, length, and tone of the response.", { category: "format", priority: "high" }],
  ["Provide an example", "A representative example can remove ambiguity from the requested result.", { category: "context", priority: "low" }],
  ["Identify constraints", "State technical, legal, or business constraints that affect the answer.", { category: "risk", priority: "high" }],
  ["Review assumptions", "Ask the response to call out assumptions that may change its recommendation.", { category: "quality", priority: "medium" }],
  ["Use consistent terminology", "Keep domain terms consistent throughout the prompt and response.", { category: "quality", priority: "low" }],
  ["Request sources", "Ask for references when claims need to be independently verified.", { category: "research", priority: "medium" }],
  ["Plan for iteration", "Reserve a follow-up step to refine the result using stakeholder feedback.", { category: "workflow", priority: "low" }],
  ["Set a decision deadline", "Include the date by which the recommendation must be actionable.", { category: "strategy", priority: "medium" }],
  ["Highlight trade-offs", "Request benefits, risks, and alternatives for each recommendation.", { category: "risk", priority: "high" }],
  ["Tailor the language", "Match vocabulary and detail to the knowledge level of the reader.", { category: "audience", priority: "medium" }],
];

const wait = (ms, signal) =>
  new Promise((resolve, reject) => {
    const timeout = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => {
      clearTimeout(timeout);
      reject(new DOMException("Request cancelled", "AbortError"));
    });
  });

// This mock base query mirrors the backend contract. Replace its body with
// fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_BASE_URL }) in production.
const mockBaseQuery = async ({ url, method = "GET", body, params }, { signal }) => {
  try {
    await wait(450, signal);

    if (url === "/api/prompts" && method === "POST") {
      if (body.prompt.toLowerCase().includes("error")) {
        return { error: { status: 422, data: { message: "The backend rejected the submitted prompt." } } };
      }
      if (body.prompt.toLowerCase().includes("clarify")) {
        return { data: { status: "NEEDS_CLARIFICATION", requestId: crypto.randomUUID(), message: "Please provide the target audience and expected level of detail." } };
      }
      return { data: { status: "SUCCESS", requestId: crypto.randomUUID() } };
    }

    if (url.match(/^\/api\/prompts\/[^/]+\/insights$/)) {
      const page = Math.max(1, Number(params.page) || 1);
      const limit = Number(params.limit) || PAGE_SIZE;
      const start = (page - 1) * limit;
      const insights = insightTemplates.slice(start, start + limit).map(([title, content, metadata], index) => ({
        id: `insight-${start + index + 1}`,
        title,
        content,
        metadata,
      }));
      return {
        data: {
          insights,
          pagination: {
            page,
            pageSize: limit,
            totalItems: insightTemplates.length,
            totalPages: Math.ceil(insightTemplates.length / limit),
            hasNextPage: start + insights.length < insightTemplates.length,
          },
        },
      };
    }

    return { error: { status: 404, data: { message: "Resource not found." } } };
  } catch (error) {
    return { error: { status: "FETCH_ERROR", error: error.message } };
  }
};

export const promptApi = createApi({
  reducerPath: "promptApi",
  baseQuery: mockBaseQuery,
  keepUnusedDataFor: 300,
  endpoints: (builder) => ({
    submitPrompt: builder.mutation({
      query: (body) => ({ url: "/api/prompts", method: "POST", body }),
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
