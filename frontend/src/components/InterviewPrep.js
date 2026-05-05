import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  FiMessageSquare, FiSearch, FiTarget, FiBook,
  FiCheckCircle, FiAlertTriangle, FiClock, FiStar, FiZap
} from "react-icons/fi";
import { toTitleCase } from "../utils/stringUtils";
import axios from "axios";
import API_BASE from "../config/api";

function InterviewPrep({ result }) {
  const [prepData, setPrepData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [skills, setSkills] = useState("");
  const [jobSkills, setJobSkills] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [activeTab, setActiveTab] = useState("your_skills");

  const handleGenerate = async () => {
    const userList = skills
      ? skills.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean)
      : result?.resume_skills || [];

    const jobList = jobSkills
      ? jobSkills.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean)
      : result?.job_skills || [];

    if (userList.length === 0 || jobList.length === 0) {
      alert("Enter your skills and job skills, or run an analysis first");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/interview-prep`, {
        user_skills: userList,
        job_skills: jobList,
        target_role: targetRole || null,
        job_description: jobDescription || null,
      });
      setPrepData(response.data);
    } catch (error) {
      // Demo data
      setPrepData({
        target_role: targetRole || "ML Engineer",
        total_questions: 18,
        ai_generated: false,
        technical_questions: {
          your_skills: [
            { q: "What are Python decorators? Explain with an example.", level: "intermediate", type: "technical", source: "curated" },
            { q: "Explain the difference between list, tuple, and set in Python.", level: "beginner", type: "technical", source: "curated" },
            { q: "What is the difference between INNER JOIN and LEFT JOIN?", level: "beginner", type: "technical", source: "curated" },
            { q: "Explain indexing in databases and when to use it.", level: "intermediate", type: "technical", source: "curated" },
          ],
          gap_skills: [
            { q: "What is the bias-variance tradeoff?", level: "intermediate", type: "technical", source: "curated" },
            { q: "Explain supervised vs unsupervised learning.", level: "beginner", type: "technical", source: "curated" },
            { q: "What is Docker and how is it different from a VM?", level: "beginner", type: "technical", source: "curated" },
            { q: "What are the key AWS services for deploying?", level: "beginner", type: "technical", source: "curated" },
          ]
        },
        behavioral_questions: [
          { q: "Tell me about a challenging technical problem you solved.", level: "all", type: "behavioral" },
          { q: "How do you stay updated with new technologies?", level: "all", type: "behavioral" },
          { q: "Describe a situation where you learned a new technology quickly.", level: "all", type: "behavioral" },
        ],
        preparation_tips: [
          "You'll likely be tested on: python, sql. Prepare deep examples.",
          "Be ready to explain how you'd learn: machine learning, docker",
          "Frame skill gaps positively: 'I'm currently learning X through Y'",
          "Prepare 2-3 project examples demonstrating your technical skills",
          "Research the company's tech stack and recent projects",
        ],
        study_plan: {
          priority_topics: [
            { skill: "machine learning", difficulty: "intermediate", suggested_prep_hours: 20, focus: "Learn fundamentals + prepare 2 interview answers" },
            { skill: "docker", difficulty: "intermediate", suggested_prep_hours: 8, focus: "Learn basics + containerization concepts" },
          ],
          estimated_prep_days: 10
        },
        confidence_areas: ["python", "sql"],
        weak_areas: ["machine learning", "docker", "aws"]
      });
    }
    setLoading(false);
  };

  const getDifficultyStyle = (level) => {
    switch (level) {
      case "beginner": return "bg-emerald-900/20 text-emerald-400";
      case "intermediate": return "bg-amber-900/20 text-amber-400";
      case "advanced": return "bg-red-900/20 text-red-400";
      default: return "bg-primary-900/20 text-primary-400";
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">
          <FiMessageSquare className="inline mr-2 text-primary-400" />
          Interview
          <span className="text-primary-400"> Preparation</span>
        </h1>
        <p className="text-gray-400 mt-1">
          Personalized interview questions based on your skill gaps
        </p>
      </div>

      {/* Input */}
      <div className="glass-card p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Your Skills</label>
            <input type="text" className="input-dark" placeholder="python, sql, git" value={skills} onChange={(e) => setSkills(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Job Required Skills</label>
            <input type="text" className="input-dark" placeholder="python, ml, docker, aws" value={jobSkills} onChange={(e) => setJobSkills(e.target.value)} />
          </div>
        </div>
        <div>
          <label className="text-sm text-gray-400 mb-1 block">Target Role (Optional)</label>
          <input type="text" className="input-dark" placeholder="e.g., ML Engineer" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} />
        </div>
        {/* NEW: Job Description for Groq AI */}
        <div>
          <label className="text-sm text-gray-400 mb-1 flex items-center gap-2">
            <FiZap className="text-amber-400" size={12} />
            Job Description <span className="text-xs text-amber-400 font-medium">(Paste for AI-Generated Questions)</span>
          </label>
          <textarea
            className="input-dark w-full h-28 resize-none text-sm"
            placeholder="Paste the full job description here to unlock Groq AI-powered, role-specific interview questions..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>
        <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }} className="btn-primary flex items-center gap-2" onClick={handleGenerate} disabled={loading}>
          {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <><FiSearch /> Generate Interview Prep</>}
        </motion.button>
      </div>

      {prepData && (
        <>
          {/* AI Generated Banner */}
          {prepData.ai_generated && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-amber-700/40 bg-amber-900/10"
            >
              <FiZap className="text-amber-400" size={16} />
              <span className="text-sm font-semibold text-amber-300">AI-Generated Questions</span>
              <span className="text-xs text-gray-400">— Powered by Groq ({prepData.ai_model || 'llama3'}) using your Job Description</span>
            </motion.div>
          )}

          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-4">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4 text-center">
              <p className="text-2xl font-bold text-white">{prepData.total_questions}</p>
              <p className="text-xs text-gray-500">Total Questions</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-4 text-center">
              <p className="text-2xl font-bold text-emerald-400">{(prepData.confidence_areas || []).length}</p>
              <p className="text-xs text-gray-500">Confident Areas</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-4 text-center">
              <p className="text-2xl font-bold text-red-400">{(prepData.weak_areas || []).length}</p>
              <p className="text-xs text-gray-500">Weak Areas</p>
            </motion.div>
          </div>

          {/* Strength/Weakness Tags */}
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-emerald-400 mb-2 flex items-center gap-1"><FiCheckCircle size={14} /> Confidence Areas</h4>
              <div className="flex flex-wrap gap-2">{(prepData.confidence_areas || []).map((s, i) => <span key={i} className="skill-tag-matched capitalize">{toTitleCase(s)}</span>)}</div>
            </div>
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-1"><FiAlertTriangle size={14} /> Weak Areas</h4>
              <div className="flex flex-wrap gap-2">{(prepData.weak_areas || []).map((s, i) => <span key={i} className="skill-tag-missing capitalize">{toTitleCase(s)}</span>)}</div>
            </div>
          </div>

          {/* Questions Tabs */}
          <div className="glass-card p-6">
            <div className="flex gap-2 mb-4">
              {[
                { key: "your_skills", label: "Your Skills", icon: <FiCheckCircle /> },
                { key: "gap_skills", label: "Gap Skills", icon: <FiAlertTriangle /> },
                { key: "behavioral", label: "Behavioral", icon: <FiStar /> },
              ].map((tab) => (
                <button
                  key={tab.key}
                  className={`flex items-center gap-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.key ? "bg-primary-900/40 text-primary-400" : "text-gray-500 hover:text-gray-300"
                  }`}
                  onClick={() => setActiveTab(tab.key)}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              {(activeTab === "behavioral"
                ? (prepData.behavioral_questions || [])
                : (prepData.technical_questions?.[activeTab] || [])
              ).map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-4 rounded-lg border border-primary-900/20 hover:border-primary-700/30 transition-colors"
                  style={{ background: "rgba(20, 40, 35, 0.5)" }}
                >
                  <div className="flex items-start justify-between">
                    <p className="text-gray-200 text-sm flex-1 mr-4">{item.q}</p>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${getDifficultyStyle(item.level)}`}>
                        {item.level}
                      </span>
                      {item.source === "ai" ? (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-900/20 text-amber-400 border border-amber-700/30 flex items-center gap-1">
                          <FiZap size={9} /> AI
                        </span>
                      ) : item.source === "curated" ? (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800/40 text-gray-500 border border-gray-700/30 flex items-center gap-1">
                          <FiBook size={9} /> Curated
                        </span>
                      ) : null}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Prep Tips */}
          <div className="glass-card p-6">
            <h3 className="section-title flex items-center gap-2 mb-3">
              <FiTarget className="text-amber-400" />
              Preparation Tips
            </h3>
            <div className="space-y-2">
              {(prepData.preparation_tips || []).map((tip, i) => (
                <div key={i} className="p-3 rounded-lg bg-dark-300/50 text-sm text-gray-300">
                  {tip}
                </div>
              ))}
            </div>
          </div>

          {/* Study Plan */}
          {prepData.study_plan?.priority_topics && (
            <div className="glass-card p-6">
              <h3 className="section-title flex items-center gap-2 mb-4">
                <FiBook className="text-primary-400" />
                Study Plan ({prepData.study_plan.estimated_prep_days} days)
              </h3>
              <div className="space-y-3">
                {prepData.study_plan.priority_topics.map((topic, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center gap-4 p-4 rounded-lg border border-primary-900/20"
                    style={{ background: "rgba(20, 40, 35, 0.5)" }}
                  >
                    <div className="w-8 h-8 rounded-full bg-primary-900/40 flex items-center justify-center text-primary-400 font-bold text-sm">{i + 1}</div>
                    <div className="flex-1">
                      <h4 className="text-white font-medium capitalize">{topic.skill}</h4>
                      <p className="text-xs text-gray-500">{topic.focus}</p>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <FiClock size={12} />
                      {topic.suggested_prep_hours}h
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getDifficultyStyle(topic.difficulty)}`}>
                      {topic.difficulty}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default InterviewPrep;
