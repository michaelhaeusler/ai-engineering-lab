/**
 * Custom hook for handling file upload functionality
 * Manages upload state, progress tracking, and document processing
 */

import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadedFile, Message } from '@/types'
import { MAX_PDF_MB } from '@/config/constants'

interface UseFileUploadProps {
  apiKey: string
  selectedModel: string
  setIsLoading: (loading: boolean) => void
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
}

export const useFileUpload = ({
  apiKey,
  selectedModel,
  setIsLoading,
  setMessages
}: UseFileUploadProps) => {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null)
  const [processingStep, setProcessingStep] = useState<string>('')
  const [showReplaceDialog, setShowReplaceDialog] = useState(false)
  const [pendingFile, setPendingFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  /**
   * Main file processing function - handles upload, processing, and summary generation
   */
  const processFileUpload = async (file: File) => {
    const startTime = Date.now()
    console.log(`🚀 Starting document processing for ${file.name} (${formatFileSize(file.size)})`)

    setUploadedFile({
      name: file.name,
      size: file.size,
      uploadProgress: 0,
      status: 'uploading'
    })
    setError(null)
    setIsLoading(true)
    setProcessingStep('Preparing document...')

    try {
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)
      formData.append('apiKey', apiKey)

      console.log('📤 Uploading and processing document...')
      const uploadStart = Date.now()

      // Upload file with real progress tracking using XMLHttpRequest
      const uploadResponse = await new Promise<Response>((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const uploadProgress = Math.round((event.loaded / event.total) * 70) // Upload is 70% of total process
            setUploadedFile(prev => prev ? { ...prev, uploadProgress } : null)

            if (uploadProgress < 25) {
              setProcessingStep('Uploading document...')
            } else if (uploadProgress < 50) {
              setProcessingStep('Processing file...')
            } else {
              setProcessingStep('Analyzing content...')
            }
          }
        })

        // Handle completion
        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const response = new Response(xhr.responseText, {
              status: xhr.status,
              statusText: xhr.statusText,
              headers: new Headers(xhr.getAllResponseHeaders().split('\r\n').reduce((headers, line) => {
                const [key, value] = line.split(': ')
                if (key && value) headers[key] = value
                return headers
              }, {} as Record<string, string>))
            })
            resolve(response)
          } else {
            reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`))
          }
        })

        xhr.addEventListener('error', () => reject(new Error('Network error')))
        xhr.addEventListener('timeout', () => reject(new Error('Request timeout')))

        xhr.open('POST', '/api/upload-pdf-only')
        xhr.send(formData)
      })

      const uploadEnd = Date.now()
      console.log(`✅ Document processing completed in ${uploadEnd - uploadStart}ms`)

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json().catch(() => ({}))
        throw new Error(errorData.error || 'Upload failed')
      }

      await uploadResponse.json() // Process result but don't need to use it

      // Continue from where upload left off (should be around 70%) to 90%
      setProcessingStep('Server processing...')

      // Animate server processing from 70% to 90%
      for (let progress = 70; progress <= 90; progress += 2) {
        setUploadedFile(prev => prev ? { ...prev, uploadProgress: progress } : null)
        if (progress > 85) {
          setProcessingStep('Almost ready...')
        }
        await new Promise(resolve => setTimeout(resolve, 150))
      }

      // Final step to 100%
      setUploadedFile({
        name: file.name,
        size: file.size,
        uploadProgress: 100,
        status: 'uploading' // Keep as uploading to show progress bar
      })
      setProcessingStep('Document processed successfully!')

      // Let the user see the 100% completion for a moment
      await new Promise(resolve => setTimeout(resolve, 1000))

      console.log('🤖 Generating document summary...')
      const summaryStart = Date.now()

      setProcessingStep('Creating summary...')

      // Stream the summary generation
      const summaryResponse = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          developer_message: `You are analyzing a document. Please provide a comprehensive summary in the following format:

# 📄 Document Summary

## Overview
[2-3 sentence overview of what this document is about]

## 🎯 Main Topics
- **Topic 1**: Brief description
- **Topic 2**: Brief description  
- **Topic 3**: Brief description

## 📚 Key Sections
- **Section 1**: Brief description
- **Section 2**: Brief description
- **Section 3**: Brief description

## 💡 Suggested Questions
Based on the content I analyzed, here are specific questions you can ask:
- [Generate 3-4 specific questions that can be answered using the content provided above]
- [Reference actual topics, names, concepts, or data mentioned in the document]
- [Make questions specific enough that they can be answered with the available content]
- [Example: Instead of "How does X work?" use "How does [specific process mentioned] work in [specific context]?"]

---
*Document "${file.name}" has been processed and is ready for questions!*`,
          user_message: 'Please analyze and summarize the uploaded document.',
          model: selectedModel,
          api_key: apiKey
        }),
      })

      if (!summaryResponse.ok) {
        throw new Error('Summary generation failed')
      }

      const reader = summaryResponse.body?.getReader()
      if (!reader) throw new Error('No reader available')

      let summaryContent = ''
      let isFirstChunk = true
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        summaryContent += chunk

        // Add message and hide progress bar as soon as first chunk arrives
        if (isFirstChunk) {
          // Mark file as completed and hide progress bar
          setUploadedFile({
            name: file.name,
            size: file.size,
            uploadProgress: 100,
            status: 'completed'
          })

          const summaryMessage: Message = {
            role: 'assistant',
            content: summaryContent,
            timestamp: Date.now()
          }
          setMessages(prev => [...prev, summaryMessage])
          setIsLoading(false)
          setProcessingStep('')
          isFirstChunk = false
        } else {
          // Update existing message
          setMessages(prev =>
            prev.map((msg, index) =>
              index === prev.length - 1
                ? { ...msg, content: summaryContent }
                : msg
            )
          )
        }
      }

      const summaryEnd = Date.now()
      console.log(`✅ Summary generated in ${summaryEnd - summaryStart}ms`)

      // Clean up processing step
      setProcessingStep('')

      const totalTime = Date.now() - startTime
      console.log(`🎉 Total processing time: ${totalTime}ms (${(totalTime / 1000).toFixed(1)}s)`)

    } catch (error) {
      console.error('❌ Upload error:', error)
      setError(error instanceof Error ? error.message : 'Upload failed')
      setUploadedFile(prev => prev ? { ...prev, status: 'error' } : null)
      setIsLoading(false)
      setProcessingStep('')
    }
  }

  /**
   * Handle file drop - manages replacement dialog for existing files
   */
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]

    // Handle empty file array
    if (!file) {
      return
    }

    if (file.type === 'application/pdf') {
      // Check file size using unified constant
      const maxSize = MAX_PDF_MB * 1024 * 1024
      if (file.size > maxSize) {
        setError(`File is too large. Please upload a PDF smaller than ${MAX_PDF_MB}MB.`)
        return
      }

      // If there's already a file, show replacement confirmation
      if (uploadedFile && uploadedFile.status === 'completed') {
        setPendingFile(file)
        setShowReplaceDialog(true)
      } else {
        processFileUpload(file)
      }
    } else {
      setError('Please upload a PDF file only.')
    }
  }

  /**
   * Confirm file replacement
   */
  const handleReplaceConfirm = () => {
    if (pendingFile) {
      processFileUpload(pendingFile)
    }
    setShowReplaceDialog(false)
    setPendingFile(null)
  }

  /**
   * Cancel file replacement
   */
  const handleReplaceCancel = () => {
    setShowReplaceDialog(false)
    setPendingFile(null)
  }

  /**
   * Remove uploaded document and return to normal chat mode
   */
  const handleRemoveDocument = async () => {
    try {
      setError(null)
      console.log('🗑️ Removing uploaded document...')

      const response = await fetch('/api/clear-document', {
        method: 'POST',
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || 'Failed to clear document')
      }

      // Clear frontend state
      setUploadedFile(null)
      setMessages([])
      setProcessingStep('')

      console.log('✅ Document removed - returned to normal chat mode')

    } catch (error) {
      console.error('❌ Error removing document:', error)
      setError(error instanceof Error ? error.message : 'Failed to remove document')
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    multiple: false
  })

  // Helper function for file size formatting
  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return {
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
    formatFileSize,
    error,
    setError
  }
}
