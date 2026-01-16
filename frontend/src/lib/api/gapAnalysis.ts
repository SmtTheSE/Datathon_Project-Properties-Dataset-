// API Client for Product 2: Demand-Supply Gap Analysis

const API_BASE_URL = process.env.NEXT_PUBLIC_API_GAP_URL || 'http://localhost:5002';

export interface GapAnalysisRequest {
  city: string;
  area_locality: string;
  bhk: string;
  avg_rent: number;
  economic_indicators?: {
    inflation_rate?: number;
    interest_rate?: number;
    employment_rate?: number;
    covid_impact_score?: number;
    economic_health_score?: number;
  };
}

export interface GapAnalysisResponse {
  predicted_gap_ratio: number;
  gap_severity: string;
  recommendation: string;
}

export interface BatchGapRequest {
  requests: GapAnalysisRequest[];
}

export interface BatchGapResponse {
  predictions: GapAnalysisResponse[];
}

export async function analyzeGap(
  request: GapAnalysisRequest
): Promise<GapAnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to analyze gap');
    }

    return await response.json();
  } catch (error) {
    console.error('Error analyzing gap:', error);
    throw error;
  }
}

export async function analyzeGapBatch(
  request: BatchGapRequest
): Promise<BatchGapResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/predict/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to analyze batch gaps');
    }

    return await response.json();
  } catch (error) {
    console.error('Error analyzing batch gaps:', error);
    throw error;
  }
}

export async function getSupportedCities(): Promise<{ cities: string[] }> {
  try {
    const response = await fetch(`${API_BASE_URL}/cities`);

    if (!response.ok) {
      throw new Error('Failed to fetch supported cities');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching cities:', error);
    throw error;
  }
}

export async function getModelInfo(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/model/info`);

    if (!response.ok) {
      throw new Error('Failed to fetch model info');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching model info:', error);
    throw error;
  }
}

export async function checkHealth(): Promise<{ status: string; model_loaded: boolean; features_loaded: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
}
