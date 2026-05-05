import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import {
  FiTarget, FiTrendingUp,
  FiBarChart2, FiCpu, FiZap, FiCheckCircle, FiXCircle, FiBook, FiCode,
  FiClock, FiUsers, FiEdit, FiClipboard, FiAlertTriangle, FiAward, FiFileText, FiChevronDown, FiChevronUp, FiStar
} from "react-icons/fi";
import { toTitleCase } from "../utils/stringUtils";
import ComparativeAnalytics from "./ComparativeAnalytics";

function ResultsDashboard({ result }) {
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [isAdvancedView, setIsAdvancedView] = useState(false);

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIdx(idx);
      setTimeout(() => setCopiedIdx(null), 2000);
    });
  };

  if (!result) {
    return (
      <div className="flex items-center justify-center h-96 animate-fade-in">
        <div className="text-center glass-card p-12">
          <FiBarChart2 size={48} className="text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-heading text-gray-400">No Analysis Yet</h2>
          <p className="text-gray-600 mt-2">
            Go to Skill Analyzer to run an analysis first
          </p>
        </div>
      </div>
    );
  }

  const {
    gap_analysis, employability, explanation, skill_proficiency,
    skill_decay, cohort_benchmarking, ats_optimization,
    resume_skills, extracted_skills
  } = result;

  // Determine all skills from resume
  const allResumeSkills = (resume_skills || 
    (extracted_skills?.normalized ? extracted_skills.normalized.map(s => s.canonical) : [])).map(toTitleCase);
  const score = employability?.employability_score || 0;
  const level = employability?.readiness_level || "N/A";

  // Score color
  const getScoreClass = (s) => {
    if (s >= 80) return "score-excellent";
    if (s >= 60) return "score-good";
    if (s >= 40) return "score-fair";
    return "score-poor";
  };

  // Feature importance for bar chart
  const featureData = (employability?.feature_names || []).map((name, i) => ({
    name: name.replace(" %", "").substring(0, 15),
    value: Math.round((employability?.feature_values?.[i] || 0) * 100),
    importance: Math.round(
      (employability?.feature_importance?.[name] || 0) * 100
    ),
  }));

  // Category coverage for radar
  const categoryData = Object.entries(
    gap_analysis?.category_analysis || {}
  ).map(([key, val]) => ({
    category: key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()).substring(0, 18),
    coverage: val.coverage,
  }));

  // Pie chart for readiness
  const pieData = employability?.readiness_probabilities
    ? Object.entries(employability.readiness_probabilities).map(
        ([name, val]) => ({ name, value: Math.round(val * 100) })
      )
    : [
        { name: level, value: 100 },
      ];

  const COLORS = ["#10b981", "#2dd4bf", "#f59e0b", "#ef4444"];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">
          <FiBarChart2 className="inline mr-2 text-primary-400" />
          Analysis
          <span className="text-primary-400"> Results</span>
        </h1>
        <p className="text-gray-400 mt-1">
          AI-powered skill gap analysis with ML predictions & XAI explanations
        </p>
      </div>

      {/* Narrative Summary */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-5 rounded-xl border border-primary-500/30 bg-primary-900/10 flex flex-col gap-2"
      >
        <h2 className="text-lg font-heading font-bold text-white flex items-center gap-2">
          <FiStar className="text-primary-400" /> Executive Summary
        </h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          Based on our analysis, your profile has a <strong className="text-primary-400">{gap_analysis?.match_percentage || 0}% match</strong> for this role.
          You are currently at a <strong className="text-emerald-400">{level}</strong> readiness level. 
          To bridge your biggest gaps and improve your employability score ({Math.round(score)}/100), we recommend focusing on mastering:{" "}
          <strong className="text-amber-400">
            {(gap_analysis?.priority_ranking || []).slice(0, 3).map(item => toTitleCase(item.skill)).join(", ")}
          </strong>.
        </p>
      </motion.div>

      {/* Top Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-5 text-center"
        >
          <p className="text-xs text-gray-500 uppercase">Employability Score</p>
          <div className={`score-badge text-3xl mx-auto mt-3 w-20 h-20 ${getScoreClass(score)}`}>
            {Math.round(score)}
          </div>
          <p className="text-xs text-gray-400 mt-2">{level}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-5 text-center"
        >
          <p className="text-xs text-gray-500 uppercase">Match Percentage</p>
          <p className="text-3xl font-bold text-primary-400 mt-3">
            {gap_analysis?.match_percentage || 0}%
          </p>
          <p className="text-xs text-gray-400 mt-2">
            {gap_analysis?.total_matched}/{gap_analysis?.total_required} skills
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-5 text-center"
        >
          <p className="text-xs text-gray-500 uppercase">Gap Severity</p>
          <p className={`text-2xl font-bold mt-3 ${
            gap_analysis?.gap_severity === "Low" ? "text-emerald-400" :
            gap_analysis?.gap_severity === "Medium" ? "text-amber-400" :
            "text-red-400"
          }`}>
            {gap_analysis?.gap_severity}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            {gap_analysis?.total_missing} skills missing
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-5 text-center"
        >
          <p className="text-xs text-gray-500 uppercase">Job Suitability</p>
          <p className={`text-2xl font-bold mt-3 ${
            employability?.job_suitability === "Suitable"
              ? "text-emerald-400" : "text-red-400"
          }`}>
            {employability?.job_suitability}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Rating: {employability?.overall_rating}
          </p>
        </motion.div>
      </div>

            {/* Advanced View Toggle */}
      <div className="flex justify-center my-4">
        <button
          onClick={() => setIsAdvancedView(!isAdvancedView)}
          className="flex items-center gap-2 px-4 py-2 rounded-full border border-dark-700/50 bg-dark-900/50 text-sm font-medium text-gray-400 hover:text-white transition-colors"
        >
          {isAdvancedView ? <FiChevronUp /> : <FiChevronDown />}
          {isAdvancedView ? "Hide Advanced ML Details" : "Show Advanced ML Details"}
        </button>
      </div>

      {/* Charts Row */}
      {isAdvancedView && (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Importance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiCpu className="text-primary-400" />
            ML Feature Importance
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={featureData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,212,191,0.1)" />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }}
              />
              <Bar dataKey="value" name="Score %" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
              <Bar dataKey="importance" name="Importance %" fill="#f59e0b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Category Coverage Radar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiTarget className="text-primary-400" />
            Skill Category Coverage
          </h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={categoryData}>
                <PolarGrid stroke="rgba(45,212,191,0.15)" />
                <PolarAngleAxis dataKey="category" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Radar dataKey="coverage" stroke="#2dd4bf" fill="#2dd4bf" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">No category data available</p>
          )}
        </motion.div>
      </div>
      )}

      {/* Skills Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* All Resume Skills */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.55 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiFileText className="text-primary-400" />
            All Resume Skills ({allResumeSkills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {allResumeSkills.length > 0 ? (
              allResumeSkills.map((skill, i) => (
                <span key={i} className="px-2 py-1 rounded bg-dark-400 text-gray-300 text-xs border border-primary-900/10 capitalize">
                  {toTitleCase(skill)}
                </span>
              ))
            ) : (
              <p className="text-gray-500 text-xs italic">No skills extracted</p>
            )}
          </div>
        </motion.div>

        {/* Matched Skills */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiCheckCircle className="text-emerald-400" />
            Matched Skills ({gap_analysis?.matched_skills?.length || 0})
          </h3>
          <div className="flex flex-wrap gap-2">
            {(gap_analysis?.matched_skills || []).map((skill, i) => (
              <span key={i} className="skill-tag-matched">{toTitleCase(skill)}</span>
            ))}
          </div>
        </motion.div>

        {/* Missing Skills */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-4">
            <FiXCircle className="text-red-400" />
            Missing Skills ({gap_analysis?.missing_skills?.length || 0})
          </h3>
          <div className="flex flex-wrap gap-2">
            {(gap_analysis?.missing_skills || []).map((skill, i) => (
              <span key={i} className="skill-tag-missing">{toTitleCase(skill)}</span>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Priority Ranking Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="glass-card p-6"
      >
        <h3 className="section-title flex items-center gap-2 mb-4">
          <FiTrendingUp className="text-amber-400" />
          Priority Ranking (Learn These First)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase border-b border-primary-900/20">
                <th className="py-3 text-left">Rank</th>
                <th className="py-3 text-left">Skill</th>
                <th className="py-3 text-left">Category</th>
                <th className="py-3 text-left">Difficulty</th>
                <th className="py-3 text-right">Market</th>
                <th className="py-3 text-right">Hours</th>
                <th className="py-3 text-right">Priority</th>
              </tr>
            </thead>
            <tbody>
              {(gap_analysis?.priority_ranking || []).map((item, i) => (
                <tr key={i} className="border-b border-primary-900/10 hover:bg-primary-900/10">
                  <td className="py-3 font-bold text-primary-400">#{i + 1}</td>
                  <td className="py-3 text-white capitalize">{toTitleCase(item.skill)}</td>
                  <td className="py-3 text-gray-400 capitalize">
                    {(item.category || "").replace(/_/g, " ")}
                  </td>
                  <td className="py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      item.difficulty === "beginner" ? "bg-emerald-900/30 text-emerald-400" :
                      item.difficulty === "intermediate" ? "bg-amber-900/30 text-amber-400" :
                      "bg-red-900/30 text-red-400"
                    }`}>{item.difficulty}</span>
                  </td>
                  <td className="py-3 text-right text-primary-400 font-medium">
                    {item.market_weight}/10
                  </td>
                  <td className="py-3 text-right text-gray-400">
                    {item.estimated_hours}h
                  </td>
                  <td className="py-3 text-right font-bold text-amber-400">
                    {item.priority_score}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* XAI Explanations */}
      {isAdvancedView && (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="glass-card p-6"
      >
        <h3 className="section-title flex items-center gap-2 mb-4">
          <FiZap className="text-amber-400" />
          AI Explanation (XAI Module)
        </h3>

        {/* Summary */}
        <div className="p-4 rounded-lg bg-dark-400/50 mb-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            {explanation?.summary || "Analysis explanation not available."}
          </p>
        </div>

        {/* Actionable Insights */}
        <div className="space-y-2">
          {(explanation?.actionable_insights || []).map((insight, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-dark-300/50">
              <span className="text-sm text-gray-300">{insight}</span>
            </div>
          ))}
        </div>

        {/* Strengths */}
        {explanation?.strengths?.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-emerald-400 mb-2">
              Your Strengths
            </h4>
            <div className="flex flex-wrap gap-2">
              {explanation.strengths.map((s, i) => (
                <span key={i} className="skill-tag-matched text-xs">
                  {toTitleCase(s.skill)} (weight: {s.market_weight}/10)
                </span>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      )}

      {/* Readiness Distribution Pie Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="glass-card p-6"
      >
        <h3 className="section-title flex items-center gap-2 mb-4">
          <FiBook className="text-primary-400" />
          Readiness Level Distribution
        </h3>
        <div className="flex items-center justify-center gap-8">
          <ResponsiveContainer width={250} height={200}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80}>
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2">
            {pieData.map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                <span className="text-sm text-gray-400">{item.name}</span>
                <span className="text-sm font-semibold text-white">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* ─── Skill Proficiency Card (from Coding Platforms) ─── */}
      {skill_proficiency && skill_proficiency.skill_proficiency?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.05 }}
          className="glass-card p-6"
        >
          <div className="flex items-start justify-between mb-2">
            <h3 className="section-title flex items-center gap-2">
              <FiCode className="text-primary-400" />
              Skill Proficiency from Coding Platforms
            </h3>
            <div className="flex gap-2 flex-wrap justify-end">
              {Object.values(skill_proficiency.profiles || {}).map((p, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-0.5 rounded-full border border-primary-700/40 bg-primary-900/20 text-primary-300"
                >
                  {p.platform}: {p.level}
                  {p.estimated && <span className="opacity-60"> (est.)</span>}
                </span>
              ))}
            </div>
          </div>
          <p className="section-subtitle mb-1">
            Based on {skill_proficiency.platforms_analyzed} platform{skill_proficiency.platforms_analyzed !== 1 ? "s" : ""} ·
            Avg strength: <span className="text-primary-400 font-semibold">{skill_proficiency.summary?.avg_strength}%</span>
          </p>

          {/* Platform profile quick stats */}
          {Object.values(skill_proficiency.profiles || {}).length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 my-4">
              {Object.values(skill_proficiency.profiles).map((p, i) => (
                <div
                  key={i}
                  className="rounded-lg p-3 border border-primary-900/20 bg-primary-900/10 text-center"
                >
                  <p className="text-xs text-gray-500 mb-1 truncate">{p.platform}</p>
                  <p className="text-lg font-bold text-white">{p.normalized_score}</p>
                  <p className={`text-xs font-medium mt-0.5 ${
                    p.level === "Expert" ? "text-emerald-400" :
                    p.level === "Advanced" ? "text-primary-400" :
                    p.level === "Intermediate" ? "text-amber-400" :
                    "text-red-400"
                  }`}>{p.level}</p>
                  {p.problems_solved !== undefined && (
                    <p className="text-xs text-gray-600 mt-1">{p.problems_solved} solved</p>
                  )}
                  {p.rating !== undefined && (
                    <p className="text-xs text-gray-600 mt-1">Rating: {p.rating}</p>
                  )}
                  {p.public_repos !== undefined && (
                    <p className="text-xs text-gray-600 mt-1">{p.public_repos} repos</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Per-skill proficiency bars */}
          <div className="space-y-3 mt-4">
            {skill_proficiency.skill_proficiency.map((item, i) => (
              <motion.div
                key={toTitleCase(item.skill)}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.1 + i * 0.04 }}
                className="flex items-center gap-3"
              >
                {/* Skill name */}
                <span className="text-sm text-gray-300 w-32 capitalize truncate">{toTitleCase(item.skill)}</span>

                {/* Strength bar */}
                <div className="flex-1 h-3 bg-dark-400 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.strength}%` }}
                    transition={{ delay: 1.15 + i * 0.04, duration: 0.7 }}
                    className="h-full rounded-full"
                    style={{
                      background:
                        item.strength >= 80 ? "linear-gradient(90deg, #059669, #10b981)" :
                        item.strength >= 60 ? "linear-gradient(90deg, #0f766e, #2dd4bf)" :
                        item.strength >= 40 ? "linear-gradient(90deg, #b45309, #f59e0b)" :
                        "linear-gradient(90deg, #991b1b, #ef4444)",
                    }}
                  />
                </div>

                {/* Strength value */}
                <span className={`text-sm font-bold w-10 text-right ${
                  item.strength >= 80 ? "text-emerald-400" :
                  item.strength >= 60 ? "text-primary-400" :
                  item.strength >= 40 ? "text-amber-400" :
                  "text-red-400"
                }`}>{item.strength}</span>

                {/* Level badge */}
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium w-24 text-center ${
                  item.level === "Expert" ? "bg-emerald-900/30 text-emerald-400 border border-emerald-900/40" :
                  item.level === "Advanced" ? "bg-primary-900/30 text-primary-400 border border-primary-900/40" :
                  item.level === "Intermediate" ? "bg-amber-900/30 text-amber-400 border border-amber-900/40" :
                  "bg-red-900/30 text-red-400 border border-red-900/40"
                }`}>{item.level}</span>
              </motion.div>
            ))}
          </div>

          <p className="text-xs text-gray-600 mt-4 text-right">
            Proficiency estimated from {skill_proficiency.platforms_analyzed} connected platform{skill_proficiency.platforms_analyzed !== 1 ? 's' : ''}
          </p>
        </motion.div>
      )}

      {/* ─── FEATURE 1: Skill Freshness / Decay Card ─── */}
      {skill_decay && skill_decay.skill_freshness?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.15 }}
          className="glass-card p-6"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-1">
            <h3 className="section-title flex items-center gap-2">
              <FiClock className="text-amber-400" />
              Skill Freshness Analysis
            </h3>
            <div className="flex gap-2 text-xs">
              <span className="px-2 py-0.5 rounded-full bg-emerald-900/30 text-emerald-400 border border-emerald-900/40">
                 {skill_decay.summary.fresh} Fresh
              </span>
              <span className="px-2 py-0.5 rounded-full bg-amber-900/30 text-amber-400 border border-amber-900/40">
                 {skill_decay.summary.fading} Fading
              </span>
              <span className="px-2 py-0.5 rounded-full bg-red-900/30 text-red-400 border border-red-900/40">
                 {skill_decay.summary.decaying} Decaying
              </span>
            </div>
          </div>
          <p className="section-subtitle mb-4">
            Half-life decay model — skills lose ~15% strength per year of inactivity •
            Avg freshness: <span className="font-semibold text-amber-400">{skill_decay.summary.avg_freshness_score}/100</span>
          </p>

          {/* Needs refresher alert */}
          {skill_decay.summary.needs_refresher?.length > 0 && (
            <div className="mb-4 p-3 rounded-lg border border-amber-700/30 bg-amber-900/10 flex items-start gap-2">
              <FiAlertTriangle className="text-amber-400 mt-0.5 shrink-0" size={16} />
              <div>
                <p className="text-xs font-semibold text-amber-300">Refresher Recommended</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {skill_decay.summary.needs_refresher.join(", ")} — these skills may need updating to stay competitive.
                </p>
              </div>
            </div>
          )}

          {/* Per-skill freshness bars */}
          <div className="space-y-3">
            {skill_decay.skill_freshness.map((item, i) => (
              <motion.div
                key={toTitleCase(item.skill)}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.2 + i * 0.04 }}
                className="flex items-center gap-3"
              >
                <span className="text-sm w-32 capitalize truncate text-gray-300">{toTitleCase(item.skill)}</span>
                <div className="flex-1 h-3 bg-dark-400 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.freshness_score}%` }}
                    transition={{ delay: 1.25 + i * 0.04, duration: 0.7 }}
                    className="h-full rounded-full"
                    style={{
                      background:
                        item.freshness_score >= 70 ? "linear-gradient(90deg, #059669, #10b981)" :
                        item.freshness_score >= 45 ? "linear-gradient(90deg, #b45309, #f59e0b)" :
                        "linear-gradient(90deg, #991b1b, #ef4444)",
                    }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-24 text-right">
                  {item.last_used_year ? `Last: ${item.last_used_year}` : "Year unknown"}
                </span>
                <span className={`text-xs font-bold w-10 text-right ${
                  item.label === "Fresh" ? "text-emerald-400" :
                  item.label === "Fading" ? "text-amber-400" : "text-red-400"
                }`}>{item.freshness_score}</span>
                <span className={`w-2 h-2 rounded-full ${item.label === "Fresh" ? "bg-emerald-400" : item.label === "Fading" ? "bg-amber-400" : "bg-red-400"}`}></span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ─── FEATURE 2: Peer Cohort Benchmarking ─── */}
      {cohort_benchmarking && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          className="glass-card p-6"
        >
          <h3 className="section-title flex items-center gap-2 mb-1">
            <FiUsers className="text-blue-400" />
            Peer Cohort Benchmarking
          </h3>
          <p className="section-subtitle mb-4">
            How you rank vs. other platform users targeting{" "}
            <span className="text-white font-medium">{cohort_benchmarking.target_role || "this role"}</span>
          </p>

          {cohort_benchmarking.percentile !== null && cohort_benchmarking.percentile !== undefined ? (
            <div className="space-y-4">
              {/* Percentile Hero — dual bars */}
              <div className="space-y-3">
                {/* vs Platform Users */}
                <div className="flex items-center gap-6">
                  <div className="text-center w-20 shrink-0">
                    <div className="text-4xl font-extrabold text-primary-400">
                      {cohort_benchmarking.percentile}%
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">vs Users</p>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>0%</span>
                      <span className={`font-semibold ${
                        cohort_benchmarking.percentile >= 80 ? "text-emerald-400" :
                        cohort_benchmarking.percentile >= 60 ? "text-primary-400" :
                        cohort_benchmarking.percentile >= 40 ? "text-amber-400" :
                        "text-red-400"
                      }`}>{cohort_benchmarking.rank_label}</span>
                      <span>100%</span>
                    </div>
                    <div className="h-4 bg-dark-400 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${cohort_benchmarking.percentile}%` }}
                        transition={{ delay: 1.3, duration: 1.0 }}
                        className="h-full rounded-full"
                        style={{
                          background:
                            cohort_benchmarking.percentile >= 80 ? "linear-gradient(90deg,#059669,#10b981)" :
                            cohort_benchmarking.percentile >= 60 ? "linear-gradient(90deg,#0f766e,#2dd4bf)" :
                            cohort_benchmarking.percentile >= 40 ? "linear-gradient(90deg,#b45309,#f59e0b)" :
                            "linear-gradient(90deg,#991b1b,#ef4444)",
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* vs Live Market Standard (Feature 5) */}
                {cohort_benchmarking.market_percentile !== null && cohort_benchmarking.market_percentile !== undefined && (
                  <div className="flex items-center gap-6">
                    <div className="text-center w-20 shrink-0">
                      <div className="text-4xl font-extrabold text-amber-400">
                        {Math.round(cohort_benchmarking.market_percentile)}%
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">vs Market</p>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>0%</span>
                        <span className="font-semibold text-amber-400">
                          {cohort_benchmarking.market_baseline_score !== null
                            ? `Market Avg: ${cohort_benchmarking.market_baseline_score}/100`
                            : "Live Market Standard"}
                        </span>
                        <span>100%</span>
                      </div>
                      <div className="h-4 bg-dark-400 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${cohort_benchmarking.market_percentile}%` }}
                          transition={{ delay: 1.5, duration: 1.0 }}
                          className="h-full rounded-full"
                          style={{ background: "linear-gradient(90deg,#b45309,#f59e0b)" }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Cohort stats grid */}
              <div className="grid grid-cols-3 gap-3 mt-2">
                {[
                  { label: "Your Score", val: cohort_benchmarking.your_score, unit: "/100" },
                  { label: "Cohort Avg", val: cohort_benchmarking.avg_cohort_score, unit: "/100" },
                  { label: "Cohort Size", val: cohort_benchmarking.cohort_size, unit: " users" },
                ].map((stat, i) => (
                  <div key={i} className="rounded-lg p-3 border border-primary-900/20 bg-primary-900/10 text-center">
                    <p className="text-xs text-gray-500">{stat.label}</p>
                    <p className="text-xl font-bold text-white mt-1">
                      {stat.val}<span className="text-xs text-gray-500">{stat.unit}</span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-lg border border-primary-700/20 bg-primary-900/10 flex items-center gap-3">
              <FiAward className="text-primary-400" size={24} />
              <div>
                <p className="text-sm font-semibold text-primary-300">Pioneer Analysis</p>
                <p className="text-xs text-gray-400 mt-1">
                  {cohort_benchmarking.message || "Run more analyses to unlock peer benchmarking data."}
                </p>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* ─── FEATURE 3: ATS Resume Optimizer ─── */}
      {ats_optimization && ats_optimization.ats_suggestions?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.25 }}
          className="glass-card p-6"
        >
          <div className="flex items-start justify-between mb-1">
            <h3 className="section-title flex items-center gap-2">
              <FiEdit className="text-violet-400" />
              ATS Resume Optimizer
            </h3>
            <div className="text-xs px-2 py-0.5 rounded-full bg-violet-900/30 text-violet-300 border border-violet-700/40">
              {ats_optimization.under_highlighted_count} skills to improve
            </div>
          </div>
          <p className="section-subtitle mb-4">
            {ats_optimization.well_highlighted_count} skills are well highlighted •
            Improve keyword density for better ATS pass rates
          </p>

          <div className="space-y-5">
            {ats_optimization.ats_suggestions.map((item, si) => (
              <motion.div
                key={toTitleCase(item.skill)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.3 + si * 0.06 }}
                className="rounded-lg border border-violet-900/20 bg-violet-950/20 p-4"
              >
                {/* Skill header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white capitalize">{toTitleCase(item.skill)}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      item.urgency === "High" ? "bg-red-900/30 text-red-400 border border-red-900/40" :
                      item.urgency === "Medium" ? "bg-amber-900/30 text-amber-400 border border-amber-900/40" :
                      "bg-slate-800/50 text-slate-400 border border-slate-700/50"
                    }`}>{item.urgency} Priority</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Currently: {item.current_mentions}× mention{item.current_mentions !== 1 ? "s" : ""} •
                    ATS score: <span className="text-violet-400 font-semibold">{item.ats_impact_score}/10</span>
                  </div>
                </div>

                {/* Suggested rewrites */}
                <div className="space-y-2">
                  {item.suggested_rewrites.map((rewrite, ri) => (
                    <div
                      key={ri}
                      className="flex items-start gap-2 p-2.5 rounded-lg bg-dark-400/40 border border-primary-900/10 group"
                    >
                      <p className="flex-1 text-xs text-gray-300 leading-relaxed">{rewrite}</p>
                      <button
                        onClick={() => handleCopy(rewrite, `${si}-${ri}`)}
                        title="Copy to clipboard"
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-primary-900/30"
                      >
                        {copiedIdx === `${si}-${ri}` ? (
                          <FiCheckCircle size={14} className="text-emerald-400" />
                        ) : (
                          <FiClipboard size={14} className="text-gray-500 hover:text-primary-400" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>

                {/* Context keywords from JD */}
                {item.jd_context_keywords?.length > 0 && (
                  <div className="mt-2 flex items-center gap-1 flex-wrap">
                    <span className="text-xs text-gray-600">JD context:</span>
                    {item.jd_context_keywords.map((kw, ki) => (
                      <span key={ki} className="text-xs px-1.5 py-0.5 rounded bg-violet-900/20 text-violet-400">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ─── FEATURE 4: Comparative Analytics ─── */}
      <div className="mt-8">
        <ComparativeAnalytics result={result} />
      </div>

      {/* Models Used Footer */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <FiCpu className="text-primary-500" />
          <span>Models: </span>
          {["spaCy NER", "TF-IDF", "Random Forest", "XGBoost", "KNN", "K-Means", "networkx DAG", "SHAP",
            "Half-life Decay", "Cohort Percentile", "ATS NLP"
          ].map((m, i) => (
            <span key={i} className="px-2 py-0.5 bg-primary-900/20 rounded-full text-primary-400">
              {m}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ResultsDashboard;
