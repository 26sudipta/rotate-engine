import { lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import { AppProvider } from "./context/AppContext.jsx";
import RootLayout from "./components/layout/RootLayout.jsx";
import Landing from "./pages/Landing.jsx";
import NotFound from "./pages/NotFound.jsx";

// Heavier pages (map, charts) load on demand.
const Dashboard = lazy(() => import("./pages/Dashboard.jsx"));
const FarmAnalysis = lazy(() => import("./pages/FarmAnalysis.jsx"));
const HistoricalAnalog = lazy(() => import("./pages/HistoricalAnalog.jsx"));
const Strategies = lazy(() => import("./pages/Strategies.jsx"));
const Scenario = lazy(() => import("./pages/Scenario.jsx"));
const Results = lazy(() => import("./pages/Results.jsx"));
const Crops = lazy(() => import("./pages/Crops.jsx"));
const Methodology = lazy(() => import("./pages/Methodology.jsx"));
const Contact = lazy(() => import("./pages/Contact.jsx"));

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<RootLayout />}>
            <Route path="/" element={<Landing />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/farm/:id" element={<FarmAnalysis />} />
            <Route path="/historical" element={<HistoricalAnalog />} />
            <Route path="/strategies" element={<Strategies />} />
            <Route path="/scenario" element={<Scenario />} />
            <Route path="/results" element={<Results />} />
            <Route path="/crops" element={<Crops />} />
            <Route path="/methodology" element={<Methodology />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
