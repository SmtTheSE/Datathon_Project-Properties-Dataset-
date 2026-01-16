// API Client for Product 1: Rental Demand Forecasting

const API_BASE_URL = process.env.NEXT_PUBLIC_API_DEMAND_URL || 'http://localhost:5001';

export interface DemandForecastRequest {
  city: string;
  date: string;
  economic_factors?: {
    inflation_rate?: number;
    interest_rate?: number;
    employment_rate?: number;
  };
}

export interface DemandForecastResponse {
  city: string;
  date: string;
  predicted_demand: number;
}

export interface BatchDemandRequest {
  requests: DemandForecastRequest[];
}

export interface BatchDemandResponse {
  predictions: DemandForecastResponse[];
}

export interface CityInfo {
  cities: string[];
}

export interface ModelInfo {
  service: string;
  description: string;
  features: string[];
  supported_cities: string;
  data_granularity: string;
  users: string[];
  version: string;
  security_features: string[];
  enhanced: boolean;
  features_used: number;
}

export async function predictDemand(
  request: DemandForecastRequest
): Promise<DemandForecastResponse> {
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
      throw new Error(error.error || 'Failed to fetch demand forecast');
    }

    return await response.json();
  } catch (error) {
    console.error('Error predicting demand:', error);
    throw error;
  }
}

export async function predictDemandBatch(
  request: BatchDemandRequest
): Promise<BatchDemandResponse> {
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
      throw new Error(error.error || 'Failed to fetch batch demand forecast');
    }

    return await response.json();
  } catch (error) {
    console.error('Error predicting batch demand:', error);
    throw error;
  }
}

export async function getSupportedCities(): Promise<CityInfo> {
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

export async function getModelInfo(): Promise<ModelInfo> {
  try {
    const response = await fetch(`${API_BASE_URL}/info`);

    if (!response.ok) {
      throw new Error('Failed to fetch model info');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching model info:', error);
    throw error;
  }
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
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
