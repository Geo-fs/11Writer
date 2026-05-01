import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { WaveDetailPage } from "./pages/WaveDetailPage";
import { WavesPage } from "./pages/WavesPage";

export function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<WavesPage />} />
        <Route path="/waves/:waveId" element={<WaveDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}
