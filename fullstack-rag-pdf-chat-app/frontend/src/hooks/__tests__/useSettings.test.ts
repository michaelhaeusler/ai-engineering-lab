/**
 * Unit tests for useSettings hook
 * Tests localStorage persistence, state management, and edge cases
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSettings } from '../useSettings'

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

// Replace the global localStorage with our mock
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
})

describe('useSettings Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with default values when localStorage is empty', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSettings())

      expect(result.current.selectedModel).toBe('gpt-4o-mini')
      expect(result.current.selectedColor).toBe('emerald')
    })

    it('should load saved values from localStorage', () => {
      mockLocalStorage.getItem
        .mockReturnValueOnce('gpt-4o') // for selectedModel
        .mockReturnValueOnce('purple') // for selectedColor

      const { result } = renderHook(() => useSettings())

      expect(result.current.selectedModel).toBe('gpt-4o')
      expect(result.current.selectedColor).toBe('purple')
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('ragchat-model')
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('ragchat-color')
    })

    it('should handle corrupted localStorage data gracefully', () => {
      // Mock console.error to suppress error output during test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('localStorage corrupted')
      })

      const { result } = renderHook(() => useSettings())

      expect(result.current.selectedModel).toBe('gpt-4o-mini')
      expect(result.current.selectedColor).toBe('emerald')

      consoleSpy.mockRestore()
    })
  })

  describe('Model Selection', () => {
    it('should update selectedModel and persist to localStorage', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedModel('gpt-3.5-turbo')
      })

      expect(result.current.selectedModel).toBe('gpt-3.5-turbo')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('ragchat-model', 'gpt-3.5-turbo')
    })

    it('should handle invalid model gracefully', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedModel('invalid-model' as string)
      })

      expect(result.current.selectedModel).toBe('invalid-model')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('ragchat-model', 'invalid-model')
    })
  })

  describe('Color Selection', () => {
    it('should update selectedColor and persist to localStorage', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedColor('blue')
      })

      expect(result.current.selectedColor).toBe('blue')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('ragchat-color', 'blue')
    })

    it('should handle empty string color', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedColor('')
      })

      expect(result.current.selectedColor).toBe('')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('ragchat-color', '')
    })
  })

  describe('LocalStorage Persistence', () => {
    it('should handle localStorage setItem failures gracefully', () => {
      // Mock console.warn to suppress warning output during test
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

      mockLocalStorage.getItem.mockReturnValue(null)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage full')
      })

      const { result } = renderHook(() => useSettings())

      // Should not throw error
      act(() => {
        result.current.setSelectedModel('gpt-4o')
      })

      expect(result.current.selectedModel).toBe('gpt-4o')

      consoleSpy.mockRestore()
    })

    it('should handle multiple rapid updates correctly', () => {
      // Mock console.warn to suppress warning output during test
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

      mockLocalStorage.getItem.mockReturnValue(null)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage full')
      })

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedModel('gpt-4o')
        result.current.setSelectedColor('red')
        result.current.setSelectedModel('gpt-3.5-turbo')
        result.current.setSelectedColor('green')
      })

      expect(result.current.selectedModel).toBe('gpt-3.5-turbo')
      expect(result.current.selectedColor).toBe('green')

      consoleSpy.mockRestore()
    })
  })

  describe('Edge Cases', () => {
    it('should handle null localStorage values', () => {
      // Mock console.warn to suppress warning output during test
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

      mockLocalStorage.getItem.mockReturnValue(null)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage full')
      })

      const { result } = renderHook(() => useSettings())

      expect(result.current.selectedModel).toBe('gpt-4o-mini')
      expect(result.current.selectedColor).toBe('emerald')

      consoleSpy.mockRestore()
    })

    it('should handle undefined localStorage values', () => {
      // Mock console.warn to suppress warning output during test
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

      mockLocalStorage.getItem.mockReturnValue(undefined)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage full')
      })

      const { result } = renderHook(() => useSettings())

      expect(result.current.selectedModel).toBe('gpt-4o-mini')
      expect(result.current.selectedColor).toBe('emerald')

      consoleSpy.mockRestore()
    })

    it('should handle very long string values', () => {
      // Mock console.warn to suppress warning output during test
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

      const longString = 'a'.repeat(10000)
      mockLocalStorage.getItem.mockReturnValue(null)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage full')
      })

      const { result } = renderHook(() => useSettings())

      act(() => {
        result.current.setSelectedModel(longString as string)
      })

      expect(result.current.selectedModel).toBe(longString)

      consoleSpy.mockRestore()
    })
  })
})