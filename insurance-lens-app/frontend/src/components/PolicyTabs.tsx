'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FileText, AlertTriangle, MessageCircle, Loader2, ExternalLink, Sparkles, Clock, CheckCircle } from 'lucide-react';
import type { PolicyOverview, AnswerResponse } from '@/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface QuestionAnswer {
  question: string;
  answer: AnswerResponse;
  timestamp: string;
}

interface PolicyTabsProps {
  policy: PolicyOverview;
  onAskQuestion: (question: string) => void;
  questionHistory: QuestionAnswer[];
  isAsking: boolean;
}

/**
 * PolicyTabs Component
 * 
 * Apple-like tabbed interface for policy overview, highlights, and Q&A.
 * Features smooth animations, beautiful cards, and intuitive navigation.
 */
export default function PolicyTabs({ policy, onAskQuestion, questionHistory, isAsking }: PolicyTabsProps) {
  const [question, setQuestion] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const handleQuickQuestion = (quickQuestion: string) => {
    setActiveTab('questions');
    onAskQuestion(quickQuestion);
  };

  return (
    <div className="w-full">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full justify-start">
          <TabsTrigger value="overview" className="gap-2" data-testid="tab-übersicht">
            <FileText className="w-4 h-4" />
            Übersicht
          </TabsTrigger>
          <TabsTrigger value="highlights" className="gap-2" data-testid="tab-highlights">
            <AlertTriangle className="w-4 h-4" />
            Highlights
          </TabsTrigger>
          <TabsTrigger value="questions" className="gap-2" data-testid="tab-fragen">
            <MessageCircle className="w-4 h-4" />
            Fragen
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-600" />
                Police Information
              </CardTitle>
              <CardDescription>Details zu Ihrer hochgeladenen Versicherungspolice</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-gray-500">Dateiname</dt>
                  <dd className="text-base font-semibold text-gray-900">{policy.filename}</dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-gray-500">Upload-Datum</dt>
                  <dd className="text-base font-semibold text-gray-900">
                    {new Date(policy.upload_date).toLocaleDateString('de-DE', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-gray-500">Seitenzahl</dt>
                  <dd className="text-base font-semibold text-gray-900">{policy.total_pages || 'N/A'}</dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-gray-500">Text-Abschnitte</dt>
                  <dd className="text-base font-semibold text-gray-900">{policy.total_chunks}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-slate-600" />
                Schnellzugriff
              </CardTitle>
              <CardDescription>Häufig gestellte Fragen zu Ihrer Police</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start text-left hover:scale-[1.02] transition-transform"
                  onClick={() => handleQuickQuestion('Was sind meine Wartezeiten?')}
                  data-testid="quick-question-waiting-periods"
                >
                  <div className="flex flex-col items-start gap-1 w-full">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-slate-600" />
                      <span className="font-semibold">Wartezeiten</span>
                    </div>
                    <span className="text-sm text-gray-600">Erfahren Sie mehr über Ihre Wartezeiten</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start text-left hover:scale-[1.02] transition-transform"
                  onClick={() => handleQuickQuestion('Welche Leistungen sind ausgeschlossen?')}
                  data-testid="quick-question-exclusions"
                >
                  <div className="flex flex-col items-start gap-1 w-full">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      <span className="font-semibold">Ausschlüsse</span>
                    </div>
                    <span className="text-sm text-gray-600">Welche Behandlungen sind nicht versichert?</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start text-left hover:scale-[1.02] transition-transform"
                  onClick={() => handleQuickQuestion('Wie hoch ist meine Selbstbeteiligung?')}
                  data-testid="quick-question-deductible"
                >
                  <div className="flex flex-col items-start gap-1 w-full">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">💰</span>
                      <span className="font-semibold">Selbstbeteiligung</span>
                    </div>
                    <span className="text-sm text-gray-600">Ihre Kosten bei Behandlungen</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start text-left hover:scale-[1.02] transition-transform"
                  onClick={() => handleQuickQuestion('Welche Leistungen sind im Ausland versichert?')}
                  data-testid="quick-question-abroad"
                >
                  <div className="flex flex-col items-start gap-1 w-full">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">🌍</span>
                      <span className="font-semibold">Auslandsschutz</span>
                    </div>
                    <span className="text-sm text-gray-600">Versicherungsschutz außerhalb Deutschlands</span>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Highlights Tab */}
        <TabsContent value="highlights" className="space-y-4">
          {policy.highlighted_clauses.length === 0 ? (
            <Card className="border-gray-200">
              <CardContent className="pt-12 pb-12">
                <div className="text-center">
                  <CheckCircle className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium text-gray-900">Keine Auffälligkeiten gefunden</p>
                  <p className="text-sm mt-2 text-gray-600">Ihre Police entspricht den üblichen Branchenstandards.</p>
                  <p className="text-xs mt-3 text-gray-500">
                    Wartezeiten, Ausschlüsse und Selbstbeteiligung liegen im normalen Bereich.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              <Card className="border-gray-300 bg-gray-50/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-900">
                    <AlertTriangle className="w-5 h-5 text-gray-600" />
                    {policy.highlighted_clauses.length} ungewöhnliche {policy.highlighted_clauses.length === 1 ? 'Klausel' : 'Klauseln'} gefunden
                  </CardTitle>
                  <CardDescription className="text-gray-600">
                    Diese Klauseln weichen von typischen Branchenstandards ab.
                  </CardDescription>
                </CardHeader>
              </Card>

              <div className="space-y-4">
                {policy.highlighted_clauses.map((clause, index) => (
                  <Card
                    key={clause.clause_id}
                    className="hover:shadow-lg transition-shadow"
                    data-testid={`highlighted-clause-${clause.clause_id}`}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between gap-4">
                        <CardTitle className="text-lg">{clause.title}</CardTitle>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 whitespace-nowrap">
                          {clause.category}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg leading-relaxed">
                          {clause.text}
                        </p>
                      </div>

                      <div>
                        <h5 className="text-sm font-semibold text-gray-700 mb-2">Warum markiert?</h5>
                        <p className="text-sm text-gray-700 leading-relaxed">{clause.reason}</p>
                      </div>

                      {clause.page_number && (
                        <div className="flex items-center gap-2 text-xs text-gray-500 pt-2 border-t">
                          <FileText className="w-3 h-3" />
                          Seite {clause.page_number} im Original-Dokument
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions" className="space-y-6">
          <Card className="border-slate-200 bg-slate-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-900">
                <MessageCircle className="w-5 h-5" />
                Fragen Sie mich alles!
              </CardTitle>
              <CardDescription className="text-slate-700">
                Stellen Sie spezifische Fragen zu Ihrer Police oder allgemeine Fragen zur Krankenversicherung.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ihre Frage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                id="question"
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all resize-none"
                placeholder="z.B. 'Wie lange sind meine Wartezeiten für Zahnbehandlungen?' oder 'Was bedeutet Selbstbeteiligung?'"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                data-testid="question-input"
                disabled={isAsking}
              />
              <Button
                onClick={() => {
                  if (question.trim()) {
                    onAskQuestion(question);
                    setQuestion('');
                  }
                }}
                disabled={!question.trim() || isAsking}
                size="lg"
                data-testid="ask-question-button"
              >
                {isAsking ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Antwort wird generiert...
                  </>
                ) : (
                  <>
                    <MessageCircle className="w-4 h-4" />
                    Frage stellen
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Question history */}
          {questionHistory.length === 0 ? (
            <Card>
              <CardContent className="pt-12 pb-12">
                <div className="text-center text-gray-500">
                  <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Noch keine Fragen gestellt</p>
                  <p className="text-sm mt-2">Ihr Frageverlauf wird hier angezeigt.</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Frageverlauf
              </h3>
              {questionHistory.map((qa, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6 space-y-4">
                    {/* Question */}
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                        <MessageCircle className="w-5 h-5 text-slate-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 text-xs mb-1">
                          <span className="text-gray-500">
                            {new Date(qa.timestamp).toLocaleString('de-DE', {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          <span className={cn(
                            "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                            qa.answer.question_type === 'policy_specific'
                              ? "bg-gray-900 text-white"
                              : "bg-gray-200 text-gray-700"
                          )}>
                            {qa.answer.question_type === 'policy_specific' ? 'Ihre Police' : 'Allgemein'}
                          </span>
                        </div>
                        <p className="font-semibold text-gray-900">{qa.question}</p>
                      </div>
                    </div>

                    {/* Answer */}
                    <div className="ml-13 space-y-4">
                      <div className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-xl border [&_p]:mb-4 [&_ul]:my-3 [&_ol]:my-3 [&_li]:mb-2 [&_strong]:font-semibold">
                        <ReactMarkdown>{qa.answer.answer}</ReactMarkdown>
                      </div>

                      {/* Citations */}
                      {qa.answer.citations.length > 0 && (
                        <Card className="bg-gray-50 border-gray-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                              <FileText className="w-4 h-4" />
                              Quellen ({qa.answer.citations.length})
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            {qa.answer.citations.map((citation, citationIndex) => (
                              <div key={citationIndex} className="text-sm space-y-1">
                                <div className="font-medium text-gray-900">
                                  {citation.page_number && `Seite ${citation.page_number}`}
                                  {citation.page_number && ' · '}
                                  Relevanz: {(citation.relevance_score * 100).toFixed(0)}%
                                </div>
                                <div className="text-gray-600 italic pl-3 border-l-2 border-gray-300">
                                  &quot;{citation.text_snippet}&quot;
                                </div>
                              </div>
                            ))}
                          </CardContent>
                        </Card>
                      )}

                      {/* Web Sources */}
                      {qa.answer.web_sources.length > 0 && (
                        <Card className="bg-blue-50 border-blue-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2 text-blue-900">
                              <ExternalLink className="w-4 h-4" />
                              Web-Quellen ({qa.answer.web_sources.length})
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-2">
                            {qa.answer.web_sources.map((source, sourceIndex) => (
                              <a
                                key={sourceIndex}
                                href={source}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-2 hover:underline"
                              >
                                <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                <span className="truncate">{source}</span>
                              </a>
                            ))}
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
