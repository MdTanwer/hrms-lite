import { z } from "zod";

/** Single source of truth for employee create/edit form validation. */
export const employeeSchema = z.object({
  employeeId: z
    .string()
    .min(1, "Employee ID is required")
    .regex(
      /^EMP\d{1,6}$/i,
      "Invalid format. Use EMP followed by 1–6 digits (e.g. EMP001)"
    )
    .transform((val) => val.toUpperCase().trim()),

  fullName: z
    .string()
    .min(2, "Full name must be at least 2 characters")
    .max(100, "Full name must be less than 100 characters")
    .transform((val) => val.trim()),

  email: z
    .string()
    .min(1, "Email is required")
    .email("Invalid email address")
    .transform((val) => val.toLowerCase().trim()),

  department: z.enum(
    ["Engineering", "HR", "Sales", "Marketing", "Finance"],
    { message: "Please select a department" }
  ),

  position: z
    .string()
    .max(100, "Position must be less than 100 characters")
    .optional(),
});

export type EmployeeFormValues = z.infer<typeof employeeSchema>;

/** Default form values; keys must match schema (camelCase for form/API). */
export const defaultEmployeeFormValues: EmployeeFormValues = {
  employeeId: "",
  fullName: "",
  email: "",
  department: "Engineering",
  position: "",
};
