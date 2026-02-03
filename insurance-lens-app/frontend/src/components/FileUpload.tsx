'use client';

import { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, Sparkles } from 'lucide-react';
import { api } from '@/utils/api';
import type { PolicyUploadResponse, UploadProgress } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onUploadComplete: (result: PolicyUploadResponse) => void;
}

/**
 * FileUpload Component
 * 
 * Apple-like file upload component with drag & drop support and real-time progress feedback.
 * Features smooth animations, proper error handling, and beautiful visual feedback.
 */
export default function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [progress, setProgress] = useState<UploadProgress>({
    stage: 'uploading',
    progress: 0,
    message: 'Bereit zum Upload...'
  });
  const [error, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (!file.type.includes('pdf')) {
      setError('Bitte wählen Sie eine PDF-Datei aus.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      setError('Die Datei ist zu groß. Maximum: 50MB');
      return;
    }

    setError(null);
    setUploading(true);
    setSelectedFileName(file.name);

    try {
      // Phase 1: Upload
      setProgress({
        stage: 'uploading',
        progress: 0,
        message: 'Wird hochgeladen...'
      });

      const result = await api.uploadPolicy(file, (uploadProgress) => {
        if (uploadProgress < 100) {
          // Phase 1: Uploading file
          setProgress({
            stage: 'uploading',
            progress: uploadProgress,
            message: `Hochladen: ${Math.round(uploadProgress)}%`
          });
        } else {
          // Phase 2: Upload complete, now processing on backend
          setProgress({
            stage: 'processing',
            progress: 100,
            message: 'KI analysiert Ihre Police...'
          });
        }
      });

      // Phase 3: Complete
      setProgress({
        stage: 'complete',
        progress: 100,
        message: 'Analyse abgeschlossen!'
      });

      // Brief pause to show completion message
      await new Promise(resolve => setTimeout(resolve, 1000));

      onUploadComplete(result);

    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Upload fehlgeschlagen';
      setError(errorMessage);
      setProgress({
        stage: 'uploading',
        progress: 0,
        message: 'Bereit zum Upload...'
      });
      setSelectedFileName(null);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  // Get stage-specific styling and content
  const getStageIcon = () => {
    if (uploading) {
      if (progress.stage === 'complete') {
        return <CheckCircle className="w-16 h-16 text-green-500 animate-in zoom-in duration-300" />;
      }
      if (progress.stage === 'processing') {
        return (
          <div className="relative">
            <Sparkles className="w-16 h-16 text-gray-600 animate-pulse" />
            <div className="absolute inset-0 blur-xl bg-gray-600/20 animate-pulse" />
          </div>
        );
      }
      return <Loader2 className="w-16 h-16 text-gray-600 animate-spin" />;
    }
    if (error) {
      return <AlertCircle className="w-16 h-16 text-red-500 animate-in zoom-in duration-300" />;
    }
    if (dragActive) {
      return <Upload className="w-16 h-16 text-gray-600 animate-bounce" />;
    }
    return <FileText className="w-16 h-16 text-gray-400" />;
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <Card
        className={cn(
          "relative overflow-hidden border-2 transition-all duration-300",
          dragActive && "border-gray-400 bg-gray-50/50 scale-[1.02] shadow-xl",
          error && "border-red-300 bg-red-50/50",
          !dragActive && !error && "border-dashed hover:border-gray-400 hover:shadow-lg"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CardContent className="p-12">
          {uploading ? (
            // Upload in progress
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="flex justify-center">
                {getStageIcon()}
              </div>

              {selectedFileName && (
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    {selectedFileName}
                  </p>
                </div>
              )}

              <div className="space-y-3">
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">
                    {progress.message}
                  </p>
                  {progress.stage === 'processing' && (
                    <p className="text-sm text-gray-600 mt-2">
                      Highlights werden identifiziert...
                    </p>
                  )}
                </div>
                <Progress value={progress.progress} className="h-3" />
                <p className="text-center text-sm text-gray-600">
                  {Math.round(progress.progress)}%
                </p>
              </div>
            </div>
          ) : (
            // Ready for upload
            <div className="space-y-6">
              <div className="flex justify-center">
                {getStageIcon()}
              </div>

              <div className="text-center space-y-2">
                <h3 className="text-xl font-semibold text-gray-900">
                  {dragActive ? 'Lassen Sie die Datei los' : 'Police hochladen'}
                </h3>
                <p className="text-gray-600">
                  {dragActive
                    ? 'Datei hier ablegen...'
                    : 'Ziehen Sie Ihre PDF-Datei hierher oder wählen Sie sie aus'
                  }
                </p>
              </div>

              {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-200 animate-in slide-in-from-top duration-300">
                  <p className="text-red-800 text-sm font-medium text-center">{error}</p>
                </div>
              )}

              <div className="flex justify-center">
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                  data-testid="file-upload-input"
                  disabled={uploading}
                />
                <label htmlFor="file-upload">
                  <Button
                    size="lg"
                    className="cursor-pointer"
                    asChild
                    data-testid="file-upload-button"
                  >
                    <span>
                      <Upload className="w-5 h-5" />
                      PDF auswählen
                    </span>
                  </Button>
                </label>
              </div>

              <div className="text-center space-y-1">
                <p className="text-xs text-gray-500">
                  Nur PDF-Dateien, maximal 50 MB
                </p>
                <p className="text-xs text-gray-400">
                  Ihre Daten werden sicher und privat verarbeitet
                </p>
              </div>
            </div>
          )}
        </CardContent>

        {/* Decorative gradient overlay */}
        {dragActive && (
          <div className="absolute inset-0 bg-gray-50/50 pointer-events-none animate-in fade-in duration-300" />
        )}
      </Card>
    </div>
  );
}
