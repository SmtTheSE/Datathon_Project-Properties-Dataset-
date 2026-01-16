'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, Target, ArrowRight, BarChart3, MapPin } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-orange-50 to-blue-50 mandala-bg">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 pt-24 pb-32 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-white/90 px-5 py-2.5 shadow-lg backdrop-blur-sm border border-gray-200">
              <Sparkles className="h-5 w-5 text-[var(--primary)]" />
              <span className="text-sm font-semibold text-[var(--dark)]">
                AI-Powered Rental Intelligence
              </span>
            </div>

            <h1 className="mb-8 text-5xl font-bold leading-tight text-[var(--dark)] sm:text-6xl lg:text-7xl">
              Transform Your{' '}
              <span className="text-gradient">Rental Property</span>
              <br />
              Investment Strategy
            </h1>

            <p className="mx-auto mb-12 max-w-3xl text-lg leading-relaxed text-gray-600 sm:text-xl">
              Harness the power of advanced AI to forecast demand and identify lucrative opportunities
              in India's dynamic rental market
            </p>

            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center sm:gap-6">
              <Link
                href="/demand-forecasting"
                className="group inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:bg-[var(--primary-dark)] hover:shadow-xl hover:-translate-y-1"
              >
                Explore Demand Forecasting
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>

              <Link
                href="/gap-analysis"
                className="group inline-flex items-center justify-center gap-2 rounded-xl border-2 border-[var(--secondary)] bg-white px-8 py-4 text-lg font-semibold text-[var(--secondary)] shadow-lg transition-all hover:bg-[var(--secondary)] hover:text-white hover:shadow-xl hover:-translate-y-1"
              >
                Discover Gap Analysis
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute top-20 left-10 h-72 w-72 rounded-full bg-[var(--primary)] opacity-10 blur-3xl"></div>
        <div className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-[var(--secondary)] opacity-10 blur-3xl"></div>
      </section>

      {/* AI Products Showcase */}
      <section className="px-6 py-20 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold text-[var(--dark)] sm:text-5xl">
              Our AI-Powered Products
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Two revolutionary tools designed to give you unparalleled insights into the rental market
            </p>
          </motion.div>

          <div className="grid gap-8 lg:grid-cols-2">
            {/* Product 1: Demand Forecasting */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Link href="/demand-forecasting" className="group block h-full">
                <div className="relative h-full overflow-hidden rounded-3xl bg-white p-10 shadow-lg transition-all hover:shadow-2xl hover:-translate-y-2 border border-gray-100">
                  <div className="absolute top-0 right-0 h-40 w-40 rounded-full bg-[var(--product-1)] opacity-10 blur-3xl"></div>

                  <div className="relative flex flex-col h-full">
                    <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl gradient-product-1 shadow-lg">
                      <TrendingUp className="h-8 w-8 text-white" />
                    </div>

                    <h3 className="mb-4 text-3xl font-bold text-[var(--dark)]">
                      Demand Forecasting
                    </h3>

                    <p className="mb-8 text-base leading-relaxed text-gray-600">
                      Predict future rental demand with precision using advanced machine learning algorithms
                      that analyze economic indicators, seasonal trends, and market dynamics.
                    </p>

                    <div className="mb-8 space-y-4 flex-grow">
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-1)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Multi-city demand comparison and forecasting
                        </p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-1)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Economic indicators integration (inflation, interest rates)
                        </p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-1)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Interactive visualizations and trend analysis
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-[var(--product-1)] font-bold text-lg group-hover:gap-3 transition-all">
                      Explore Forecasting
                      <ArrowRight className="h-5 w-5" />
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>

            {/* Product 2: Gap Analysis */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Link href="/gap-analysis" className="group block h-full">
                <div className="relative h-full overflow-hidden rounded-3xl bg-white p-10 shadow-lg transition-all hover:shadow-2xl hover:-translate-y-2 border border-gray-100">
                  <div className="absolute top-0 right-0 h-40 w-40 rounded-full bg-[var(--product-2)] opacity-10 blur-3xl"></div>

                  <div className="relative flex flex-col h-full">
                    <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl gradient-product-2 shadow-lg">
                      <Target className="h-8 w-8 text-white" />
                    </div>

                    <h3 className="mb-4 text-3xl font-bold text-[var(--dark)]">
                      Gap Analysis
                    </h3>

                    <p className="mb-8 text-base leading-relaxed text-gray-600">
                      Identify high-potential investment opportunities by analyzing demand-supply gaps
                      across cities, localities, and property types with AI-powered insights.
                    </p>

                    <div className="mb-8 space-y-4 flex-grow">
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-2)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Heat map visualization of market gaps
                        </p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-2)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Investment opportunity recommendations with ROI calculator
                        </p>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-[var(--product-2)] flex-shrink-0"></div>
                        <p className="text-sm leading-relaxed text-gray-600">
                          Location-based gap severity analysis
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-[var(--product-2)] font-bold text-lg group-hover:gap-3 transition-all">
                      Explore Gap Analysis
                      <ArrowRight className="h-5 w-5" />
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20 bg-white sm:px-8 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold text-[var(--dark)] sm:text-5xl">
              Why Choose Our Platform?
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Built for the Indian market with cutting-edge AI technology
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: BarChart3,
                title: 'Data-Driven Insights',
                description: 'Make informed decisions backed by analysis of 10M+ rental records across 40 Indian cities',
                color: 'var(--primary)',
              },
              {
                icon: MapPin,
                title: 'Hyperlocal Analysis',
                description: 'Get granular insights down to specific localities and property types',
                color: 'var(--secondary)',
              },
              {
                icon: Sparkles,
                title: 'AI-Powered Predictions',
                description: 'Leverage advanced machine learning models trained on comprehensive market data',
                color: 'var(--accent)',
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="rounded-2xl bg-white p-8 border border-gray-100 shadow-md transition-all hover:shadow-xl hover:-translate-y-2"
              >
                <div
                  className="mb-6 inline-flex h-14 w-14 items-center justify-center rounded-xl shadow-lg"
                  style={{ backgroundColor: feature.color }}
                >
                  <feature.icon className="h-7 w-7 text-white" />
                </div>
                <h3 className="mb-3 text-xl font-bold text-[var(--dark)]">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative overflow-hidden rounded-3xl gradient-luxury p-12 text-center shadow-2xl"
          >
            <div className="relative z-10">
              <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl">
                Ready to Transform Your Investment Strategy?
              </h2>
              <p className="mb-8 text-lg text-white/90">
                Join thousands of investors making smarter decisions with AI-powered insights
              </p>
              <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                <Link
                  href="/demand-forecasting"
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-8 py-4 text-lg font-semibold text-[var(--dark)] shadow-lg transition-all hover:shadow-xl hover:-translate-y-1"
                >
                  Get Started Free
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>

            <div className="absolute top-0 left-0 h-full w-full opacity-10">
              <div className="absolute top-10 left-10 h-32 w-32 rounded-full bg-white blur-2xl"></div>
              <div className="absolute bottom-10 right-10 h-40 w-40 rounded-full bg-white blur-2xl"></div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
