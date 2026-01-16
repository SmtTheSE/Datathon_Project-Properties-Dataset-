import Link from 'next/link';
import { Github, Linkedin, Mail } from 'lucide-react';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="border-t border-gray-200 bg-white">
            <div className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-12">
                <div className="grid gap-8 md:grid-cols-3">
                    {/* Brand */}
                    <div>
                        <div className="mb-4 flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-luxury shadow-md">
                                <span className="text-xl font-bold text-white">RP</span>
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-[var(--dark)]">Rental Property AI</h3>
                                <p className="text-xs text-gray-600">Investment Intelligence</p>
                            </div>
                        </div>
                        <p className="text-sm text-gray-600">
                            AI-powered rental market analysis for smarter investment decisions across India.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="mb-4 text-sm font-bold text-[var(--dark)] uppercase tracking-wide">
                            Products
                        </h4>
                        <ul className="space-y-2">
                            <li>
                                <Link
                                    href="/demand-forecasting"
                                    className="text-sm text-gray-600 transition-colors hover:text-[var(--primary)]"
                                >
                                    Demand Forecasting
                                </Link>
                            </li>
                            <li>
                                <Link
                                    href="/gap-analysis"
                                    className="text-sm text-gray-600 transition-colors hover:text-[var(--primary)]"
                                >
                                    Gap Analysis
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="mb-4 text-sm font-bold text-[var(--dark)] uppercase tracking-wide">
                            Connect
                        </h4>
                        <div className="flex gap-4">
                            <a
                                href="#"
                                className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-all hover:bg-[var(--primary)] hover:text-white hover:shadow-md"
                                aria-label="GitHub"
                            >
                                <Github className="h-5 w-5" />
                            </a>
                            <a
                                href="#"
                                className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-all hover:bg-[var(--primary)] hover:text-white hover:shadow-md"
                                aria-label="LinkedIn"
                            >
                                <Linkedin className="h-5 w-5" />
                            </a>
                            <a
                                href="#"
                                className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-all hover:bg-[var(--primary)] hover:text-white hover:shadow-md"
                                aria-label="Email"
                            >
                                <Mail className="h-5 w-5" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* Copyright */}
                <div className="mt-8 border-t border-gray-200 pt-8 text-center">
                    <p className="text-sm text-gray-600">
                        © {currentYear} Rental Property AI. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
