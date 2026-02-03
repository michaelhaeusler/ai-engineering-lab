/**
 * Chat Area Component
 * Displays chat messages with streaming support and empty states
 */

import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MessageCircle, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Message, UploadedFile } from '@/types'
import { getColorClasses } from '@/utils/theme'

interface ChatAreaProps {
  messages: Message[]
  isLoading: boolean
  uploadedFile: UploadedFile | null
  selectedColor: string
  messagesEndRef: React.RefObject<HTMLDivElement | null>
}

export const ChatArea = ({
  messages,
  isLoading,
  uploadedFile,
  selectedColor,
  messagesEndRef
}: ChatAreaProps) => {
  const colorClasses = getColorClasses(selectedColor)

  return (
    <Card className="flex-1 mb-4 border-0 shadow-lg bg-white/80 backdrop-blur-sm overflow-hidden relative">
      <ScrollArea className="h-full relative">
        {/* Top gradient fade - positioned inside ScrollArea */}
        <div className="absolute top-0 left-0 right-0 h-8 bg-gradient-to-b from-white via-white/80 to-transparent pointer-events-none z-10" />

        <div className="p-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              {isLoading ? (
                <>
                  <Loader2 className="w-16 h-16 text-neutral-400 mx-auto mb-4 animate-spin" />
                  <h3 className="text-lg font-medium text-neutral-700 mb-2">
                    Analyzing your document
                  </h3>
                  <p className="text-neutral-500">
                    {uploadedFile
                      ? `We're reading and understanding "${uploadedFile.name}". This takes a moment for thorough analysis.`
                      : 'Preparing your document for analysis...'
                    }
                  </p>
                </>
              ) : (
                <>
                  <MessageCircle className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-neutral-700 mb-2">
                    {uploadedFile ? 'Ask questions about your document' : 'Start a conversation'}
                  </h3>
                  <p className="text-neutral-500">
                    {uploadedFile
                      ? `Your PDF "${uploadedFile.name}" is ready for questions.`
                      : 'Upload a PDF document above to get started, or ask general questions.'
                    }
                  </p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    data-testid={`chat-message-${message.role}`}
                    className={`max-w-[80%] ${message.role === 'user'
                      ? `${colorClasses.userBg} text-white rounded-2xl rounded-br-md px-4 py-3`
                      : `text-neutral-900`
                      }`}>
                    {message.role === 'user' ? (
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    ) : (
                      <div className="prose prose-sm prose-neutral max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div data-testid="chat-loading-indicator" className={`${colorClasses.assistantBg} rounded-2xl rounded-bl-md px-4 py-3`}>
                    <div className="flex items-center space-x-2">
                      <Loader2 className={`w-4 h-4 animate-spin ${colorClasses.loading}`} />
                      <span className={`text-sm ${colorClasses.loadingText}`}>AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom gradient fade - positioned inside ScrollArea */}
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white via-white/80 to-transparent pointer-events-none z-10" />
      </ScrollArea>
    </Card>
  )
}
