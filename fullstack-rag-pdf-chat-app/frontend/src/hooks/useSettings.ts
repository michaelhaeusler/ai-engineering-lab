/**
 * Custom hook for managing user settings (model, color theme)
 * Handles localStorage persistence and provides reactive state
 */

import { useState, useEffect } from 'react'
import { AVAILABLE_MODELS, AVAILABLE_COLORS, DEFAULT_MODEL, DEFAULT_COLOR, STORAGE_KEYS } from '@/config/constants'

export const useSettings = () => {
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL)
  const [selectedColor, setSelectedColor] = useState('')

  // Load settings from localStorage on component mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const savedModel = localStorage.getItem(STORAGE_KEYS.MODEL)
        const savedColor = localStorage.getItem(STORAGE_KEYS.COLOR)

        if (savedModel && AVAILABLE_MODELS.some(m => m.id === savedModel)) {
          setSelectedModel(savedModel)
        }

        if (savedColor && AVAILABLE_COLORS.some(c => c.id === savedColor)) {
          setSelectedColor(savedColor)
        } else {
          // Set default color only if no saved color exists
          setSelectedColor(DEFAULT_COLOR)
        }
      } catch {
        // Handle localStorage errors gracefully - use defaults
        setSelectedColor(DEFAULT_COLOR)
      }
    }
  }, [])

  // Save model to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEYS.MODEL, selectedModel)
      } catch (error) {
        // Handle localStorage write errors gracefully
        console.warn('Failed to save model to localStorage:', error)
      }
    }
  }, [selectedModel])

  // Save color to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEYS.COLOR, selectedColor)
      } catch (error) {
        // Handle localStorage write errors gracefully
        console.warn('Failed to save color to localStorage:', error)
      }
    }
  }, [selectedColor])

  return {
    selectedModel,
    selectedColor,
    setSelectedModel,
    setSelectedColor
  }
}
