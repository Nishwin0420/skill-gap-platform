import React from "react";
import { motion } from "framer-motion";
import { FiBook, FiClock, FiTrendingUp, FiExternalLink, FiCheckCircle } from "react-icons/fi";

function LearningPath({ result }) {
  if (!result || !result.learning_path) {
    return (
      <div className="flex items-center justify-center h-96 animate-fade-in">
        <div className="text-center glass-card p-12">
          <FiBook size={48} className="text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-heading text-gray-400">No Learning Path</h2>
          <p className="text-gray-600 mt-2">
            Run an analysis first to generate a personalized learning path
          </p>
        </div>
      </div>
    );
  }

  const { steps, summary } = result.learning_path;

  const difficultyColors = {
    beginner: { bg: "bg-emerald-900/30", text: "text-emerald-400", border: "border-emerald-700/30" },
    intermediate: { bg: "bg-amber-900/30", text: "text-amber-400", border: "border-amber-700/30" },
    advanced: { bg: "bg-red-900/30", text: "text-red-400", border: "border-red-700/30" },
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">
          <FiBook className="inline mr-2 text-primary-400" />
          Personalized
          <span className="text-primary-400"> Learning Path</span>
        </h1>
        <p className="text-gray-400 mt-1">
          DAG-based optimal learning sequence with market justification
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-5 text-center"
          >
            <FiBook className="text-primary-400 mx-auto mb-2" size={24} />
            <p className="text-2xl font-bold text-white">{summary.total_skills}</p>
            <p className="text-xs text-gray-500">Skills to Learn</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-5 text-center"
          >
            <FiClock className="text-amber-400 mx-auto mb-2" size={24} />
            <p className="text-2xl font-bold text-white">
              {summary.total_estimated_hours}h
            </p>
            <p className="text-xs text-gray-500">Total Estimated</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-5 text-center"
          >
            <FiTrendingUp className="text-emerald-400 mx-auto mb-2" size={24} />
            <p className="text-2xl font-bold text-white">
              ~{summary.total_estimated_weeks} weeks
            </p>
            <p className="text-xs text-gray-500">At 15hrs/week</p>
          </motion.div>
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary-500 via-amber-500 to-red-500 opacity-30" />

        <div className="space-y-4">
          {(steps || []).map((step, i) => {
            const colors = difficultyColors[step.difficulty] || difficultyColors.intermediate;

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="relative pl-20"
              >
                {/* Step Number */}
                <div
                  className={`absolute left-4 w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 ${colors.border} ${colors.bg} ${colors.text}`}
                >
                  {step.step}
                </div>

                {/* Card */}
                <div className="glass-card-hover p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-white capitalize text-lg">
                          {step.skill}
                        </h3>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
                        >
                          {step.difficulty}
                        </span>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span className="flex items-center gap-1">
                          <FiClock size={12} />
                          {step.estimated_hours}h estimated
                        </span>
                        <span className="flex items-center gap-1">
                          <FiTrendingUp size={12} />
                          Demand: {step.market_demand_score}/10
                        </span>
                      </div>

                      {/* Resources */}
                      {step.resources && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {Object.entries(step.resources || {}).map(([type, url]) => (
                            <a
                              key={type}
                              href={url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-primary-900/20 text-primary-400 hover:bg-primary-900/40 transition-colors"
                            >
                              <FiExternalLink size={10} />
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Demand Score Badge */}
                    <div
                      className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold text-sm ${
                        step.market_demand_score >= 8
                          ? "bg-emerald-900/30 text-emerald-400"
                          : step.market_demand_score >= 5
                          ? "bg-amber-900/30 text-amber-400"
                          : "bg-gray-800 text-gray-400"
                      }`}
                    >
                      {step.market_demand_score}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Completion */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 + (steps?.length || 0) * 0.1 }}
          className="relative pl-20 mt-4"
        >
          <div className="absolute left-4 w-9 h-9 rounded-full flex items-center justify-center bg-primary-500 text-white">
            <FiCheckCircle size={18} />
          </div>
          <div className="glass-card p-4 border-primary-500/30">
            <p className="text-primary-400 font-semibold">
              🎉 Path Complete — You'll be job-ready!
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Complete this path to maximize your employability score
            </p>
          </div>
        </motion.div>
      </div>

      {/* Tech Note */}
      <div className="glass-card p-4 text-xs text-gray-500 flex items-center gap-2">
        <FiBook className="text-primary-500" />
        Generated using networkx DAG with topological sorting • Skills ordered by prerequisites & difficulty progression
      </div>
    </div>
  );
}

export default LearningPath;
