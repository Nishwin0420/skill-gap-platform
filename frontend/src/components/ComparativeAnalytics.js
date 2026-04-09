import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis
} from "recharts";
import { FiLayers, FiTarget, FiTrendingUp, FiSearch, FiZap } from "react-icons/fi";
import axios from "axios";
import API_BASE from "../config/api";

function ComparativeAnalytics({ result }) {
  const [comparisons, setComparisons] = useState(null);
  const [loading, setLoading] = useState(false);
  const [skills, setSkills] = useState("");
  const [experience, setExperience] = useState("1");

  const handleCompare = async () => {
    const skillList = skills
      ? skills.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean)
      : result?.resume_skills || [];

    if (skillList.length === 0) {
      alert("Enter your skills (comma-separated) or run an analysis first");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/comparative-analysis`, {
        user_skills: skillList,
        experience: parseFloat(experience || 1),
      });
      setComparisons(response.data);
    } catch (error) {
      // Demo data
      setComparisons({
        best_fit_role: "Full Stack Developer",
        user_skills: skillList,
        comparisons: {
          "Full Stack Developer": { match_percentage: 66.7, your_score: 62.3, benchmark_score: 60, diff_from_benchmark: 2.3, above_average: true, matched_skills: ["javascript", "react", "python"], missing_skills: ["node.js", "docker"], gap_severity: "Medium" },
          "Machine Learning Engineer": { match_percentage: 28.6, your_score: 35.2, benchmark_score: 65, diff_from_benchmark: -29.8, above_average: false, matched_skills: ["python"], missing_skills: ["ml", "deep learning", "tensorflow"], gap_severity: "High" },
          "Data Scientist": { match_percentage: 42.9, your_score: 48.5, benchmark_score: 62, diff_from_benchmark: -13.5, above_average: false, matched_skills: ["python", "sql"], missing_skills: ["ml", "statistics"], gap_severity: "High" },
          "DevOps Engineer": { match_percentage: 25.0, your_score: 30.1, benchmark_score: 58, diff_from_benchmark: -27.9, above_average: false, matched_skills: ["python", "git"], missing_skills: ["docker", "kubernetes", "aws"], gap_severity: "High" },
          "Backend Developer": { match_percentage: 57.1, your_score: 55.8, benchmark_score: 63, diff_from_benchmark: -7.2, above_average: false, matched_skills: ["python", "sql", "git"], missing_skills: ["docker", "rest api"], gap_severity: "Medium" },
        }
      });
    }
    setLoading(false);
  };

  const radarData = comparisons
    ? Object.entries(comparisons.comparisons).map(([role, data]) => ({
        role: role.split(" ").slice(0, 2).join(" "),
        match: data.match_percentage,
        score: data.your_score,
        benchmark: data.benchmark_score,
      }))
    : [];

  const barData = comparisons
    ? Object.entries(comparisons.comparisons).map(([role, data]) => ({
        role: role.split(" ").slice(0, 2).join(" "),
        your_score: data.your_score,
        benchmark: data.benchmark_score,
        diff: data.diff_from_benchmark,
      }))
    : [];

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">
          <FiLayers className="inline mr-2 text-primary-400" />
          Comparative
          <span className="text-primary-400"> Analytics</span>
        </h1>
        <p className="text-gray-400 mt-1">
          Compare your profile against 5 industry role benchmarks
        </p>
      </div>

      {/* Input */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="section-title">Enter Your Skills</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="text-sm text-gray-400 mb-1 block">Skills (comma-separated)</label>
            <input
              type="text"
              className="input-dark"
              placeholder="e.g., python, react, sql, git, javascript"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Experience (years)</label>
            <input
              type="number"
              className="input-dark"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            />
          </div>
        </div>
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="btn-primary flex items-center gap-2"
          onClick={handleCompare}
          disabled={loading}
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <><FiSearch /> Compare Against All Roles</>
          )}
        </motion.button>
      </div>

      {comparisons && (
        <>
          {/* Best Fit */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-6 gradient-border"
          >
            <div className="flex items-center gap-3">
              <FiZap className="text-amber-400" size={24} />
              <div>
                <p className="text-xs text-gray-500 uppercase">Best Fit Role</p>
                <p className="text-2xl font-bold text-white">{comparisons.best_fit_role}</p>
              </div>
            </div>
          </motion.div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card p-6"
            >
              <h3 className="section-title mb-4">
                <FiTarget className="inline mr-2 text-primary-400" />
                Match vs Benchmark
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(45,212,191,0.15)" />
                  <PolarAngleAxis dataKey="role" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                  <Radar dataKey="score" stroke="#2dd4bf" fill="#2dd4bf" fillOpacity={0.3} name="Your Score" />
                  <Radar dataKey="benchmark" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} name="Benchmark" />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Bar Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass-card p-6"
            >
              <h3 className="section-title mb-4">
                <FiTrendingUp className="inline mr-2 text-primary-400" />
                Score Comparison
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,212,191,0.1)" />
                  <XAxis dataKey="role" tick={{ fontSize: 10, angle: -20, textAnchor: "end" }} height={60} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }} />
                  <Bar dataKey="your_score" fill="#2dd4bf" name="Your Score" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="benchmark" fill="#f59e0b" name="Benchmark" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          {/* Role Details */}
          <div className="space-y-3">
            {Object.entries(comparisons.comparisons).map(([role, data], i) => (
              <motion.div
                key={role}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.08 }}
                className="glass-card-hover p-5"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-white">{role}</h4>
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold ${data.above_average ? "text-emerald-400" : "text-red-400"}`}>
                      {data.above_average ? "▲" : "▼"} {data.diff_from_benchmark > 0 ? "+" : ""}{data.diff_from_benchmark}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      data.gap_severity === "Low" ? "bg-emerald-900/20 text-emerald-400" :
                      data.gap_severity === "Medium" ? "bg-amber-900/20 text-amber-400" :
                      "bg-red-900/20 text-red-400"
                    }`}>{data.gap_severity}</span>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-xs text-gray-400 mb-2">
                  <span>Match: <strong className="text-primary-400">{data.match_percentage}%</strong></span>
                  <span>Your Score: <strong className="text-white">{data.your_score}</strong></span>
                  <span>Benchmark: <strong className="text-amber-400">{data.benchmark_score}</strong></span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {(data.matched_skills || []).map((s, j) => (
                    <span key={j} className="skill-tag-matched text-xs capitalize">{s}</span>
                  ))}
                  {(data.missing_skills || []).slice(0, 4).map((s, j) => (
                    <span key={j} className="skill-tag-missing text-xs capitalize">{s}</span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default ComparativeAnalytics;
