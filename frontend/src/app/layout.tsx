import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata = {
  title: 'TFM · Seguridad y turismo internacional en Ecuador',
  description:
    'Dashboard de Visual Analytics que cuantifica el impacto de la crisis de seguridad pública 2022-2024 sobre el turismo internacional ecuatoriano. Trabajo Fin de Máster, Universidad Internacional de La Rioja (UNIR), 2026.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-8 min-h-screen overflow-x-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
