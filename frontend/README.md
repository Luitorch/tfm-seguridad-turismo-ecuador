# Dashboard de Visual Analytics — TFM Seguridad y Turismo Ecuador

Dashboard Next.js + Tailwind + Recharts que consume el API FastAPI del backend para visualizar los cuatro análisis del piloto experimental.

## Estructura

```
frontend/
├── src/
│   ├── app/                 # App Router de Next.js 14
│   │   ├── layout.tsx       # Layout global con Sidebar
│   │   ├── page.tsx         # / Resumen ejecutivo con KPIs
│   │   ├── tendencia/       # /tendencia Análisis 1 STL
│   │   ├── correlacion/     # /correlacion Análisis 2 lag+Granger
│   │   ├── provincias/      # /provincias Análisis 3 espacial
│   │   ├── perfiles/        # /perfiles Análisis 4 K-Means
│   │   └── globals.css
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── KpiCard.tsx
│   │   └── charts/          # Gráficos Recharts
│   └── lib/
│       └── api.ts           # Cliente del backend FastAPI
├── package.json
├── tsconfig.json
├── next.config.mjs          # Rewrite /api/* → http://localhost:8000
├── tailwind.config.ts
└── postcss.config.mjs
```

## Levantar el dashboard

```bash
# 1. Levantar el backend (en otra terminal)
cd ../backend
uvicorn app.main:app --reload  # http://localhost:8000

# 2. Instalar dependencias y levantar el frontend
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

## Páginas

| Ruta | Descripción |
|------|-------------|
| `/` | Resumen ejecutivo con 8 KPIs y diagnóstico |
| `/tendencia` | Línea temporal 2010-2025 con marca de quiebre 2022 |
| `/correlacion` | Tabla lag × correlación + ranking de mercados |
| `/provincias` | Tabla provincial + scatter homicidios vs flujos |
| `/perfiles` | Cards de 8 clusters + barras horizontales de evolución |

## Stack

- **Next.js 14.2** (App Router) — framework full-stack React
- **Tailwind CSS 3.4** — diseño utility-first
- **Recharts 2.12** — gráficos React declarativos
- **TypeScript 5.5** — tipado estricto

## Build de producción

```bash
npm run build
npm start
```
