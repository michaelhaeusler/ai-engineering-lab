/**
 * Replace File Dialog Component
 * Confirmation dialog when user tries to replace an existing uploaded file
 */

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'
import { UploadedFile } from '@/types'
import { getColorClasses } from '@/utils/theme'

interface ReplaceFileDialogProps {
  isOpen: boolean
  currentFile: UploadedFile | null
  pendingFile: File | null
  selectedColor: string
  onConfirm: () => void
  onCancel: () => void
}

export const ReplaceFileDialog = ({
  isOpen,
  currentFile,
  pendingFile,
  selectedColor,
  onConfirm,
  onCancel
}: ReplaceFileDialogProps) => {
  if (!isOpen || !pendingFile) return null

  const colorClasses = getColorClasses(selectedColor)

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md p-6 shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-orange-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-orange-600" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-900 mb-2">Replace Document?</h3>
          <p className="text-sm text-neutral-600 mb-4">
            This will replace your current document with the new one.
          </p>
          <div className="space-y-2 text-xs text-neutral-500">
            <div className="flex justify-between">
              <span>Current:</span>
              <span className="font-medium">{currentFile?.name}</span>
            </div>
            <div className="flex justify-between">
              <span>New:</span>
              <span className="font-medium">{pendingFile.name}</span>
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <Button
            variant="outline"
            onClick={onCancel}
            className="flex-1 rounded-xl border-neutral-200 hover:bg-neutral-50"
          >
            Keep Current
          </Button>
          <Button
            onClick={onConfirm}
            className={`flex-1 rounded-xl ${colorClasses.button} text-white`}
          >
            Replace
          </Button>
        </div>
      </Card>
    </div>
  )
}
