/**
 * Theme utility functions for color management
 */

import { ColorClasses } from '@/types'

/**
 * Returns CSS classes for the selected color theme
 * Handles loading state with neutral colors when no color is selected
 */
export const getColorClasses = (color: string): ColorClasses => {
  const colorMap = {
    blue: {
      userBg: 'bg-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700',
      loading: 'text-blue-600',
      loadingText: 'text-blue-700',
      icon: 'text-blue-500 hover:text-blue-700',
      selectedBorder: 'border-blue-300',
      progress: 'bg-blue-600'
    },
    teal: {
      userBg: 'bg-teal-600',
      button: 'bg-teal-600 hover:bg-teal-700',
      loading: 'text-teal-600',
      loadingText: 'text-teal-700',
      icon: 'text-teal-500 hover:text-teal-700',
      selectedBorder: 'border-teal-300',
      progress: 'bg-teal-600'
    },
    purple: {
      userBg: 'bg-purple-600',
      button: 'bg-purple-600 hover:bg-purple-700',
      loading: 'text-purple-600',
      loadingText: 'text-purple-700',
      icon: 'text-purple-500 hover:text-purple-700',
      selectedBorder: 'border-purple-300',
      progress: 'bg-purple-600'
    },
    emerald: {
      userBg: 'bg-emerald-600',
      button: 'bg-emerald-600 hover:bg-emerald-700',
      loading: 'text-emerald-600',
      loadingText: 'text-emerald-700',
      icon: 'text-emerald-500 hover:text-emerald-700',
      selectedBorder: 'border-emerald-300',
      progress: 'bg-emerald-600'
    },
    indigo: {
      userBg: 'bg-indigo-600',
      button: 'bg-indigo-600 hover:bg-indigo-700',
      loading: 'text-indigo-600',
      loadingText: 'text-indigo-700',
      icon: 'text-indigo-500 hover:text-indigo-700',
      selectedBorder: 'border-indigo-300',
      progress: 'bg-indigo-600'
    },
    rose: {
      userBg: 'bg-rose-600',
      button: 'bg-rose-600 hover:bg-rose-700',
      loading: 'text-rose-600',
      loadingText: 'text-rose-700',
      icon: 'text-rose-500 hover:text-rose-700',
      selectedBorder: 'border-rose-300',
      progress: 'bg-rose-600'
    },
    orange: {
      userBg: 'bg-orange-600',
      button: 'bg-orange-600 hover:bg-orange-700',
      loading: 'text-orange-600',
      loadingText: 'text-orange-700',
      icon: 'text-orange-500 hover:text-orange-700',
      selectedBorder: 'border-orange-300',
      progress: 'bg-orange-600'
    },
    amber: {
      userBg: 'bg-amber-600',
      button: 'bg-amber-600 hover:bg-amber-700',
      loading: 'text-amber-600',
      loadingText: 'text-amber-700',
      icon: 'text-amber-500 hover:text-amber-700',
      selectedBorder: 'border-amber-300',
      progress: 'bg-amber-600'
    },
    cyan: {
      userBg: 'bg-cyan-600',
      button: 'bg-cyan-600 hover:bg-cyan-700',
      loading: 'text-cyan-600',
      loadingText: 'text-cyan-700',
      icon: 'text-cyan-500 hover:text-cyan-700',
      selectedBorder: 'border-cyan-300',
      progress: 'bg-cyan-600'
    },
    stone: {
      userBg: 'bg-stone-600',
      button: 'bg-stone-600 hover:bg-stone-700',
      loading: 'text-stone-600',
      loadingText: 'text-stone-700',
      icon: 'text-stone-500 hover:text-stone-700',
      selectedBorder: 'border-stone-300',
      progress: 'bg-stone-600'
    },
    violet: {
      userBg: 'bg-violet-600',
      button: 'bg-violet-600 hover:bg-violet-700',
      loading: 'text-violet-600',
      loadingText: 'text-violet-700',
      icon: 'text-violet-500 hover:text-violet-700',
      selectedBorder: 'border-violet-300',
      progress: 'bg-violet-600'
    },
    red: {
      userBg: 'bg-red-600',
      button: 'bg-red-600 hover:bg-red-700',
      loading: 'text-red-600',
      loadingText: 'text-red-700',
      icon: 'text-red-500 hover:text-red-700',
      selectedBorder: 'border-red-300',
      progress: 'bg-red-600'
    }
  }

  // Handle loading state (empty color) with neutral styles
  if (!color) {
    return {
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
    }
  }

  const selectedColors = colorMap[color as keyof typeof colorMap] || colorMap.emerald

  return {
    ...selectedColors,
    assistantBg: 'bg-gray-50',
    assistantText: 'text-gray-900',
    iconHover: 'hover:bg-gray-100',
    selectedBg: 'bg-gray-100'
  }
}

/**
 * Formats file size from bytes to MB
 */
export const formatFileSize = (bytes: number): string => {
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}
