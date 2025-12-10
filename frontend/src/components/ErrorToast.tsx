import { colors } from "../constants/colors";
import { AppError } from "../hooks/useErrorHandler";

interface ErrorToastProps {
  error: AppError;
  onClose: (id: string) => void;
}

export default function ErrorToast({ error, onClose }: ErrorToastProps) {
  const bgColor =
    error.type === "error"
      ? colors.errorBg
      : error.type === "warning"
        ? colors.warningBg
        : colors.infoBg;

  const textColor =
    error.type === "error"
      ? colors.errorText
      : error.type === "warning"
        ? colors.warningText
        : colors.infoText;

  return (
    <div
      style={{
        padding: "12px 16px",
        backgroundColor: bgColor,
        color: textColor,
        borderRadius: "4px",
        marginBottom: "10px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontSize: "14px",
        animation: "slideIn 0.3s ease-in-out",
      }}
    >
      <span>{error.message}</span>
      <button
        onClick={() => onClose(error.id || "")}
        style={{
          background: "none",
          border: "none",
          color: "inherit",
          cursor: "pointer",
          fontSize: "18px",
          padding: "0 8px",
        }}
      >
        ×
      </button>
    </div>
  );
}
