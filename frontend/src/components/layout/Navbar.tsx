'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, TrendingUp, Target, MessageSquare } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/demand-forecasting', label: 'Demand Forecasting', icon: TrendingUp },
    { href: '/gap-analysis', label: 'Gap Analysis', icon: Target },
    { href: '/ai-chat', label: 'AI Chat', icon: MessageSquare },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/90 backdrop-blur-lg shadow-sm">
      <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-12">
        <div className="flex h-20 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-luxury shadow-md transition-all group-hover:shadow-lg group-hover:scale-105">
              <span className="text-xl font-bold text-white">RP</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-[var(--dark)]">Rental Property AI</h1>
              <p className="text-xs text-gray-600">Investment Intelligence</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${isActive
                    ? 'bg-[var(--primary)] text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-[var(--primary)]'
                    }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden md:inline">{link.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
