import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { promptSchema } from "../schemas/promptSchema.js";
import { useSubmitPromptMutation } from "../api/promptApi.js";

const languages = [
    { value: "en", label: "English" },
    { value: "es", label: "Spanish" },
    { value: "fr", label: "French" },
];

function PromptForm({ onResult }) {
    const [submitPrompt, { isLoading, error, reset }] = useSubmitPromptMutation();

    const {
        register,
        handleSubmit,
        formState: { errors, isValid, isDirty },
        control,
    } = useForm({
        resolver: zodResolver(promptSchema),
        mode: "onChange",
        defaultValues: {
            prompt: "",
            targetLanguage: "en",
        },
    });

    const promptValue = useWatch({ control, name: "prompt" });
    const onSubmit = async (formData) => {
        try {
            console.log("Submitting prompt:", formData);
            const response = await submitPrompt(formData).unwrap();
            console.log("Prompt submitted successfully:", response);
            onResult(response);
        } catch (error) {
            console.error("Error submitting prompt:", error);
            onResult(null);
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
                    onInput={reset}
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

            {error && (
                <p className="field-error" role="alert">
                    {error.data?.message || "Unable to submit the prompt. Please try again."}
                </p>
            )}

            <button
                type="submit"
                disabled={!isDirty || !isValid || isLoading}
            >
                {isLoading ? "Submitting..." : "Submit prompt"}
            </button>
        </form>
    );
}

export default PromptForm;
