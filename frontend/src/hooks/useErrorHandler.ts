import { useState, useCallback } from "react";

export interface AppError {
  message: string;
  type: "error" | "warning" | "info";
  id?: string;
}

export const useErrorHandler = () => {
  const [errors, setErrors] = useState<AppError[]>([]);

  const addError = useCallback((error: AppError | string) => {
    const appError: AppError =
      typeof error === "string"
        ? { message: error, type: "error" }
        : error;

    const id = appError.id || Date.now().toString();
    setErrors((prev) => [...prev, { ...appError, id }]);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setErrors((prev) => prev.filter((e) => e.id !== id));
    }, 5000);
  }, []);

  const removeError = useCallback((id: string) => {
    setErrors((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  return { errors, addError, removeError, clearErrors };
};
