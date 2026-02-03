/**
 * TypeScript type definitions for InsuranceLens frontend
 */

export interface PolicyOverview {
  policy_id: string;
  filename: string;
  upload_date: string;
  total_pages: number;
  total_chunks: number;
  highlighted_clauses: HighlightedClause[];
}

export interface HighlightedClause {
  clause_id: string;
  title: string;
  text: string;
  reason: string;
  norm_comparison: string;
  category: string;
  page_number?: number;
}

export interface Citation {
  chunk_id: string;
  page_number?: number;
  text_snippet: string;
  relevance_score: number;
}

export interface AnswerResponse {
  answer: string;
  question_type: 'policy_specific' | 'general_insurance';
  citations: Citation[];
  web_sources: string[];
  confidence: number;
}

export interface QuestionRequest {
  question: string;
}

export interface PolicyUploadResponse {
  policy_id: string;
  filename: string;
  total_pages: number;
  total_chunks: number;
  highlights: HighlightedClause[];
}

export interface UploadProgress {
  stage: 'uploading' | 'processing' | 'analyzing' | 'complete';
  progress: number;
  message: string;
}
