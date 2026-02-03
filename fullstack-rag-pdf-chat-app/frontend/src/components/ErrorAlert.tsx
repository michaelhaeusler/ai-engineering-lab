/**
 * Error Alert Component
 * Displays error messages with consistent styling
 */

import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

interface ErrorAlertProps {
  error: string | null
}

export const ErrorAlert = ({ error }: ErrorAlertProps) => {
  if (!error) return null

  return (
    <Alert data-testid="error-alert" className="mb-6 border-red-200 bg-red-50">
      <AlertCircle className="h-4 w-4 text-red-600" />
      <AlertDescription className="text-red-700">{error}</AlertDescription>
    </Alert>
  )
}
