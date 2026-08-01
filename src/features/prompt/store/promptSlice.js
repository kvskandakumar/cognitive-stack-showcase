import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { submitPromptRequest } from "../api/promptApi";

const initialState = {
  currentRequest: null,
  response: null,
  status: "idle",
  error: null,
};

const normalizeApiError = (error) => {
  if (error.response) {
    return {
      type: "HTTP_ERROR",
      statusCode: error.response.status,
      message:
        error.response.data?.message ||
        "The server could not process the request.",
      errors: error.response.data?.errors || [],
    };
  }

  if (error.code === "ERR_CANCELED") {
    return {
      type: "CANCELLED",
      message: "The request was cancelled.",
      errors: [],
    };
  }

  if (error.request) {
    return {
      type: "NETWORK_ERROR",
      message:
        "Unable to connect to the server. Please check your connection.",
      errors: [],
    };
  }

  return {
    type: "UNKNOWN_ERROR",
    message: error.message || "An unexpected error occurred.",
    errors: [],
  };
};

export const submitPrompt = createAsyncThunk(
  "prompt/submitPrompt",
  async (payload, { rejectWithValue, signal }) => {
    try {
      // submitPromptRequest is a function that makes the API call to submit the prompt.
      return await submitPromptRequest(payload, signal);
    } catch (error) {
      return rejectWithValue(normalizeApiError(error));
    }
  }
);

const promptSlice = createSlice({
  name: "prompt",
  initialState,
  reducers: {
    clearPromptState: () => initialState,
    clearPromptError: (state) => {
      state.error = null;

      if (state.status === "failed") {
        state.status = "idle";
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitPrompt.pending, (state, action) => {
        state.status = "loading";
        state.error = null;
        state.response = null;
        state.currentRequest = action.meta.arg;
      })
      .addCase(submitPrompt.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.response = action.payload;
      })
      .addCase(submitPrompt.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || {
          type: "UNKNOWN_ERROR",
          message: "An unexpected error occurred.",
          errors: [],
        };
      });
  },
});

export const { clearPromptState, clearPromptError } = promptSlice.actions;

export const selectPromptState = (state) => state.prompt;
export const selectPromptStatus = (state) => state.prompt.status;
export const selectPromptResponse = (state) => state.prompt.response;
export const selectPromptError = (state) => state.prompt.error;
export const selectCurrentRequest = (state) => state.prompt.currentRequest;

export default promptSlice.reducer;