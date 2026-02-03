/**
 * Settings Modal Component
 * Allows users to configure model and color theme preferences
 */

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { X } from 'lucide-react'
import { AVAILABLE_MODELS, AVAILABLE_COLORS } from '@/config/constants'
import { getColorClasses } from '@/utils/theme'

interface SettingsModalProps {
  isOpen: boolean
  selectedModel: string
  selectedColor: string
  onModelChange: (model: string) => void
  onColorChange: (color: string) => void
  onClose: () => void
}

export const SettingsModal = ({
  isOpen,
  selectedModel,
  selectedColor,
  onModelChange,
  onColorChange,
  onClose
}: SettingsModalProps) => {
  if (!isOpen) return null

  const colorClasses = getColorClasses(selectedColor)

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md p-6 shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Settings</h3>
          <button
            data-testid="settings-modal-close-button"
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Language Model</h4>
          <div className="space-y-2">
            {AVAILABLE_MODELS.map((model) => (
              <button
                key={model.id}
                data-testid={`settings-model-${model.id}`}
                onClick={() => onModelChange(model.id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedModel === model.id
                  ? `${colorClasses.selectedBorder} ${colorClasses.selectedBg}`
                  : 'border-gray-200 hover:border-gray-300'
                  }`}
              >
                <div className="font-medium text-gray-900">{model.name}</div>
                <div className="text-sm text-gray-500">{model.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Color Selection */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Theme Color</h4>
          <div className="grid grid-cols-4 gap-2">
            {AVAILABLE_COLORS.map((color) => (
              <button
                key={color.id}
                data-testid={`settings-color-${color.id}`}
                onClick={() => onColorChange(color.id)}
                className={`p-2 rounded-lg border text-center transition-colors ${selectedColor === color.id
                  ? `border-${color.id}-300 bg-gray-100`
                  : 'border-gray-200 hover:border-gray-300'
                  }`}
              >
                <div className="flex justify-center space-x-1 mb-1">
                  <div className={`w-3 h-3 bg-${color.id}-600 rounded`}></div>
                  <div className="w-3 h-3 bg-gray-50 border rounded"></div>
                </div>
                <div className="text-xs font-medium text-gray-700">{color.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Close Button */}
        <Button
          data-testid="settings-modal-done-button"
          onClick={onClose}
          className={`w-full ${colorClasses.button} text-white`}
        >
          Done
        </Button>
      </Card>
    </div>
  )
}
