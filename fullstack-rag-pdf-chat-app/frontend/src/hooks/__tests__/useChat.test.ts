/**
 * Unit tests for useChat hook
 * Tests message handling, streaming responses, and keyboard interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useChat } from '../useChat'
import { UploadedFile } from '@/types'

// Mock fetch for streaming responses
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('useChat Hook', () => {
  const defaultProps = {
    apiKey: 'test-api-key',
    selectedModel: 'gpt-4o-mini',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
  })

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      expect(result.current.messages).toEqual([])
      expect(result.current.input).toBe('')
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.messagesEndRef).toBeDefined()
      expect(result.current.textareaRef).toBeDefined()
      expect(typeof result.current.sendMessage).toBe('function')
      expect(typeof result.current.handleKeyPress).toBe('function')
      expect(typeof result.current.setMessages).toBe('function')
      expect(typeof result.current.setInput).toBe('function')
      expect(typeof result.current.setIsLoading).toBe('function')
      expect(typeof result.current.setError).toBe('function')
    })
  })

  describe('Message Input Handling', () => {
    it('should update input value correctly', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Hello, world!')
      })

      expect(result.current.input).toBe('Hello, world!')
    })

    it('should handle empty input', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('')
      })

      expect(result.current.input).toBe('')
    })

    it('should handle very long input', () => {
      const { result } = renderHook(() => useChat(defaultProps))
      const longInput = 'a'.repeat(10000)

      act(() => {
        result.current.setInput(longInput)
      })

      expect(result.current.input).toBe(longInput)
    })
  })

  describe('Keyboard Interactions', () => {
    it('should send message on Enter key press', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('Hello') })
          .mockResolvedValueOnce({ done: true, value: undefined })
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: { getReader: () => mockReader }
      })

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      const mockEvent = {
        key: 'Enter',
        shiftKey: false,
        preventDefault: vi.fn(),
      } as unknown as React.KeyboardEvent<HTMLTextAreaElement>

      await act(async () => {
        result.current.handleKeyPress(mockEvent)
      })

      expect(mockEvent.preventDefault).toHaveBeenCalled()
      expect(result.current.input).toBe('')
      expect(result.current.messages).toHaveLength(2) // User message + assistant response
    })

    it('should not send message on Shift+Enter', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      const mockEvent = {
        key: 'Enter',
        shiftKey: true,
        preventDefault: vi.fn(),
      } as unknown as React.KeyboardEvent<HTMLTextAreaElement>

      act(() => {
        result.current.handleKeyPress(mockEvent)
      })

      expect(mockEvent.preventDefault).not.toHaveBeenCalled()
      expect(result.current.input).toBe('Test message')
      expect(result.current.messages).toHaveLength(0)
    })

    it('should ignore other key presses', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      const mockEvent = {
        key: 'Escape',
        shiftKey: false,
        preventDefault: vi.fn(),
      } as unknown as React.KeyboardEvent<HTMLTextAreaElement>

      act(() => {
        result.current.handleKeyPress(mockEvent)
      })

      expect(mockEvent.preventDefault).not.toHaveBeenCalled()
      expect(result.current.messages).toHaveLength(0)
    })
  })

  describe('Message Sending', () => {
    it('should not send empty messages', async () => {
      const { result } = renderHook(() => useChat(defaultProps))

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(mockFetch).not.toHaveBeenCalled()
      expect(result.current.messages).toHaveLength(0)
    })

    it('should not send messages when loading', async () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
        result.current.setIsLoading(true)
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('should not send messages without API key', async () => {
      const propsWithoutApiKey = { ...defaultProps, apiKey: '' }
      const { result } = renderHook(() => useChat(propsWithoutApiKey))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(mockFetch).not.toHaveBeenCalled()
      expect(result.current.messages).toHaveLength(0)
    })

    it('should send message successfully with streaming response', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('Hello') })
          .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode(' World') })
          .mockResolvedValueOnce({ done: true, value: undefined })
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: { getReader: () => mockReader }
      })

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(mockFetch).toHaveBeenCalledWith('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          developer_message: 'You are a helpful AI assistant.',
          user_message: 'Test message',
          model: 'gpt-4o-mini',
          api_key: 'test-api-key'
        })
      })

      expect(result.current.messages).toHaveLength(2)
      expect(result.current.messages[0]).toEqual({
        role: 'user',
        content: 'Test message',
        timestamp: expect.any(Number)
      })
      expect(result.current.messages[1]).toEqual({
        role: 'assistant',
        content: 'Hello World',
        timestamp: expect.any(Number)
      })
      expect(result.current.input).toBe('')
      expect(result.current.isLoading).toBe(false)
    })

    it('should send message with uploaded file context', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('Response') })
          .mockResolvedValueOnce({ done: true, value: undefined })
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: { getReader: () => mockReader }
      })

      const uploadedFile: UploadedFile = {
        name: 'test.pdf',
        size: 1000,
        uploadProgress: 100,
        status: 'completed'
      }

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Question about document')
      })

      await act(async () => {
        await result.current.sendMessage(uploadedFile)
      })

      expect(mockFetch).toHaveBeenCalledWith('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          developer_message: 'You are a helpful AI assistant. Answer questions based on the uploaded PDF document: test.pdf. If the answer is not in the document, please say so.',
          user_message: 'Question about document',
          model: 'gpt-4o-mini',
          api_key: 'test-api-key'
        })
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle HTTP errors', async () => {
      // Mock console.error to suppress error output during test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(result.current.error).toBe('Failed to send message. Please check your API key and try again.')
      expect(result.current.isLoading).toBe(false)

      consoleSpy.mockRestore()
    })

    it('should handle network errors', async () => {
      // Mock console.error to suppress error output during test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(result.current.error).toBe('Failed to send message. Please check your API key and try again.')
      expect(result.current.isLoading).toBe(false)

      consoleSpy.mockRestore()
    })

    it('should handle missing reader', async () => {
      // Mock console.error to suppress error output during test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: null
      })

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(result.current.error).toBe('Failed to send message. Please check your API key and try again.')
      expect(result.current.isLoading).toBe(false)

      consoleSpy.mockRestore()
    })

    it('should handle streaming errors', async () => {
      // Mock console.error to suppress error output during test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      const mockReader = {
        read: vi.fn().mockRejectedValueOnce(new Error('Stream error'))
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: { getReader: () => mockReader }
      })

      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setInput('Test message')
      })

      await act(async () => {
        await result.current.sendMessage()
      })

      expect(result.current.error).toBe('Failed to send message. Please check your API key and try again.')
      expect(result.current.isLoading).toBe(false)

      consoleSpy.mockRestore()
    })
  })

  describe('Message Management', () => {
    it('should add messages correctly', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      const testMessage = {
        role: 'user' as const,
        content: 'Test message',
        timestamp: Date.now()
      }

      act(() => {
        result.current.setMessages([testMessage])
      })

      expect(result.current.messages).toEqual([testMessage])
    })

    it('should clear messages', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      const testMessage = {
        role: 'user' as const,
        content: 'Test message',
        timestamp: Date.now()
      }

      act(() => {
        result.current.setMessages([testMessage])
      })

      act(() => {
        result.current.setMessages([])
      })

      expect(result.current.messages).toEqual([])
    })

    it('should handle multiple messages', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      const messages = [
        { role: 'user' as const, content: 'First message', timestamp: Date.now() },
        { role: 'assistant' as const, content: 'First response', timestamp: Date.now() },
        { role: 'user' as const, content: 'Second message', timestamp: Date.now() },
      ]

      act(() => {
        result.current.setMessages(messages)
      })

      expect(result.current.messages).toHaveLength(3)
      expect(result.current.messages).toEqual(messages)
    })
  })

  describe('Loading State', () => {
    it('should manage loading state correctly', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setIsLoading(true)
      })

      expect(result.current.isLoading).toBe(true)

      act(() => {
        result.current.setIsLoading(false)
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Error State', () => {
    it('should manage error state correctly', () => {
      const { result } = renderHook(() => useChat(defaultProps))

      act(() => {
        result.current.setError('Test error')
      })

      expect(result.current.error).toBe('Test error')

      act(() => {
        result.current.setError(null)
      })

      expect(result.current.error).toBeNull()
    })
  })
})
