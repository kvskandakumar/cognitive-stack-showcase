import { configureStore } from "@reduxjs/toolkit";
import { promptApi } from "../features/prompt/api/promptApi";

export const store = configureStore({
  reducer: {
    [promptApi.reducerPath]: promptApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(promptApi.middleware),
});
