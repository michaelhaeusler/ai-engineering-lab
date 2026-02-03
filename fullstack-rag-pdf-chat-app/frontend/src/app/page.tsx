'use client'

/**
 * Main RAG Chat Application Component
 * 
 * This is the primary application component that orchestrates the entire RAG chat experience.
 * It has been refactored from a 950-line monolith into a clean, maintainable architecture
 * using custom hooks for business logic and focused components for UI concerns.
 * 
 * Architecture:
 * - Custom hooks handle complex state management and side effects
 * - UI components are focused and reusable
 * - Business logic is separated from presentation logic
 * - Type safety is enforced throughout the application
 */

import { useState } from 'react'

// Custom hooks for business logic
import { useSettings } from '@/hooks/useSettings'
import { useChat } from '@/hooks/useChat'
import { useFileUpload } from '@/hooks/useFileUpload'

// UI Components
import { ApiKeyInput } from '@/components/ApiKeyInput'
import { Header } from '@/components/Header'
import { FileUploadArea } from '@/components/FileUploadArea'
import { ChatArea } from '@/components/ChatArea'
import { ChatInput } from '@/components/ChatInput'
import { SettingsModal } from '@/components/SettingsModal'
import { ReplaceFileDialog } from '@/components/ReplaceFileDialog'
import { ErrorAlert } from '@/components/ErrorAlert'

/**
 * Main RAG Chat Component
 * 
 * Manages the overall application state and coordinates between different subsystems:
 * - Authentication (API key management)
 * - Settings (model and theme preferences)
 * - File upload and processing
 * - Chat functionality
 * - UI state management
 */
export default function RAGChat() {
  // Authentication state
  const [apiKey, setApiKey] = useState('')
  const [showApiKeyInput, setShowApiKeyInput] = useState(true)

  // UI state
  const [showSettings, setShowSettings] = useState(false)

  // Settings management (model, theme with localStorage persistence)
  const { selectedModel, selectedColor, setSelectedModel, setSelectedColor } = useSettings()

  // Chat functionality (messages, streaming, keyboard shortcuts)
  const {
    messages,
    setMessages,
    input,
    setInput,
    isLoading,
    setIsLoading,
    error: chatError,
    messagesEndRef,
    textareaRef,
    sendMessage
  } = useChat({ apiKey, selectedModel })

  // File upload management (drag & drop, progress, document processing)
  const {
    uploadedFile,
    processingStep,
    showReplaceDialog,
    pendingFile,
    getRootProps,
    getInputProps,
    isDragActive,
    handleReplaceConfirm,
    handleReplaceCancel,
    handleRemoveDocument,
    error: uploadError
  } = useFileUpload({
    apiKey,
    selectedModel,
    setIsLoading,
    setMessages
  })

  // Combine errors from both hooks
  const error = uploadError || chatError

  // Create wrapper functions that include uploadedFile context
  const sendMessageWithFile = () => sendMessage(uploadedFile)

  const handleKeyPressWithFile = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(uploadedFile)
    }
  }

  /**
   * Handle API key submission from the initial screen
   */
  const handleApiKeySubmit = (key: string) => {
    setApiKey(key)
    setShowApiKeyInput(false)
  }

  /**
   * Show the API key input screen if not authenticated
   */
  if (showApiKeyInput) {
    return (
      <ApiKeyInput
        selectedColor={selectedColor}
        onApiKeySubmit={handleApiKeySubmit}
      />
    )
  }

  /**
   * Main application interface
   */
  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Application Header */}
      <Header onSettingsClick={() => setShowSettings(true)} />

      {/* Main Content Area */}
      <div className="max-w-4xl mx-auto p-4 h-[calc(100vh-80px)] flex flex-col">

        {/* File Upload Section */}
        <FileUploadArea
          uploadedFile={uploadedFile}
          processingStep={processingStep}
          selectedColor={selectedColor}
          isDragActive={isDragActive}
          getRootProps={getRootProps}
          getInputProps={getInputProps}
          onRemoveDocument={handleRemoveDocument}
        />

        {/* Error Display */}
        <ErrorAlert error={error} />

        {/* Chat Messages Area */}
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          uploadedFile={uploadedFile}
          selectedColor={selectedColor}
          messagesEndRef={messagesEndRef}
        />

        {/* Message Input */}
        <ChatInput
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          uploadedFile={uploadedFile}
          selectedColor={selectedColor}
          textareaRef={textareaRef}
          onSendMessage={sendMessageWithFile}
          onKeyPress={handleKeyPressWithFile}
        />
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        selectedModel={selectedModel}
        selectedColor={selectedColor}
        onModelChange={setSelectedModel}
        onColorChange={setSelectedColor}
        onClose={() => setShowSettings(false)}
      />

      {/* File Replacement Confirmation Dialog */}
      <ReplaceFileDialog
        isOpen={showReplaceDialog}
        currentFile={uploadedFile}
        pendingFile={pendingFile}
        selectedColor={selectedColor}
        onConfirm={handleReplaceConfirm}
        onCancel={handleReplaceCancel}
      />
    </div>
  )
}