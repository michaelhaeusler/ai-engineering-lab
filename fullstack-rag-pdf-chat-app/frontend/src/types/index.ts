/**
 * Shared type definitions for the RAG Chat application
 */

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface UploadedFile {
  name: string
  size: number
  uploadProgress: number
  status: 'uploading' | 'completed' | 'error'
}

export interface Model {
  id: string
  name: string
  description: string
}

export interface ColorTheme {
  id: string
  name: string
  description: string
}

export interface ColorClasses {
  userBg: string
  button: string
  loading: string
  loadingText: string
  icon: string
  selectedBorder: string
  progress: string
  assistantBg: string
  assistantText: string
  iconHover: string
  selectedBg: string
}
