import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useFileUpload } from '../useFileUpload'

// Mock react-dropzone - focus on business logic, not UI
const mockGetRootProps = vi.fn(() => ({ onClick: vi.fn() }))
const mockGetInputProps = vi.fn(() => ({ type: 'file' }))
let mockOnDrop: (acceptedFiles: File[]) => void = vi.fn()

vi.mock('react-dropzone', () => ({
  useDropzone: vi.fn((config) => {
    mockOnDrop = config.onDrop
    return {
      getRootProps: mockGetRootProps,
      getInputProps: mockGetInputProps,
      isDragActive: false,
    }
  }),
}))

// Mock fetch for simple API testing
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('useFileUpload Hook - Business Logic', () => {
  const mockSetIsLoading = vi.fn()
  const mockSetMessages = vi.fn()
  const defaultProps = {
    apiKey: 'test-api-key',
    selectedModel: 'gpt-4o-mini',
    setIsLoading: mockSetIsLoading,
    setMessages: mockSetMessages
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
  })

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      expect(result.current.uploadedFile).toBeNull()
      expect(result.current.processingStep).toBe('')
      expect(result.current.showReplaceDialog).toBe(false)
      expect(result.current.pendingFile).toBeNull()
      expect(result.current.error).toBeNull()
      expect(result.current.isDragActive).toBe(false)
      expect(typeof result.current.getRootProps).toBe('function')
      expect(typeof result.current.getInputProps).toBe('function')
      expect(typeof result.current.handleReplaceConfirm).toBe('function')
      expect(typeof result.current.handleReplaceCancel).toBe('function')
      expect(typeof result.current.handleRemoveDocument).toBe('function')
    })
  })

  describe('File Validation Logic', () => {
    it('should accept valid PDF files', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))
      const pdfFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      act(() => {
        mockOnDrop([pdfFile])
      })

      // Should start processing (not reject)
      expect(result.current.error).toBeNull()
    })

    it('should reject non-PDF files', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))
      const txtFile = new File(['content'], 'test.txt', { type: 'text/plain' })

      act(() => {
        mockOnDrop([txtFile])
      })

      expect(result.current.error).toBe('Please upload a PDF file only.')
      expect(result.current.uploadedFile).toBeNull()
    })

    it('should handle empty file array gracefully', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      act(() => {
        mockOnDrop([])
      })

      // Should not set any error or state changes
      expect(result.current.error).toBeNull()
      expect(result.current.uploadedFile).toBeNull()
    })
  })

  describe('Replace Dialog Logic', () => {
    it('should not show replace dialog when no file exists', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      const newFile = new File(['new content'], 'new.pdf', { type: 'application/pdf' })

      act(() => {
        mockOnDrop([newFile])
      })

      // Should not show dialog when no existing file
      expect(result.current.showReplaceDialog).toBe(false)
      expect(result.current.pendingFile).toBeNull()
    })

    it('should handle replace confirmation logic', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      // Test that the function exists and can be called without error
      act(() => {
        result.current.handleReplaceConfirm()
      })

      // Should not crash and dialog should remain closed
      expect(result.current.showReplaceDialog).toBe(false)
    })

    it('should handle replace cancellation logic', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      // Test that the function exists and can be called without error
      act(() => {
        result.current.handleReplaceCancel()
      })

      // Should not crash and dialog should remain closed
      expect(result.current.showReplaceDialog).toBe(false)
    })
  })

  describe('Document Removal Logic', () => {
    it('should handle successful document removal', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      const { result } = renderHook(() => useFileUpload(defaultProps))

      await act(async () => {
        await result.current.handleRemoveDocument()
      })

      expect(mockFetch).toHaveBeenCalledWith('/api/clear-document', {
        method: 'POST',
      })
      expect(mockSetMessages).toHaveBeenCalledWith([])
    })

    it('should handle document removal API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Server error' }),
      })

      const { result } = renderHook(() => useFileUpload(defaultProps))

      await act(async () => {
        await result.current.handleRemoveDocument()
      })

      expect(result.current.error).toBe('Server error')
    })

    it('should handle document removal network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useFileUpload(defaultProps))

      await act(async () => {
        await result.current.handleRemoveDocument()
      })

      expect(result.current.error).toBe('Network error')
    })
  })

  describe('Error Handling', () => {
    it('should start with no errors and handle valid files', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      // Should start with no error
      expect(result.current.error).toBeNull()

      const pdfFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      act(() => {
        mockOnDrop([pdfFile])
      })

      // Should still have no error after valid file
      expect(result.current.error).toBeNull()
    })
  })

  describe('Edge Cases', () => {
    it('should handle missing API key gracefully', () => {
      const propsWithoutApiKey = { ...defaultProps, apiKey: '' }
      const { result } = renderHook(() => useFileUpload(propsWithoutApiKey))

      const pdfFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      act(() => {
        mockOnDrop([pdfFile])
      })

      // Should still accept the file (API key validation happens at upload time)
      expect(result.current.error).toBeNull()
    })

    it('should handle files with special characters in name', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))
      const specialFile = new File(['content'], 'file with spaces & symbols!@#.pdf', { type: 'application/pdf' })

      act(() => {
        mockOnDrop([specialFile])
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('Utility Functions', () => {
    it('should format file sizes correctly', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))

      expect(result.current.formatFileSize(0)).toBe('0.00 MB')
      expect(result.current.formatFileSize(1024 * 1024)).toBe('1.00 MB')
      expect(result.current.formatFileSize(2.5 * 1024 * 1024)).toBe('2.50 MB')
      expect(result.current.formatFileSize(1024)).toBe('0.00 MB')
    })

    it('should handle very large file sizes', () => {
      const { result } = renderHook(() => useFileUpload(defaultProps))
      const largeSize = 100 * 1024 * 1024 // 100MB

      expect(result.current.formatFileSize(largeSize)).toBe('100.00 MB')
    })
  })
})