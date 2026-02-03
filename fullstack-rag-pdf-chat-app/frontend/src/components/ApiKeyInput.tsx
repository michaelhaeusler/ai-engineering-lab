/**
 * API Key Input Component
 * Handles the initial API key entry screen before accessing the main app
 */

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageCircle } from 'lucide-react'
import { getColorClasses } from '@/utils/theme'

interface ApiKeyInputProps {
  selectedColor: string
  onApiKeySubmit: (apiKey: string) => void
}

export const ApiKeyInput = ({ selectedColor, onApiKeySubmit }: ApiKeyInputProps) => {
  const [apiKey, setApiKey] = useState('')

  const handleSubmit = () => {
    if (apiKey.trim()) {
      onApiKeySubmit(apiKey.trim())
    }
  }

  const colorClasses = getColorClasses(selectedColor)

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-neutral-600 to-neutral-800 rounded-2xl mx-auto mb-4 flex items-center justify-center">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-semibold text-neutral-900 mb-2">RAG Chat</h1>
          <p className="text-neutral-600 text-sm">Enter your OpenAI API key to continue</p>
        </div>

        <div className="space-y-4">
          <div>
            <input
              data-testid="api-key-input-field"
              type="password"
              placeholder="sk-..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:border-neutral-400 focus:outline-none transition-colors bg-white/50"
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
          </div>

          <Button
            data-testid="api-key-continue-button"
            onClick={handleSubmit}
            disabled={!apiKey.trim()}
            className={`w-full h-12 rounded-xl ${colorClasses.button} text-white font-medium transition-all duration-200`}
          >
            Continue
          </Button>
        </div>
      </Card>
    </div>
  )
}
