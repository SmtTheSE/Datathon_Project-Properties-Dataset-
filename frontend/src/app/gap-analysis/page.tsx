'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, MapPin, Home, TrendingUp, AlertCircle, CheckCircle, DollarSign } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { analyzeGap, getSupportedCities, type GapAnalysisRequest } from '@/lib/api/gapAnalysis';

const BHK_OPTIONS = ['1', '2', '3', '4', '5+'];

export default function GapAnalysis() {
  const [selectedCity, setSelectedCity] = useState('Mumbai');
  const [selectedLocality, setSelectedLocality] = useState('Bandra');
  const [selectedBHK, setSelectedBHK] = useState('2');
  const [avgRent, setAvgRent] = useState(35000);
  const [cities, setCities] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [gapResult, setGapResult] = useState<any>(null);
  const [heatMapData, setHeatMapData] = useState<any[]>([]);

  useEffect(() => {
    loadCities();
  }, []);

  useEffect(() => {
    fetchLocalityData(selectedCity);
  }, [selectedCity]);


  const loadCities = async () => {
    try {
      const data = await getSupportedCities();
      setCities(data.cities);
    } catch (error) {
      console.error('Error loading cities:', error);
      setCities(['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune']);
    }
  };

  const fetchLocalityData = async (city: string) => {
    try {
      const response = await fetch(`http://localhost:5002/historical/${city}?top_n=6`);
      const data = await response.json();

      if (data.locality_data && data.locality_data.length > 0) {
        setHeatMapData(data.locality_data);
      } else {
        // Fallback to empty data if no data found
        setHeatMapData([]);
      }
    } catch (error) {
      console.error('Error fetching locality data:', error);
      // Fallback to empty data on error
      setHeatMapData([]);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const request: GapAnalysisRequest = {
        city: selectedCity,
        area_locality: selectedLocality,
        bhk: selectedBHK,
        avg_rent: avgRent,
        economic_indicators: {
          inflation_rate: 6.0,
          interest_rate: 7.0,
          employment_rate: 85.0,
          covid_impact_score: 0.1,
          economic_health_score: 0.85,
        },
      };
      const result = await analyzeGap(request);
      setGapResult(result);
    } catch (error) {
      console.error('Error analyzing gap:', error);
      setGapResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getGapColor = (gap: number) => {
    if (gap > 0.5) return 'var(--success)';
    if (gap > 0) return 'var(--warning)';
    if (gap > -0.5) return 'var(--info)';
    return 'var(--error)';
  };

  const getSeverityIcon = (severity: string) => {
    if (severity.includes('High Demand')) return <TrendingUp className="h-6 w-6 text-green-600" />;
    if (severity.includes('Balanced')) return <CheckCircle className="h-6 w-6 text-blue-600" />;
    return <AlertCircle className="h-6 w-6 text-orange-600" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-purple-50 mandala-bg">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white/90 backdrop-blur-sm shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-8 sm:px-8 lg:px-12">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl gradient-product-2 shadow-lg">
              <Target className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-[var(--dark)]">Gap Analysis</h1>
              <p className="text-base text-gray-600 mt-1">Identify high-potential investment opportunities</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-12">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Control Panel */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="sticky top-6 space-y-6"
            >
              {/* Location Selection */}
              <div className="rounded-2xl bg-white p-8 shadow-lg border border-gray-100">
                <h3 className="mb-5 flex items-center gap-2 text-lg font-bold text-[var(--dark)]">
                  <MapPin className="h-5 w-5 text-[var(--product-2)]" />
                  Location
                </h3>
                <div className="space-y-5">
                  <div>
                    <label className="mb-2 block text-sm font-semibold text-gray-700">City</label>
                    <select
                      value={selectedCity}
                      onChange={(e) => setSelectedCity(e.target.value)}
                      className="w-full rounded-xl border-2 border-gray-300 px-4 py-3.5 text-gray-700 font-medium transition-all focus:border-[var(--product-2)] focus:outline-none focus:ring-4 focus:ring-[var(--product-2)]/10"
                    >
                      {cities.map((city) => (
                        <option key={city} value={city}>
                          {city}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-semibold text-gray-700">Locality</label>
                    <input
                      type="text"
                      value={selectedLocality}
                      onChange={(e) => setSelectedLocality(e.target.value)}
                      className="w-full rounded-xl border-2 border-gray-300 px-4 py-3.5 text-gray-700 font-medium transition-all focus:border-[var(--product-2)] focus:outline-none focus:ring-4 focus:ring-[var(--product-2)]/10"
                      placeholder="e.g., Bandra"
                    />
                  </div>
                </div>
              </div>

              {/* Property Details */}
              <div className="rounded-2xl bg-white p-8 shadow-lg border border-gray-100">
                <h3 className="mb-5 flex items-center gap-2 text-lg font-bold text-[var(--dark)]">
                  <Home className="h-5 w-5 text-[var(--product-2)]" />
                  Property Details
                </h3>
                <div className="space-y-6">
                  <div>
                    <label className="mb-3 block text-sm font-semibold text-gray-700">BHK Type</label>
                    <div className="grid grid-cols-5 gap-2">
                      {BHK_OPTIONS.map((bhk) => (
                        <button
                          key={bhk}
                          onClick={() => setSelectedBHK(bhk)}
                          className={`rounded-xl border-2 py-3 text-sm font-bold transition-all ${selectedBHK === bhk
                            ? 'border-[var(--product-2)] bg-[var(--product-2)] text-white shadow-md scale-105'
                            : 'border-gray-300 text-gray-700 hover:border-[var(--product-2)] hover:bg-gray-50'
                            }`}
                        >
                          {bhk}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="mb-3 block text-sm font-semibold text-gray-700">
                      Average Rent: <span className="text-[var(--product-2)]">₹{avgRent.toLocaleString()}</span>
                    </label>
                    <input
                      type="range"
                      min="5000"
                      max="100000"
                      step="1000"
                      value={avgRent}
                      onChange={(e) => setAvgRent(parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[var(--product-2)]"
                    />
                  </div>
                </div>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-2xl gradient-product-2 px-6 py-5 text-lg font-bold text-white shadow-xl transition-all hover:shadow-2xl hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <>
                    <Target className="h-5 w-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Target className="h-5 w-5" />
                    Analyze Gap
                  </>
                )}
              </button>
            </motion.div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            <div className="space-y-6">
              {/* Gap Analysis Result */}
              {gapResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl bg-white p-8 shadow-xl"
                >
                  <div className="mb-6 flex items-center justify-between">
                    <h3 className="text-2xl font-bold text-[var(--dark)]">Analysis Result</h3>
                    {getSeverityIcon(gapResult.gap_severity)}
                  </div>

                  <div className="grid gap-6 sm:grid-cols-3">
                    <div className="rounded-xl bg-gradient-to-br from-cyan-50 to-blue-50 p-6">
                      <div className="mb-2 text-sm font-medium text-gray-600">Gap Ratio</div>
                      <div className="text-3xl font-bold" style={{ color: getGapColor(gapResult.predicted_gap_ratio) }}>
                        {gapResult.predicted_gap_ratio.toFixed(2)}
                      </div>
                    </div>

                    <div className="rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 p-6">
                      <div className="mb-2 text-sm font-medium text-gray-600">Market Status</div>
                      <div className="text-lg font-bold text-[var(--dark)]">{gapResult.gap_severity}</div>
                    </div>

                    <div className="rounded-xl bg-gradient-to-br from-orange-50 to-yellow-50 p-6">
                      <div className="mb-2 text-sm font-medium text-gray-600">ROI Potential</div>
                      <div className="text-3xl font-bold text-green-600">
                        {gapResult.predicted_gap_ratio > 0.5 ? 'High' : gapResult.predicted_gap_ratio > 0 ? 'Medium' : 'Low'}
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 rounded-xl bg-blue-50 p-6">
                    <h4 className="mb-2 flex items-center gap-2 font-bold text-[var(--dark)]">
                      <DollarSign className="h-5 w-5 text-[var(--product-2)]" />
                      Investment Recommendation
                    </h4>
                    <p className="text-gray-700">{gapResult.recommendation}</p>
                  </div>
                </motion.div>
              )}

              {/* Heat Map */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl bg-white p-8 shadow-lg"
              >
                <h3 className="mb-6 text-xl font-bold text-[var(--dark)]">Locality Gap Heat Map</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={heatMapData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="locality" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Legend />
                    <Bar dataKey="gap" name="Gap Ratio" radius={[8, 8, 0, 0]}>
                      {heatMapData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getGapColor(entry.gap)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </motion.div>

              {/* Investment Opportunities */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="grid gap-6 sm:grid-cols-2"
              >
                <div className="rounded-xl border-2 border-green-200 bg-green-50 p-6">
                  <div className="mb-3 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    <h4 className="font-bold text-green-900">High Opportunity</h4>
                  </div>
                  <p className="mb-2 text-sm text-green-800">Bandra, 2 BHK</p>
                  <p className="text-xs text-green-700">Gap Ratio: +0.85 | Expected ROI: 18%</p>
                </div>

                <div className="rounded-xl border-2 border-blue-200 bg-blue-50 p-6">
                  <div className="mb-3 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                    <h4 className="font-bold text-blue-900">Moderate Opportunity</h4>
                  </div>
                  <p className="mb-2 text-sm text-blue-800">Andheri, 3 BHK</p>
                  <p className="text-xs text-blue-700">Gap Ratio: +0.42 | Expected ROI: 12%</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
