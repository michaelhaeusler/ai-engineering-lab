'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import PolicyTabs from '@/components/PolicyTabs';
import type { PolicyUploadResponse, PolicyOverview, AnswerResponse } from '@/types';
import { api } from '@/utils/api';

interface QuestionAnswer {
  question: string;
  answer: AnswerResponse;
  timestamp: string;
}

export default function Home() {
  const [uploadedPolicy, setUploadedPolicy] = useState<PolicyOverview | null>(null);
  const [questionHistory, setQuestionHistory] = useState<QuestionAnswer[]>([]);
  const [isAsking, setIsAsking] = useState(false);

  const handleUploadComplete = (result: PolicyUploadResponse) => {
    // Convert upload response to policy overview format
    const policyOverview: PolicyOverview = {
      policy_id: result.policy_id,
      filename: result.filename,
      upload_date: new Date().toISOString(),
      total_pages: result.total_pages,
      total_chunks: result.total_chunks,
      highlighted_clauses: result.highlights.map((highlight, index) => {
        const h = highlight as any;
        // Translate category to German
        const categoryTranslations: Record<string, string> = {
          'waiting_period': 'Wartezeit',
          'exclusion': 'Ausschluss',
          'deductible': 'Selbstbeteiligung',
          'coverage_scope': 'Leistungsumfang',
          'claim_process': 'Schadensprozess',
          'cancellation': 'Kündigung',
          'territorial': 'Geltungsbereich',
          'pre_existing': 'Vorerkrankungen',
          'other': 'Sonstiges'
        };
        const germanTitle = categoryTranslations[h.category] || 'Ungewöhnliche Klausel';

        return {
          clause_id: `clause-${index}-${Date.now()}`,
          title: germanTitle,
          text: h.clause_text || '',
          reason: h.reason || '',
          norm_comparison: h.reason || '', // Use reason as norm comparison
          category: h.category || 'other',
          page_number: typeof h.page === 'number' ? h.page : undefined,
        };
      }),
    };

    setUploadedPolicy(policyOverview);
    setQuestionHistory([]); // Clear previous questions
  };

  const handleAskQuestion = async (question: string) => {
    if (!uploadedPolicy || !question.trim()) return;

    setIsAsking(true);
    try {
      const answer = await api.askQuestion(uploadedPolicy.policy_id, question);

      setQuestionHistory(prev => [
        {
          question,
          answer,
          timestamp: new Date().toISOString(),
        },
        ...prev, // Add new question at the top
      ]);
    } catch (error) {
      console.error('Error asking question:', error);
      // TODO: Show error message to user
      alert(`Fehler beim Stellen der Frage: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
    } finally {
      setIsAsking(false);
    }
  };

  const handleStartOver = () => {
    setUploadedPolicy(null);
    setQuestionHistory([]);
  };

  return (
    <div className="space-y-12">
      {!uploadedPolicy ? (
        <div className="text-center space-y-12 animate-in fade-in duration-700">
          <div className="space-y-6">
            <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
              Willkommen bei InsuranceLens
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Laden Sie Ihre deutsche Krankenversicherungs-Police hoch und erhalten Sie
              eine KI-gestützte Analyse mit personalisierten Antworten auf Ihre Fragen.
            </p>
          </div>

          <FileUpload onUploadComplete={handleUploadComplete} />

          <div className="max-w-5xl mx-auto">
            <div className="bg-gray-50 rounded-3xl p-8 border border-gray-200 shadow-sm">
              <h2 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
                Wie InsuranceLens funktioniert
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="space-y-4 text-center">
                  <div className="w-16 h-16 bg-gray-400 rounded-2xl flex items-center justify-center mx-auto shadow-md">
                    <span className="text-white font-bold text-2xl">1</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg">KI-Analyse</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    Ihre Police wird intelligent analysiert und mit Branchenstandards verglichen
                  </p>
                </div>
                <div className="space-y-4 text-center">
                  <div className="w-16 h-16 bg-gray-400 rounded-2xl flex items-center justify-center mx-auto shadow-md">
                    <span className="text-white font-bold text-2xl">2</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg">Highlights</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    Ungewöhnliche Klauseln werden automatisch identifiziert und erklärt
                  </p>
                </div>
                <div className="space-y-4 text-center">
                  <div className="w-16 h-16 bg-gray-400 rounded-2xl flex items-center justify-center mx-auto shadow-md">
                    <span className="text-white font-bold text-2xl">3</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg">Fragen & Antworten</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    Stellen Sie Fragen und erhalten Sie präzise Antworten mit Quellenangaben
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 bg-white rounded-2xl p-6 shadow-sm border">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-1">
                {uploadedPolicy.filename}
              </h1>
              <p className="text-gray-600 flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Hochgeladen am {new Date(uploadedPolicy.upload_date).toLocaleDateString('de-DE', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                })}
              </p>
            </div>
            <button
              onClick={handleStartOver}
              className="px-6 py-3 text-sm font-medium text-gray-700 bg-white border-2 border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all hover:scale-[1.02] active:scale-[0.98]"
              data-testid="start-over-button"
            >
              Neue Police hochladen
            </button>
          </div>

          <PolicyTabs
            policy={uploadedPolicy}
            onAskQuestion={handleAskQuestion}
            questionHistory={questionHistory}
            isAsking={isAsking}
          />
        </div>
      )}
    </div>
  );
}