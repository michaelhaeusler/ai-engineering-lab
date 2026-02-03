/**
 * API utilities for InsuranceLens frontend
 */

import type {
  PolicyUploadResponse,
  PolicyOverview,
  QuestionRequest,
  AnswerResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.error || errorMessage;
    } catch (parseError) {
      // If can't parse error, use status text  
      console.warn('Failed to parse error response:', parseError);
      errorMessage = response.statusText || errorMessage;
    }
    throw new ApiError(response.status, errorMessage);
  }

  return response.json();
}

export const api = {
  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    return fetchApi('/health');
  },

  // Policy management
  async uploadPolicy(file: File, onProgress?: (progress: number) => void): Promise<PolicyUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Use XMLHttpRequest for progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch (parseError) {
            console.error('Failed to parse response:', parseError);
            reject(new Error('Failed to parse response'));
          }
        } else {
          reject(new ApiError(xhr.status, xhr.statusText));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error'));
      });

      xhr.open('POST', `${API_BASE_URL}/policies/upload`);
      xhr.send(formData);
    });
  },

  async getPolicyOverview(policyId: string): Promise<PolicyOverview> {
    return fetchApi(`/policies/${policyId}/overview`);
  },

  async listPolicies(): Promise<PolicyOverview[]> {
    return fetchApi('/policies/');
  },

  async deletePolicy(policyId: string): Promise<void> {
    await fetchApi(`/policies/${policyId}`, {
      method: 'DELETE',
    });
  },

  // Question answering
  async askQuestion(policyId: string, question: string): Promise<AnswerResponse> {
    return fetchApi(`/policies/${policyId}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  },

  async getQuestionHistory(policyId: string): Promise<Array<Record<string, unknown>>> {
    // TODO: Implement question history endpoint in backend
    return fetchApi(`/questions/history/${policyId}`);
  },
};

export { ApiError };
