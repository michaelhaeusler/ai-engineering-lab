/**
 * Unit tests for theme utility functions
 * Tests color class generation and file size formatting
 */

import { describe, it, expect } from 'vitest'
import { getColorClasses, formatFileSize } from '../theme'

describe('Theme Utilities', () => {
  describe('getColorClasses', () => {
    it('should return correct classes for blue theme', () => {
      const result = getColorClasses('blue')

      expect(result).toEqual({
        userBg: 'bg-blue-600',
        button: 'bg-blue-600 hover:bg-blue-700',
        loading: 'text-blue-600',
        loadingText: 'text-blue-700',
        icon: 'text-blue-500 hover:text-blue-700',
        selectedBorder: 'border-blue-300',
        progress: 'bg-blue-600',
        assistantBg: 'bg-gray-50',
        assistantText: 'text-gray-900',
        iconHover: 'hover:bg-gray-100',
        selectedBg: 'bg-gray-100'
      })
    })

    it('should return correct classes for purple theme', () => {
      const result = getColorClasses('purple')

      expect(result.userBg).toBe('bg-purple-600')
      expect(result.button).toBe('bg-purple-600 hover:bg-purple-700')
      expect(result.loading).toBe('text-purple-600')
      expect(result.progress).toBe('bg-purple-600')
    })

    it('should return correct classes for emerald theme', () => {
      const result = getColorClasses('emerald')

      expect(result.userBg).toBe('bg-emerald-600')
      expect(result.button).toBe('bg-emerald-600 hover:bg-emerald-700')
      expect(result.loading).toBe('text-emerald-600')
      expect(result.progress).toBe('bg-emerald-600')
    })

    it('should handle all supported colors', () => {
      const supportedColors = [
        'blue', 'teal', 'purple', 'emerald', 'indigo', 'rose',
        'orange', 'amber', 'cyan', 'stone', 'violet', 'red'
      ]

      supportedColors.forEach(color => {
        const result = getColorClasses(color)

        expect(result.userBg).toContain(`bg-${color}-600`)
        expect(result.button).toContain(`bg-${color}-600`)
        expect(result.button).toContain(`hover:bg-${color}-700`)
        expect(result.loading).toContain(`text-${color}-600`)
        expect(result.progress).toContain(`bg-${color}-600`)

        // Assistant colors should always be gray
        expect(result.assistantBg).toBe('bg-gray-50')
        expect(result.assistantText).toBe('text-gray-900')
      })
    })

    it('should return gray classes for empty color', () => {
      const result = getColorClasses('')

      expect(result).toEqual({
        userBg: 'bg-gray-600',
        button: 'bg-gray-600 hover:bg-gray-700',
        loading: 'text-gray-600',
        loadingText: 'text-gray-700',
        icon: 'text-gray-500 hover:text-gray-700',
        selectedBorder: 'border-gray-300',
        progress: 'bg-gray-600',
        assistantBg: 'bg-gray-50',
        assistantText: 'text-gray-900',
        iconHover: 'hover:bg-gray-100',
        selectedBg: 'bg-gray-100'
      })
    })

    it('should return gray classes for null color', () => {
      const result = getColorClasses(null as unknown as string)

      expect(result.userBg).toBe('bg-gray-600')
      expect(result.button).toBe('bg-gray-600 hover:bg-gray-700')
      expect(result.assistantBg).toBe('bg-gray-50')
    })

    it('should return gray classes for undefined color', () => {
      const result = getColorClasses(undefined as unknown as string)

      expect(result.userBg).toBe('bg-gray-600')
      expect(result.button).toBe('bg-gray-600 hover:bg-gray-700')
      expect(result.assistantBg).toBe('bg-gray-50')
    })

    it('should fallback to emerald for unknown colors', () => {
      const result = getColorClasses('unknown-color')

      expect(result.userBg).toBe('bg-emerald-600')
      expect(result.button).toBe('bg-emerald-600 hover:bg-emerald-700')
      expect(result.loading).toBe('text-emerald-600')
      expect(result.progress).toBe('bg-emerald-600')
    })

    it('should handle special characters in color name', () => {
      const result = getColorClasses('blue@#$%')

      // Should fallback to emerald
      expect(result.userBg).toBe('bg-emerald-600')
      expect(result.button).toBe('bg-emerald-600 hover:bg-emerald-700')
    })

    it('should handle numeric color values', () => {
      const result = getColorClasses('123')

      // Should fallback to emerald
      expect(result.userBg).toBe('bg-emerald-600')
      expect(result.button).toBe('bg-emerald-600 hover:bg-emerald-700')
    })

    it('should handle case sensitivity', () => {
      const upperCaseResult = getColorClasses('BLUE')
      const lowerCaseResult = getColorClasses('blue')

      // Uppercase should fallback to emerald since it's not in the map
      expect(upperCaseResult.userBg).toBe('bg-emerald-600')
      expect(lowerCaseResult.userBg).toBe('bg-blue-600')
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes to MB correctly', () => {
      expect(formatFileSize(1024 * 1024)).toBe('1.00 MB')
      expect(formatFileSize(2 * 1024 * 1024)).toBe('2.00 MB')
      expect(formatFileSize(0.5 * 1024 * 1024)).toBe('0.50 MB')
    })

    it('should handle zero bytes', () => {
      expect(formatFileSize(0)).toBe('0.00 MB')
    })

    it('should handle small file sizes', () => {
      expect(formatFileSize(1024)).toBe('0.00 MB')
      expect(formatFileSize(512 * 1024)).toBe('0.50 MB')
      expect(formatFileSize(256 * 1024)).toBe('0.25 MB')
    })

    it('should handle large file sizes', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1024.00 MB') // 1GB
      expect(formatFileSize(5.5 * 1024 * 1024 * 1024)).toBe('5632.00 MB') // 5.5GB
    })

    it('should handle decimal precision correctly', () => {
      expect(formatFileSize(1536 * 1024)).toBe('1.50 MB') // 1.5MB
      expect(formatFileSize(2560 * 1024)).toBe('2.50 MB') // 2.5MB
      expect(formatFileSize(1024 * 1024 + 512 * 1024)).toBe('1.50 MB') // 1.5MB
    })

    it('should handle very small non-zero values', () => {
      expect(formatFileSize(1)).toBe('0.00 MB')
      expect(formatFileSize(100)).toBe('0.00 MB')
      expect(formatFileSize(1000)).toBe('0.00 MB')
    })

    it('should handle negative values', () => {
      expect(formatFileSize(-1024 * 1024)).toBe('-1.00 MB')
      expect(formatFileSize(-512 * 1024)).toBe('-0.50 MB')
    })

    it('should handle floating point input', () => {
      expect(formatFileSize(1.5 * 1024 * 1024)).toBe('1.50 MB')
      expect(formatFileSize(2.75 * 1024 * 1024)).toBe('2.75 MB')
    })

    it('should handle very large numbers', () => {
      const veryLarge = Number.MAX_SAFE_INTEGER
      const result = formatFileSize(veryLarge)
      expect(result).toMatch(/^\d+\.\d{2} MB$/)
    })

    it('should handle edge case numbers', () => {
      expect(formatFileSize(Infinity)).toBe('Infinity MB')
      expect(formatFileSize(NaN)).toBe('NaN MB')
    })
  })

  describe('Integration Tests', () => {
    it('should work together in a typical usage scenario', () => {
      const color = 'blue'
      const fileSize = 2.5 * 1024 * 1024

      const colorClasses = getColorClasses(color)
      const formattedSize = formatFileSize(fileSize)

      expect(colorClasses.userBg).toBe('bg-blue-600')
      expect(formattedSize).toBe('2.50 MB')
    })

    it('should handle edge cases together', () => {
      const colorClasses = getColorClasses('')
      const formattedSize = formatFileSize(0)

      expect(colorClasses.userBg).toBe('bg-gray-600')
      expect(formattedSize).toBe('0.00 MB')
    })
  })
})
