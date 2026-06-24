'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
  { href: '/', label: 'Resumen ejecutivo', desc: 'KPIs y panorama general' },
  { href: '/tendencia', label: 'Tendencia y estacionalidad', desc: 'Análisis 1 — STL' },
  { href: '/correlacion', label: 'Correlación con seguridad', desc: 'Análisis 2 — Lag y Granger' },
  { href: '/provincias', label: 'Impacto provincial', desc: 'Análisis 3 — Espacial' },
  { href: '/perfiles', label: 'Perfiles de turista', desc: 'Análisis 4 — K-Means' },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-72 min-h-screen bg-slate-900 text-white p-6 flex flex-col">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">TFM · UNIR · 2026</p>
        <h1 className="text-lg font-semibold leading-tight">
          Seguridad y turismo internacional en Ecuador
        </h1>
        <p className="text-xs text-slate-400 mt-2">Luis Torres</p>
      </div>

      <nav className="flex-1 space-y-1">
        {links.map((l) => {
          const active = pathname === l.href;
          return (
            <Link
              key={l.href}
              href={l.href}
              className={`block px-3 py-3 rounded transition ${
                active ? 'bg-brand-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="text-sm font-medium">{l.label}</div>
              <div className={`text-xs ${active ? 'text-blue-100' : 'text-slate-500'}`}>
                {l.desc}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="mt-8 pt-6 border-t border-slate-700 text-xs text-slate-400 space-y-1">
        <p>Dashboard de Visual Analytics</p>
        <p>
          Datos:{' '}
          <a
            href="https://www.ecuadorencifras.gob.ec/entradas-y-salidas-internacionales/"
            target="_blank"
            rel="noreferrer"
            className="text-blue-300 hover:underline"
          >
            INEC
          </a>{' '}
          ·{' '}
          <a
            href="https://www.ministeriodelinterior.gob.ec/"
            target="_blank"
            rel="noreferrer"
            className="text-blue-300 hover:underline"
          >
            MDI
          </a>{' '}
          ·{' '}
          <a
            href="https://data.worldbank.org/"
            target="_blank"
            rel="noreferrer"
            className="text-blue-300 hover:underline"
          >
            BM
          </a>
        </p>
      </div>
    </aside>
  );
}
