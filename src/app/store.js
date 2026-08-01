import { configureStore } from "@reduxjs/toolkit";
import promptReducer from "../features/prompt/store/promptSlice";

export const store = configureStore({
  reducer: {
    prompt: promptReducer,
  },
});