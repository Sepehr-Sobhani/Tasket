import { AlertCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorProps {
  message: string;
  variant?: "default" | "destructive";
  className?: string;
}

export function Error({ message, variant = "default", className }: ErrorProps) {
  const variants = {
    default: "text-red-600 dark:text-red-400",
    destructive: "text-red-700 dark:text-red-300",
  };

  return (
    <div
      className={cn(
        "flex items-center space-x-2 text-sm",
        variants[variant],
        className
      )}
    >
      <AlertCircle className="h-4 w-4 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
}

interface ErrorCardProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorCard({
  title = "Something went wrong",
  message,
  onRetry,
  className,
}: ErrorCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center",
        className
      )}
    >
      <XCircle className="h-12 w-12 text-red-600 mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-md">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
