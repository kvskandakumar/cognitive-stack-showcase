import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { promptSchema } from "../schemas/promptSchema.js";
import {
  clearPromptError,
  selectPromptStatus,
  submitPrompt,
} from "../store/promptSlice.js";

const languages = [
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
];

function PromptForm() {
  const dispatch = useDispatch();
  const requestStatus = useSelector(selectPromptStatus);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid, isDirty },
    watch,
  } = useForm({
    resolver: zodResolver(promptSchema),
    mode: "onChange",
    defaultValues: {
      prompt: "",
      targetLanguage: "en",
    },
  });

  const promptValue = watch("prompt");
  const isSubmitting = requestStatus === "loading";

  useEffect(() => {
    dispatch(clearPromptError());
  }, [promptValue, dispatch]);

  const onSubmit = async (formData) => {
    try {
      await dispatch(submitPrompt(formData)).unwrap();
    } catch {
      // The structured error is already stored in Redux.
    }
  };

  return (
    <form
      className="prompt-form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
    >
      <div className="form-group">
        <label htmlFor="prompt">Prompt</label>

        <textarea
          id="prompt"
          rows="7"
          placeholder="Enter a detailed prompt..."
          aria-invalid={Boolean(errors.prompt)}
          aria-describedby={errors.prompt ? "prompt-error" : undefined}
          {...register("prompt")}
        />

        <div className="field-footer">
          <div>
            {errors.prompt && (
              <p id="prompt-error" className="field-error" role="alert">
                {errors.prompt.message}
              </p>
            )}
          </div>

          <span>{promptValue.length}/2000</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="targetLanguage">Target language</label>

        <select
          id="targetLanguage"
          aria-invalid={Boolean(errors.targetLanguage)}
          aria-describedby={
            errors.targetLanguage ? "language-error" : undefined
          }
          {...register("targetLanguage")}
        >
          {languages.map((language) => (
            <option key={language.value} value={language.value}>
              {language.label}
            </option>
          ))}
        </select>

        {errors.targetLanguage && (
          <p id="language-error" className="field-error" role="alert">
            {errors.targetLanguage.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={!isDirty || !isValid || isSubmitting}
      >
        {isSubmitting ? "Submitting..." : "Submit prompt"}
      </button>
    </form>
  );
}

export default PromptForm;