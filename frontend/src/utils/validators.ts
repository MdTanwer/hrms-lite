import { z } from "zod";

/**
 * Validate form values with a Zod schema and return errors in Formik shape.
 * Use for Formik's validate prop or manual validation.
 */
export function validateWithZod<T extends z.ZodObject<z.ZodRawShape>>(
  schema: T,
  values: Partial<z.infer<T>>
): Record<string, string> {
  const result = schema.safeParse(values);
  if (result.success) return {};
  const errors: Record<string, string> = {};
  result.error.issues.forEach((issue) => {
    const key = issue.path[0];
    if (typeof key === "string" && !(key in errors)) {
      errors[key] = issue.message;
    }
  });
  return errors;
}

/** Common regex patterns (aligned with backend where applicable). */
export const validationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[\d\s\-()]+$/,
  /** EMP + 1–6 digits, matches employeeSchema */
  employeeId: /^EMP\d{1,6}$/i,
  name: /^[a-zA-Z\s]+$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  numeric: /^\d+$/,
  decimal: /^\d+(\.\d{1,2})?$/,
};

export const validationMessages = {
  required: "This field is required",
  email: "Please enter a valid email address",
  phone: "Please enter a valid phone number",
  minLength: (min: number) => `Must be at least ${min} characters`,
  maxLength: (max: number) => `Must be less than ${max} characters`,
  min: (min: number) => `Must be at least ${min}`,
  max: (max: number) => `Must be at most ${max}`,
  pattern: "Please enter a valid format",
};
