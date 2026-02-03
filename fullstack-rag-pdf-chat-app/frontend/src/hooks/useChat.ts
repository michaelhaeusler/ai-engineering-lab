/**
 * Custom hook for managing chat functionality
 * Handles message sending, streaming responses, and chat state
 */

import { useState, useRef, useEffect } from 'react'
import { Message, UploadedFile } from '@/types'

interface UseChatProps {
  apiKey: string
  selectedModel: string
}

export const useChat = ({ apiKey, selectedModel }: UseChatProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  /**
   * Scroll to bottom when messages change
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  /**
   * Send a message to the chat API with streaming response
   */
  const sendMessage = async (uploadedFile?: UploadedFile | null) => {
    if (!input.trim() || isLoading || !apiKey) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          developer_message: uploadedFile
            ? `You are a helpful AI assistant. Answer questions based on the uploaded PDF document: ${uploadedFile.name}. If the answer is not in the document, please say so.`
            : 'You are a helpful AI assistant.',
          user_message: input.trim(),
          model: selectedModel,
          api_key: apiKey
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader available')

      let assistantContent = ''
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: Date.now()
      }

      setMessages(prev => [...prev, assistantMessage])

      let isFirstChunk = true
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        assistantContent += chunk

        // Hide loading indicator as soon as first chunk arrives
        if (isFirstChunk) {
          setIsLoading(false)
          isFirstChunk = false
        }

        setMessages(prev =>
          prev.map((msg, index) =>
            index === prev.length - 1
              ? { ...msg, content: assistantContent }
              : msg
          )
        )
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setError('Failed to send message. Please check your API key and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Handle keyboard shortcuts in chat input
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return {
    messages,
    setMessages,
    input,
    setInput,
    isLoading,
    setIsLoading,
    error,
    setError,
    messagesEndRef,
    textareaRef,
    sendMessage,
    handleKeyPress
  }
}
