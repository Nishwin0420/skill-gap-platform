import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";
import SkillAnalyzer from "./components/SkillAnalyzer";
import ResultsDashboard from "./components/ResultsDashboard";
import MarketTrends from "./components/MarketTrends";
import LearningPath from "./components/LearningPath";
import HistoryPage from "./components/HistoryPage";
import ComparativeAnalytics from "./components/ComparativeAnalytics";
import InterviewPrep from "./components/InterviewPrep";

function App() {
  const [analysisResult, setAnalysisResult] = React.useState(null);

  return (
    <Router>
      <div className="flex min-h-screen bg-dark-500">
        <Navbar />
        <main className="flex-1 ml-64 p-6 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route
              path="/analyze"
              element={
                <SkillAnalyzer onAnalysisComplete={setAnalysisResult} />
              }
            />
            <Route
              path="/results"
              element={<ResultsDashboard result={analysisResult} />}
            />
            <Route path="/market" element={<MarketTrends />} />
            <Route
              path="/learning-path"
              element={<LearningPath result={analysisResult} />}
            />
            <Route path="/history" element={<HistoryPage />} />
            <Route
              path="/compare"
              element={<ComparativeAnalytics result={analysisResult} />}
            />
            <Route
              path="/interview-prep"
              element={<InterviewPrep result={analysisResult} />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;