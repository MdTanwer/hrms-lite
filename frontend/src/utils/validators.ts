import { useState } from 'react';
import { z } from 'zod';

// Generic validation hook
export const useZodForm = <T extends z.ZodObject<any>>(
  schema: T,
  defaultValues: Partial<z.infer<T>> = {}
) => {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [values, setValues] = useState<Partial<z.infer<T>>>(defaultValues);

  const validateField = (name: keyof z.infer<T>, value: any) => {
    try {
      const fieldSchema = schema.shape[name as keyof typeof schema.shape];
      if (fieldSchema) {
        fieldSchema.parse(value);
        setErrors(prev => ({ ...prev, [name]: '' }));
        return true;
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldError = error.issues[0]?.message || 'Invalid value';
        setErrors(prev => ({ ...prev, [name]: fieldError as string }));
        return false;
      }
    }
    return false;
  };

  const validateForm = () => {
    try {
      schema.parse(values);
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.issues.forEach(err => {
          if (err.path.length > 0) {
            const pathKey = err.path[0];
            if (typeof pathKey === 'string') {
              newErrors[pathKey] = err.message;
            }
          }
        });
        setErrors(newErrors);
      }
      return false;
    }
  };

  const setFieldValue = (name: keyof z.infer<T>, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    if (touched[name as string]) {
      validateField(name, value);
    }
  };

  const setFieldTouched = (name: keyof z.infer<T>) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name, values[name]);
  };

  const resetForm = () => {
    setValues(defaultValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    setFieldValue,
    setFieldTouched,
    validateField,
    validateForm,
    resetForm,
    isValid: Object.keys(errors).length === 0,
  };
};

// Common validation patterns
export const validationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[\d\s\-\(\)]+$/,
  employeeId: /^[A-Z]{2,}\d{3,}$/,
  name: /^[a-zA-Z\s]+$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  numeric: /^\d+$/,
  decimal: /^\d+(\.\d{1,2})?$/,
};

// Common validation messages
export const validationMessages = {
  required: 'This field is required',
  email: 'Please enter a valid email address',
  phone: 'Please enter a valid phone number',
  minLength: (min: number) => `Must be at least ${min} characters`,
  maxLength: (max: number) => `Must be less than ${max} characters`,
  min: (min: number) => `Must be at least ${min}`,
  max: (max: number) => `Must be at most ${max}`,
  pattern: 'Please enter a valid format',
};
