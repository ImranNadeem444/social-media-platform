import React from 'react'

interface AlertProps {
  type: 'error' | 'success' | 'warning' | 'info'
  message: string
  title?: string
  onClose?: () => void
}

export const Alert: React.FC<AlertProps> = ({ type, message, title, onClose }) => {
  const bgColors = {
    error: 'bg-error/10 text-error border-error/20',
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    info: 'bg-primary-500/10 text-primary-700 border-primary-500/20',
  }

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border
        flex items-start justify-between gap-3
        ${bgColors[type]}
      `}
      role="alert"
    >
      <div className="flex-1">
        {title && <p className="text-sm font-medium">{title}</p>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-current hover:opacity-70 transition-opacity"
          aria-label="Close alert"
        >
          ✕
        </button>
      )}
    </div>
  )
}
