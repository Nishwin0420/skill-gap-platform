import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FiTrendingUp, FiTarget, FiAward, FiActivity,
  FiBarChart2, FiCpu, FiLayers, FiZap, FiRefreshCw,
  FiChevronDown, FiChevronUp
} from "react-icons/fi";
import axios from "axios";
import API_BASE from "../config/api";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAllSkills, setShowAllSkills] = useState(false);

  const fetchDashboardStats = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const response = await axios.get(`${API_BASE}/dashboard-stats`);
      setStats(response.data);
    } catch (error) {
      console.log("Backend not connected, showing demo data");
      setStats({
        platform_stats: {
          total_analyses: 0,
          total_users: 0,
          average_match_percentage: 0,
          average_employability_score: 0,
        },
        market_overview: {
          total_job_postings: 2000,
          unique_roles: 15,
          unique_companies: 20,
          regions_covered: 5,
        },
        recent_trends: {
          python: 9.5, javascript: 9.2, react: 8.8,
          "machine learning": 8.5, sql: 8.1, docker: 7.8,
          aws: 7.5, "node.js": 7.2, typescript: 7.0,
          postgresql: 6.8, java: 6.5, kubernetes: 6.2,
          tensorflow: 6.0, pandas: 5.8, linux: 5.6,
          git: 5.4, "deep learning": 5.2, agile: 5.0,
          "rest api": 4.8, flutter: 4.5,
        },
        total_skills_tracked: 20,
      });
    }

    if (isRefresh) setRefreshing(false);
    else setLoading(false);
  }, []);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // All skills from the API; show top 10 by default
  const allSkillEntries = stats?.recent_trends
    ? Object.entries(stats.recent_trends)
    : [];
  const visibleSkills = showAllSkills
    ? allSkillEntries
    : allSkillEntries.slice(0, 10);

  const statCards = [
    {
      title: "Job Market Intelligence",
      value: stats?.market_overview?.total_job_postings || 0,
      suffix: " postings",
      icon: <FiTrendingUp />,
      color: "from-primary-500 to-teal-700",
      desc: "Real-time market data analyzed",
    },
    {
      title: "Skills Tracked",
      value: stats?.total_skills_tracked || 180,
      suffix: "+",
      icon: <FiTarget />,
      color: "from-amber-500 to-orange-600",
      desc: "O*NET + ESCO taxonomy",
    },
    {
      title: "ML Models Active",
      value: 3,
      suffix: "",
      icon: <FiCpu />,
      color: "from-blue-500 to-indigo-600",
      desc: "RF, XGBoost, KNN",
    },
    {
      title: "NLP Engines",
      value: 5,
      suffix: "",
      icon: <FiLayers />,
      color: "from-purple-500 to-pink-600",
      desc: "spaCy + HuggingFace",
    },
  ];

  const modules = [
    {
      icon: <FiTrendingUp size={24} />,
      title: "Job Market Intelligence Engine",
      desc: "Analyzes real-time market data through web scraping & APIs",
      tech: "BeautifulSoup, pandas, trend analysis",
    },
    {
      icon: <FiLayers size={24} />,
      title: "Skill Profiling & Normalization",
      desc: "NLP-powered skill extraction with ontology mapping",
      tech: "spaCy, HuggingFace, TF-IDF, O*NET/ESCO",
    },
    {
      icon: <FiTarget size={24} />,
      title: "Skill Gap Detection Engine",
      desc: "Weighted gap analysis with priority ranking",
      tech: "K-Means clustering, cosine similarity",
    },
    {
      icon: <FiBarChart2 size={24} />,
      title: "Employability Score Prediction",
      desc: "ML-based score (0-100) with readiness levels",
      tech: "Random Forest, XGBoost, KNN",
    },
    {
      icon: <FiActivity size={24} />,
      title: "Learning Path Generator",
      desc: "DAG-based personalized learning sequences",
      tech: "networkx, topological sort",
    },
    {
      icon: <FiZap size={24} />,
      title: "Explainable AI (XAI)",
      desc: "Transparent recommendations with market evidence",
      tech: "SHAP, feature importance, reasoning chains",
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white">
            AI Decision Intelligence
            <span className="text-primary-400"> Dashboard</span>
          </h1>
          <p className="text-gray-400 mt-2">
            Real-time market intelligence • ML-powered predictions • Personalized insights
          </p>
        </div>

        {/* Refresh Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => fetchDashboardStats(true)}
          disabled={refreshing}
          title="Refresh dashboard data"
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-primary-700/40 bg-primary-900/20 text-primary-400 hover:bg-primary-900/40 hover:border-primary-500/60 transition-all text-sm font-medium disabled:opacity-50"
        >
          <FiRefreshCw
            size={15}
            className={refreshing ? "animate-spin" : ""}
          />
          {refreshing ? "Refreshing…" : "Refresh"}
        </motion.button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card-hover p-5"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">
                  {card.title}
                </p>
                <p className="text-2xl font-bold text-white mt-2">
                  {card.value.toLocaleString()}
                  <span className="text-sm text-gray-400">{card.suffix}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">{card.desc}</p>
              </div>
              <div
                className={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center text-white`}
              >
                {card.icon}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Trending Skills — with Show All toggle */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-1">
          <h2 className="section-title flex items-center gap-2">
            <FiTrendingUp className="text-primary-400" />
            Top Market Demand Skills
          </h2>
          <span className="text-xs text-gray-500">
            {showAllSkills ? `All ${allSkillEntries.length}` : "Top 10"} skills
          </span>
        </div>
        <p className="section-subtitle mb-4">Based on 2000+ job postings analysis</p>

        <div className="space-y-3">
          <AnimatePresence initial={false}>
            {visibleSkills.map(([skill, score], i) => (
              <motion.div
                key={skill}
                initial={{ opacity: 0, x: -20, height: 0 }}
                animate={{ opacity: 1, x: 0, height: "auto" }}
                exit={{ opacity: 0, x: -20, height: 0 }}
                transition={{ delay: Math.min(i, 9) * 0.04, duration: 0.3 }}
                className="flex items-center gap-4"
              >
                <span className="text-sm text-gray-400 w-36 truncate capitalize">
                  {skill}
                </span>
                <div className="flex-1 h-3 bg-dark-400 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(score / 10) * 100}%` }}
                    transition={{ delay: 0.1 + i * 0.03, duration: 0.7 }}
                    className="h-full rounded-full"
                    style={{
                      background: `linear-gradient(90deg, #0f766e, #2dd4bf)`,
                    }}
                  />
                </div>
                <span className="text-sm font-semibold text-primary-400 w-14 text-right">
                  {typeof score === "number" ? score.toFixed(2) : score}/10
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Show All / Show Less button */}
        {allSkillEntries.length > 10 && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowAllSkills((v) => !v)}
            className="mt-5 w-full flex items-center justify-center gap-2 py-2.5 rounded-lg border border-primary-700/30 bg-primary-900/10 text-primary-400 hover:bg-primary-900/25 hover:border-primary-500/50 transition-all text-sm font-medium"
          >
            {showAllSkills ? (
              <>
                <FiChevronUp size={16} /> Show Less
              </>
            ) : (
              <>
                <FiChevronDown size={16} /> Show All {allSkillEntries.length} Skills
              </>
            )}
          </motion.button>
        )}
      </motion.div>

      {/* AI Modules Grid */}
      <div>
        <h2 className="section-title mb-4">
          <FiCpu className="inline mr-2 text-primary-400" />
          Active AI/ML Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map((mod, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="glass-card-hover p-5"
            >
              <div className="w-10 h-10 rounded-lg bg-primary-900/40 flex items-center justify-center text-primary-400 mb-3">
                {mod.icon}
              </div>
              <h3 className="font-semibold text-white text-sm">{mod.title}</h3>
              <p className="text-xs text-gray-400 mt-1">{mod.desc}</p>
              <div className="mt-3 flex flex-wrap gap-1">
                {mod.tech.split(", ").map((t, j) => (
                  <span
                    key={j}
                    className="text-xs px-2 py-0.5 rounded-full bg-primary-900/30 text-primary-400"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Key Value Propositions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="glass-card p-6"
      >
        <h2 className="section-title mb-4">
          <FiAward className="inline mr-2 text-amber-400" />
          Key Value Propositions
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Students", desc: "Learn only what matters", icon: "🎓" },
            { label: "Colleges", desc: "Increase placement rates", icon: "🏛️" },
            { label: "Training Institutes", desc: "Design demand-driven courses", icon: "📚" },
            { label: "Recruiters", desc: "Hire skill-ready candidates", icon: "💼" },
          ].map((item, i) => (
            <div
              key={i}
              className="p-4 rounded-lg border border-primary-900/20 hover:border-primary-700/30 transition-colors"
              style={{ background: "rgba(20, 40, 35, 0.5)" }}
            >
              <span className="text-2xl">{item.icon}</span>
              <h3 className="font-semibold text-white text-sm mt-2">
                {item.label}
              </h3>
              <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default Dashboard;
