import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";
import { FiTrendingUp, FiGlobe, FiFilter } from "react-icons/fi";
import axios from "axios";
import API_BASE from "../config/api";

function MarketTrends() {
  const [trends, setTrends] = useState(null);
  const [region, setRegion] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [region]);

  const fetchTrends = async () => {
    setLoading(true);
    try {
      const params = region ? `?region=${region}` : "";
      const response = await axios.get(
        `${API_BASE}/market-trends${params}`
      );
      setTrends(response.data);
    } catch (error) {
      // Demo data
      setTrends({
        demand_scores: {
          python: 9.5, javascript: 9.2, react: 8.8,
          "machine learning": 8.5, sql: 8.1, docker: 7.8,
          aws: 7.5, "node.js": 7.2, typescript: 7.0,
          postgresql: 6.8, "deep learning": 6.5, kubernetes: 6.3,
          git: 6.0, "data analysis": 5.8, java: 5.5,
        },
        trending_skills: {
          "generative ai": { growth_rate: 85, trend: "Rising", recent_count: 120 },
          "machine learning": { growth_rate: 42, trend: "Rising", recent_count: 280 },
          kubernetes: { growth_rate: 35, trend: "Rising", recent_count: 95 },
          typescript: { growth_rate: 28, trend: "Rising", recent_count: 180 },
          react: { growth_rate: 22, trend: "Rising", recent_count: 320 },
          docker: { growth_rate: 18, trend: "Rising", recent_count: 210 },
          aws: { growth_rate: 15, trend: "Rising", recent_count: 250 },
          python: { growth_rate: 12, trend: "Stable", recent_count: 450 },
        },
        market_summary: {
          total_job_postings: 2000,
          unique_roles: 15,
          unique_companies: 20,
          regions_covered: 5,
        },
      });
    }
    setLoading(false);
  };

  const demandData = trends?.demand_scores
    ? Object.entries(trends.demand_scores)
        .slice(0, 15)
        .map(([skill, score]) => ({
          skill: skill.charAt(0).toUpperCase() + skill.slice(1),
          score: score,
        }))
    : [];

  const trendingData = trends?.trending_skills
    ? Object.entries(trends.trending_skills)
        .map(([skill, data]) => ({
          skill: skill.charAt(0).toUpperCase() + skill.slice(1),
          growth: data.growth_rate,
          count: data.recent_count,
          trend: data.trend,
        }))
        .sort((a, b) => b.growth - a.growth)
    : [];

  const regionData = [
    { name: "India", value: 40 },
    { name: "US", value: 25 },
    { name: "Europe", value: 15 },
    { name: "Asia Pacific", value: 10 },
    { name: "Global", value: 10 },
  ];

  const COLORS = ["#2dd4bf", "#0f766e", "#f59e0b", "#3b82f6", "#8b5cf6"];

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white">
            <FiTrendingUp className="inline mr-2 text-primary-400" />
            Market
            <span className="text-primary-400"> Trends</span>
          </h1>
          <p className="text-gray-400 mt-1">
            Real-time job market intelligence from{" "}
            {trends?.market_summary?.total_job_postings?.toLocaleString() || 0} postings
          </p>
        </div>

        {/* Region Filter */}
        <div className="flex items-center gap-2">
          <FiFilter className="text-gray-500" />
          <select
            className="input-dark w-40 text-sm"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          >
            <option value="">All Regions</option>
            <option value="India">India</option>
            <option value="US">US</option>
            <option value="Europe">Europe</option>
            <option value="Asia Pacific">Asia Pacific</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Postings", value: trends?.market_summary?.total_job_postings || 0 },
          { label: "Unique Roles", value: trends?.market_summary?.unique_roles || 0 },
          { label: "Companies", value: trends?.market_summary?.unique_companies || 0 },
          { label: "Regions", value: trends?.market_summary?.regions_covered || 0 },
        ].map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-4 text-center"
          >
            <p className="text-2xl font-bold text-white">{item.value.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">{item.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Demand Scores Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="section-title mb-4">Skill Demand Scores</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={demandData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,212,191,0.1)" />
              <XAxis type="number" domain={[0, 10]} />
              <YAxis dataKey="skill" type="category" width={120} tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }}
              />
              <Bar dataKey="score" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Trending Skills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h3 className="section-title mb-4">🔥 Trending Skills (Growth Rate %)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={trendingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,212,191,0.1)" />
              <XAxis dataKey="skill" tick={{ fontSize: 10, angle: -45, textAnchor: "end" }} height={80} />
              <YAxis />
              <Tooltip
                contentStyle={{ background: "#0e1916", border: "1px solid #134e4a", borderRadius: 8 }}
              />
              <Bar dataKey="growth" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Regional Distribution */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="section-title flex items-center gap-2 mb-4">
          <FiGlobe className="text-primary-400" />
          Regional Job Distribution
        </h3>
        <div className="flex items-center justify-center gap-12">
          <ResponsiveContainer width={300} height={200}>
            <PieChart>
              <Pie data={regionData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80}>
                {regionData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2">
            {regionData.map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i] }} />
                <span className="text-sm text-gray-400">{item.name}</span>
                <span className="text-sm font-semibold text-white">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default MarketTrends;
