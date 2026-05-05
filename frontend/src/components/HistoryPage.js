import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line
} from "recharts";
import {
  FiClock, FiTrendingUp, FiTarget, FiActivity,
  FiUser, FiCalendar, FiAward, FiX, FiRefreshCw,
  FiCheckCircle, FiXCircle
} from "react-icons/fi";
import { toTitleCase } from "../utils/stringUtils";
import axios from "axios";
import API_BASE from "../config/api";

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const fetchHistory = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/history?limit=200`);
      setHistory(response.data.history || []);
      setStats(response.data.aggregated_stats || null);
    } catch (error) {
      // Demo data
      const demoHistory = [
        { id: 1, match_percentage: 38.5, employability_score: 42.5, readiness_level: "Developing", gap_severity: "High", created_at: "2025-03-25T10:30:00", resume_skills: ["python", "sql", "git"], job_skills: ["python", "ml", "docker", "aws"] },
        { id: 2, match_percentage: 72.0, employability_score: 68.3, readiness_level: "Competitive", gap_severity: "Low", created_at: "2025-03-24T14:20:00", resume_skills: ["react", "javascript", "html", "css", "node.js"], job_skills: ["react", "javascript", "html", "css", "typescript"] },
        { id: 3, match_percentage: 55.0, employability_score: 52.1, readiness_level: "Developing", gap_severity: "Medium", created_at: "2025-03-23T09:15:00", resume_skills: ["python", "pandas", "sql"], job_skills: ["python", "ml", "statistics", "pandas", "sql", "tensorflow"] },
        { id: 4, match_percentage: 85.0, employability_score: 81.2, readiness_level: "Highly Competitive", gap_severity: "Low", created_at: "2025-03-22T16:45:00", resume_skills: ["python", "docker", "aws", "linux", "git", "kubernetes"], job_skills: ["python", "docker", "aws", "linux", "git", "kubernetes", "terraform"] },
        { id: 5, match_percentage: 28.0, employability_score: 31.5, readiness_level: "Not Ready", gap_severity: "High", created_at: "2025-03-21T11:00:00", resume_skills: ["html", "css"], job_skills: ["python", "ml", "docker", "aws", "sql", "tensorflow", "pandas"] },
      ];

      setHistory(demoHistory);
      setStats({
        avg_match: 55.7,
        avg_score: 55.1,
        total_analyses: 5,
        highest_score: 81.2,
        lowest_score: 31.5,
        most_common_missing: ["machine learning", "docker", "aws", "tensorflow"]
      });
    }
    if (isRefresh) setRefreshing(false);
    else setLoading(false);
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const trendData = history.map((h, i) => ({
    name: `#${history.length - i}`,
    match: h.match_percentage || 0,
    score: h.employability_score || 0,
  })).reverse();

  const getSeverityColor = (severity) => {
    switch(severity) {
      case "Low": return "text-emerald-400 bg-emerald-900/20";
      case "Medium": return "text-amber-400 bg-amber-900/20";
      case "High": return "text-red-400 bg-red-900/20";
      default: return "text-gray-400 bg-gray-900/20";
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-primary-400";
    if (score >= 40) return "text-amber-400";
    return "text-red-400";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white">
            <FiClock className="inline mr-2 text-primary-400" />
            Analysis
            <span className="text-primary-400"> History</span>
          </h1>
          <p className="text-gray-400 mt-1">
            Track progress across all analyses • Compare stats over time
          </p>
        </div>

        {/* Refresh button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => fetchHistory(true)}
          disabled={refreshing || loading}
          title="Refresh history data"
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-primary-700/40 bg-primary-900/20 text-primary-400 hover:bg-primary-900/40 hover:border-primary-500/60 transition-all text-sm font-medium disabled:opacity-50"
        >
          <FiRefreshCw size={15} className={refreshing ? "animate-spin" : ""} />
          {refreshing ? "Refreshing…" : "Refresh"}
        </motion.button>
      </div>

      {/* Aggregate Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "Total Analyses", value: stats.total_analyses, icon: <FiActivity />, color: "text-primary-400" },
            { label: "Avg Match %", value: `${stats.avg_match}%`, icon: <FiTarget />, color: "text-primary-400" },
            { label: "Avg Score", value: stats.avg_score, icon: <FiAward />, color: "text-amber-400" },
            { label: "Highest Score", value: stats.highest_score, icon: <FiTrendingUp />, color: "text-emerald-400" },
            { label: "Lowest Score", value: stats.lowest_score, icon: <FiUser />, color: "text-red-400" },
          ].map((card, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="glass-card p-4 text-center"
            >
              <div className={`${card.color} mx-auto mb-1`}>{card.icon}</div>
              <p className="text-2xl font-bold text-white">{card.value}</p>
              <p className="text-xs text-gray-500">{card.label}</p>
            </motion.div>
          ))}
        </div>
      )}

      {/* Progress Trend Chart */}
      {trendData.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiTrendingUp className="text-primary-400" />
            Progress Over Time
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,212,191,0.1)" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }} />
              <Line type="monotone" dataKey="match" stroke="#2dd4bf" strokeWidth={2} name="Match %" dot={{ r: 4 }} />
              <Line type="monotone" dataKey="score" stroke="#f59e0b" strokeWidth={2} name="Score" dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-6 mt-2 justify-center text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-primary-400 inline-block" /> Match %</span>
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-amber-400 inline-block" /> Employability Score</span>
          </div>
        </motion.div>
      )}

      {/* Most Common Skills Missing */}
      {stats?.most_common_missing?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-3">
            <FiTrendingUp className="text-red-400" />
            Most Frequently Missing Skills
          </h3>
          <div className="flex flex-wrap gap-2">
            {stats.most_common_missing.map((skill, i) => (
              <span key={i} className="skill-tag-missing capitalize">{toTitleCase(skill)}</span>
            ))}
          </div>
        </motion.div>
      )}

      {/* Analysis History Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="section-title flex items-center gap-2 mb-4">
          <FiClock className="text-primary-400" />
          All Analyses ({history.length})
        </h3>

        {history.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No analyses yet. Go to Skill Analyzer to run your first analysis!
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase border-b border-primary-900/20">
                  <th className="py-3 text-left">#</th>
                  <th className="py-3 text-left">Date</th>
                  <th className="py-3 text-left">Target Role</th>
                  <th className="py-3 text-left">Resume Skills</th>
                  <th className="py-3 text-right">Match %</th>
                  <th className="py-3 text-right">Score</th>
                  <th className="py-3 text-center">Level</th>
                  <th className="py-3 text-center">Severity</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item, i) => (
                  <motion.tr
                    key={item.id || i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + i * 0.05 }}
                    onClick={() => setSelectedAnalysis(item)}
                    className="border-b border-primary-900/10 hover:bg-primary-900/20 cursor-pointer transition-colors"
                  >
                    <td className="py-3 text-primary-400 font-bold">
                      {item.id || i + 1}
                    </td>
                    <td className="py-3 text-gray-400 text-xs">
                      <FiCalendar className="inline mr-1" size={12} />
                      {item.created_at
                        ? new Date(item.created_at).toLocaleDateString()
                        : "N/A"}
                    </td>
                    <td className="py-3 font-medium text-white capitalize text-sm">
                      {item.target_role && item.target_role !== "N/A" ? item.target_role : "General"}
                    </td>
                    <td className="py-3">
                      <div className="flex flex-wrap gap-1">
                        {(item.resume_skills || []).slice(0, 4).map((s, j) => (
                          <span key={j} className="text-xs px-2 py-0.5 rounded-full bg-primary-900/20 text-primary-400 capitalize">
                            {s}
                          </span>
                        ))}
                        {(item.resume_skills || []).length > 4 && (
                          <span className="text-xs text-gray-500">
                            +{item.resume_skills.length - 4}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 text-right font-medium text-primary-400">
                      {item.match_percentage}%
                    </td>
                    <td className={`py-3 text-right font-bold ${getScoreColor(item.employability_score)}`}>
                      {item.employability_score}
                    </td>
                    <td className="py-3 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        item.readiness_level === "Highly Competitive" ? "bg-emerald-900/20 text-emerald-400" :
                        item.readiness_level === "Competitive" ? "bg-primary-900/20 text-primary-400" :
                        item.readiness_level === "Developing" ? "bg-amber-900/20 text-amber-400" :
                        "bg-red-900/20 text-red-400"
                      }`}>
                        {item.readiness_level}
                      </span>
                    </td>
                    <td className="py-3 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(item.gap_severity)}`}>
                        {item.gap_severity}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {/* Analysis Details Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={() => setSelectedAnalysis(null)}>
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6 border-b border-primary-900/20 pb-4">
              <div>
                <h2 className="text-2xl font-heading font-bold text-white flex items-center gap-2">
                  <FiActivity className="text-primary-400" />
                  Analysis Details
                </h2>
                <p className="text-gray-400 text-sm mt-1">
                  <FiTarget className="inline mr-1" />
                  Target Role: <span className="text-white font-medium capitalize">{selectedAnalysis.target_role && selectedAnalysis.target_role !== "N/A" ? selectedAnalysis.target_role : "General"}</span>
                  <span className="mx-2">•</span>
                  <FiCalendar className="inline mr-1" />
                  {selectedAnalysis.created_at ? new Date(selectedAnalysis.created_at).toLocaleString() : "N/A"}
                </p>
              </div>
              <button onClick={() => setSelectedAnalysis(null)} className="text-gray-400 hover:text-white p-2">
                <FiX size={24} />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-primary-900/10 rounded-lg p-3 text-center border border-primary-900/20">
                <p className="text-xs text-gray-500 mb-1">Match %</p>
                <p className="text-xl font-bold text-primary-400">{selectedAnalysis.match_percentage}%</p>
              </div>
              <div className="bg-primary-900/10 rounded-lg p-3 text-center border border-primary-900/20">
                <p className="text-xs text-gray-500 mb-1">Employability</p>
                <p className={`text-xl font-bold ${getScoreColor(selectedAnalysis.employability_score)}`}>{selectedAnalysis.employability_score}</p>
              </div>
              <div className="bg-primary-900/10 rounded-lg p-3 text-center border border-primary-900/20">
                <p className="text-xs text-gray-500 mb-1">Level</p>
                <p className="text-sm font-bold text-white mt-1">{selectedAnalysis.readiness_level}</p>
              </div>
              <div className="bg-primary-900/10 rounded-lg p-3 text-center border border-primary-900/20">
                <p className="text-xs text-gray-500 mb-1">Severity</p>
                <p className={`text-sm font-bold mt-1 ${getSeverityColor(selectedAnalysis.gap_severity).split(' ')[0]}`}>{selectedAnalysis.gap_severity}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-gray-300 mb-2 flex items-center gap-2">My Skills (Resume)</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAnalysis.resume_skills?.map((s, i) => (
                    <span key={i} className="px-3 py-1 rounded-full text-xs bg-primary-900/20 text-primary-300 capitalize border border-primary-900/30">
                      {s}
                    </span>
                  ))}
                  {(!selectedAnalysis.resume_skills || selectedAnalysis.resume_skills.length === 0) && (
                    <span className="text-sm text-gray-500">No skills detected.</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-gray-300 mb-2 flex items-center gap-2">Required Skills (Job)</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAnalysis.job_skills?.map((s, i) => {
                    const hasSkill = selectedAnalysis.resume_skills?.includes(s);
                    return (
                      <span key={i} className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs border ${hasSkill ? 'bg-emerald-900/20 text-emerald-300 border-emerald-900/30' : 'bg-red-900/20 text-red-300 border-red-900/30'} capitalize`}>
                        {toTitleCase(s)} {hasSkill ? <FiCheckCircle size={11} /> : <FiXCircle size={11} />}
                      </span>
                    )
                  })}
                  {(!selectedAnalysis.job_skills || selectedAnalysis.job_skills.length === 0) && (
                    <span className="text-sm text-gray-500">No job skills defined.</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
              <button 
                onClick={() => setSelectedAnalysis(null)}
                className="btn-secondary text-sm px-4 py-2"
              >
                Close Details
              </button>
            </div>
          </motion.div>
        </div>
      )}

    </div>
  );
}

export default HistoryPage;
