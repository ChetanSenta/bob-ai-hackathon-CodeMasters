import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import FleetOverview from './pages/FleetOverview';
import AssetDetail from './pages/AssetDetail';
import DataUpload from './pages/DataUpload';
import MaintenancePlan from './pages/MaintenancePlan';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a' }}>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<FleetOverview />} />
          <Route path="/asset/:asset_id" element={<AssetDetail />} />
          <Route path="/maintenance" element={<MaintenancePlan />} />
          <Route path="/upload" element={<DataUpload />} />
        </Routes>
      </main>
    </div>
  );
}
