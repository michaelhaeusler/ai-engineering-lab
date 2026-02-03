/**
 * Chat Input Component
 * Handles message input with send button and keyboard shortcuts
 */

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Send, Loader2 } from 'lucide-react'
import { UploadedFile } from '@/types'
import { getColorClasses } from '@/utils/theme'

interface ChatInputProps {
  input: string
  setInput: (value: string) => void
  isLoading: boolean
  uploadedFile: UploadedFile | null
  selectedColor: string
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
  onSendMessage: () => void
  onKeyPress: (e: React.KeyboardEvent) => void
}

export const ChatInput = ({
  input,
  setInput,
  isLoading,
  uploadedFile,
  selectedColor,
  textareaRef,
  onSendMessage,
  onKeyPress
}: ChatInputProps) => {
  const colorClasses = getColorClasses(selectedColor)

  return (
    <Card className="p-4 border-0 shadow-lg bg-white/80 backdrop-blur-sm">
      <div className="flex space-x-3">
        <Textarea
          data-testid="chat-input-field"
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={onKeyPress}
          placeholder={uploadedFile ? "Ask a question about your document..." : "Type your message..."}
          className="flex-1 min-h-[60px] max-h-[200px] resize-none border-neutral-200 focus:border-neutral-400 rounded-xl bg-white/50 transition-colors"
          disabled={isLoading}
        />
        <Button
          data-testid="chat-send-button"
          onClick={onSendMessage}
          disabled={!input.trim() || isLoading}
          className={`px-6 py-3 h-auto rounded-xl ${colorClasses.button} text-white transition-all duration-200`}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </div>
    </Card>
  )
}
