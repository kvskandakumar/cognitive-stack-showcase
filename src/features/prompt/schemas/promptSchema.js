import { z } from "zod";

export const promptSchema = z.object({
  prompt: z
    .string()
    .trim()
    .min(5, "Prompt must contain at least 5 characters")
    .max(2000, "Prompt cannot exceed 2000 characters"),

  targetLanguage: z.enum(["en", "es", "fr"], {
    errorMap: () => ({
      message: "Please select a supported language",
    }),
  }),
});