import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  helpText?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helpText, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2">
        <label htmlFor={props.id} className="text-sm font-medium text-gray-900">
          {label}
        </label>
        <input
          ref={ref}
          className={`
            w-full px-4 py-2.5 border border-gray-300 rounded-lg
            text-gray-900 placeholder-gray-500
            focus:ring-2 focus:ring-primary-500 focus:border-transparent
            transition-all duration-200
            disabled:bg-gray-50 disabled:cursor-not-allowed
            ${error ? 'border-error ring-1 ring-error' : ''}
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="text-sm text-error">{error}</p>
        )}
        {helpText && !error && (
          <p className="text-sm text-gray-500">{helpText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
