/**
 * File Upload Area Component
 * Handles PDF file drag & drop upload with visual feedback
 */

import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Upload, FileText } from 'lucide-react'
import { UploadedFile } from '@/types'
import { getColorClasses, formatFileSize } from '@/utils/theme'
import { MAX_PDF_MB } from '@/config/constants'

interface FileUploadAreaProps {
  uploadedFile: UploadedFile | null
  processingStep: string
  selectedColor: string
  isDragActive: boolean
  getRootProps: () => Record<string, unknown>
  getInputProps: () => Record<string, unknown>
  onRemoveDocument: () => void
}

export const FileUploadArea = ({
  uploadedFile,
  processingStep,
  selectedColor,
  isDragActive,
  getRootProps,
  getInputProps,
  onRemoveDocument
}: FileUploadAreaProps) => {
  const colorClasses = getColorClasses(selectedColor)

  return (
    <>
      {/* File Upload Area - Always Visible */}
      <Card className={`mb-6 border-2 border-dashed ${uploadedFile && uploadedFile.status === 'completed'
        ? 'border-neutral-300 bg-neutral-50/50'
        : 'border-neutral-200 bg-white/50'
        } backdrop-blur-sm hover:border-neutral-400 transition-all duration-200`}>
        <div {...getRootProps()} data-testid="file-upload-area" role="button" className="p-6 text-center cursor-pointer">
          <input {...getInputProps()} />
          {uploadedFile && uploadedFile.status === 'completed' ? (
            <>
              <div className="flex items-center justify-center mb-3">
                <FileText className="w-8 h-8 text-neutral-500 mr-2" />
                <Upload className={`w-6 h-6 ${isDragActive ? 'text-neutral-600' : 'text-neutral-400'}`} />
              </div>
              <p className="text-sm font-medium text-neutral-700 mb-1">
                {isDragActive ? 'Drop new PDF to replace' : 'Upload a different PDF'}
              </p>
              <p className="text-xs text-neutral-500">
                Current: {uploadedFile.name} • {formatFileSize(uploadedFile.size)}
              </p>
              <p className="text-xs text-neutral-400 mt-1">
                Drag and drop or click to replace document
              </p>
            </>
          ) : (
            <>
              <Upload className={`w-10 h-10 mx-auto mb-3 ${isDragActive ? 'text-neutral-600' : 'text-neutral-400'}`} />
              <p className="text-base font-medium text-neutral-700 mb-1">
                {isDragActive ? 'Drop your PDF here' : 'Upload a PDF document'}
              </p>
              <p className="text-sm text-neutral-500">
                Drag and drop or click to select a PDF file
              </p>
              <p className="text-xs text-neutral-400 mt-2">
                Maximum size: {MAX_PDF_MB}MB
              </p>
            </>
          )}
        </div>
      </Card>

      {/* Upload Progress */}
      {uploadedFile && uploadedFile.status === 'uploading' && (
        <Card data-testid="file-upload-progress" className="gap-2 mb-3 p-3 bg-white/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-sm font-medium text-neutral-700">
              Processing {uploadedFile.name}
            </span>
            <span className="text-sm text-neutral-500">{formatFileSize(uploadedFile.size)}</span>
          </div>
          <Progress
            data-testid="file-upload-progress-bar"
            value={uploadedFile.uploadProgress}
            className="h-2"
            indicatorClassName={colorClasses.progress}
          />
          {processingStep && (
            <p data-testid="file-upload-status" className="text-xs text-neutral-400 mt-1.5">
              {processingStep}
            </p>
          )}
        </Card>
      )}

      {/* Uploaded Document Info */}
      {uploadedFile && uploadedFile.status === 'completed' && (
        <Card data-testid="file-uploaded-info" className="gap-2 mb-3 p-3 bg-white/50 backdrop-blur-sm">
          <div className="flex items-center">
            <span data-testid="file-uploaded-name" className="text-sm font-medium text-neutral-700">
              📄 {uploadedFile.name}
            </span>
            <button
              data-testid="file-remove-button"
              onClick={onRemoveDocument}
              className="ml-2 text-neutral-400 hover:text-red-500 transition-colors duration-200 p-1"
              title="Remove document and return to normal chat mode"
            >
              ✕
            </button>
          </div>
        </Card>
      )}
    </>
  )
}
