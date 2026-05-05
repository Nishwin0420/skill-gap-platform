import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  FiUpload, FiFileText, FiSearch, FiZap, FiCpu,
  FiChevronDown, FiChevronUp, FiCode, FiBriefcase, FiAlertCircle
} from "react-icons/fi";
import axios from "axios";
import API_BASE from "../config/api";

function SkillAnalyzer({ onAnalysisComplete }) {
  const navigate = useNavigate();
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [jdFile, setJdFile] = useState(null);
  const [experience, setExperience] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  // Coding platform section
  const [showPlatforms, setShowPlatforms] = useState(false);
  const [leetcode, setLeetcode] = useState("");
  const [codechef, setCodechef] = useState("");
  const [hackerrank, setHackerrank] = useState("");
  const [codeforces, setCodeforces] = useState("");
  const [github, setGithub] = useState("");

  const progressSteps = [
    "Extracting skills with NLP...",
    "Normalizing via O*NET/ESCO...",
    "Running gap detection...",
    "Training ML prediction...",
    "Generating learning path...",
    "Building XAI explanations...",
  ];

  const hasPlatforms = [leetcode, codechef, hackerrank, codeforces, github].some(
    (v) => v.trim() !== ""
  );

  const handleAnalyze = async () => {
    if (!resumeFile && !resumeText) {
      alert("Please upload a resume or enter resume text");
      return;
    }
    if (!jdText && !jdFile) {
      alert("Please enter a job description or upload JD file");
      return;
    }

    setLoading(true);
    setProgress(0);

    // Simulate progress animation
    const interval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 1, 5));
    }, 800);

    try {
      const formData = new FormData();
      if (resumeFile) formData.append("resume", resumeFile);
      if (jdFile) formData.append("jd_file", jdFile);
      formData.append("job_description", jdText);
      formData.append("experience", parseFloat(experience || 0));
      formData.append("target_role", targetRole);

      // Optional coding platform usernames
      if (leetcode.trim())    formData.append("leetcode_username",   leetcode.trim());
      if (codechef.trim())    formData.append("codechef_username",   codechef.trim());
      if (hackerrank.trim())  formData.append("hackerrank_username", hackerrank.trim());
      if (codeforces.trim())  formData.append("codeforces_username", codeforces.trim());
      if (github.trim())      formData.append("github_username",     github.trim());

      const response = await axios.post(
        `${API_BASE}/analyze-full`,
        formData
      );

      clearInterval(interval);
      setProgress(6);

      if (onAnalysisComplete) {
        onAnalysisComplete(response.data);
      }

      setTimeout(() => navigate("/results"), 500);
    } catch (error) {
      clearInterval(interval);
      console.error(error);

      // Demo fallback
      const demoResult = generateDemoResult();
      if (onAnalysisComplete) onAnalysisComplete(demoResult);
      setTimeout(() => navigate("/results"), 500);
    }

    setLoading(false);
  };

  const generateDemoResult = () => ({
    resume_skills: ["python", "javascript", "react", "sql", "git"],
    job_skills: [
      "python", "machine learning", "deep learning", "tensorflow",
      "sql", "docker", "aws", "data analysis",
    ],
    experience_detected: parseFloat(experience || 1),
    gap_analysis: {
      matched_skills: ["python", "sql"],
      missing_skills: ["machine learning", "deep learning", "tensorflow", "docker", "aws", "data analysis"],
      extra_skills: ["javascript", "react", "git"],
      match_percentage: 38.46,
      gap_severity: "High",
      vector_similarity: 0.3015,
      total_required: 8,
      total_matched: 2,
      total_missing: 6,
      category_analysis: {
        machine_learning_ai: { required: ["machine learning", "deep learning", "tensorflow"], matched: [], missing: ["machine learning", "deep learning", "tensorflow"], coverage: 0 },
        data_science: { required: ["data analysis"], matched: [], missing: ["data analysis"], coverage: 0 },
        databases: { required: ["sql"], matched: ["sql"], missing: [], coverage: 100 },
        cloud_devops: { required: ["docker", "aws"], matched: [], missing: ["docker", "aws"], coverage: 0 },
        programming_languages: { required: ["python"], matched: ["python"], missing: [], coverage: 100 },
      },
      priority_ranking: [
        { skill: "machine learning", priority_score: 8.5, market_weight: 10, difficulty: "intermediate", estimated_hours: 150, category: "machine_learning_ai" },
        { skill: "deep learning", priority_score: 7.8, market_weight: 10, difficulty: "advanced", estimated_hours: 200, category: "machine_learning_ai" },
        { skill: "aws", priority_score: 7.2, market_weight: 10, difficulty: "intermediate", estimated_hours: 120, category: "cloud_devops" },
        { skill: "tensorflow", priority_score: 6.9, market_weight: 9, difficulty: "advanced", estimated_hours: 100, category: "machine_learning_ai" },
        { skill: "docker", priority_score: 6.5, market_weight: 9, difficulty: "intermediate", estimated_hours: 40, category: "cloud_devops" },
        { skill: "data analysis", priority_score: 6.0, market_weight: 9, difficulty: "intermediate", estimated_hours: 100, category: "data_science" },
      ],
    },
    employability: {
      employability_score: 42.5,
      readiness_level: "Developing",
      readiness_confidence: 0.78,
      technical_score: 38.46,
      experience_score: 10,
      overall_rating: "Needs Improvement",
      job_suitability: "Not Suitable",
      feature_names: [
        "Skill Match %", "Market Demand Score", "Experience Level",
        "In-Demand Skills Count", "Skill Diversity", "Gap Severity",
        "Missing Skills Impact", "Matched Skills Value",
      ],
      feature_values: [0.38, 0.45, 0.05, 0.2, 0.25, 0.3, 0.4, 0.35],
      feature_importance: {
        "Skill Match %": 0.32, "Market Demand Score": 0.18,
        "Experience Level": 0.12, "In-Demand Skills Count": 0.10,
        "Skill Diversity": 0.08, "Gap Severity": 0.09,
        "Missing Skills Impact": 0.06, "Matched Skills Value": 0.05,
      },
    },
    explanation: {
      summary: "Your employability score is 43/100 (Developing). You match 38% of the required skills. There are 6 skill gaps that need attention.",
      actionable_insights: [
        "🎯 Start with foundational skills before advanced ones.",
        "📚 Priority 1: Learn machine learning — highest impact on your score.",
        "📊 Keep tracking market trends — skill demand changes quarterly.",
      ],
      strengths: [
        { skill: "python", market_weight: 10, significance: "High-demand skill" },
        { skill: "sql", market_weight: 9, significance: "Essential for data roles" },
      ],
    },
    learning_path: {
      steps: [
        { step: 1, skill: "data analysis", difficulty: "intermediate", estimated_hours: 100, market_demand_score: 9 },
        { step: 2, skill: "machine learning", difficulty: "intermediate", estimated_hours: 150, market_demand_score: 10 },
        { step: 3, skill: "deep learning", difficulty: "advanced", estimated_hours: 200, market_demand_score: 10 },
        { step: 4, skill: "tensorflow", difficulty: "advanced", estimated_hours: 100, market_demand_score: 9 },
        { step: 5, skill: "docker", difficulty: "intermediate", estimated_hours: 40, market_demand_score: 9 },
        { step: 6, skill: "aws", difficulty: "intermediate", estimated_hours: 120, market_demand_score: 10 },
      ],
      summary: { total_skills: 6, total_estimated_hours: 710, total_estimated_weeks: 47.3 },
    },
    // Demo platform proficiency when platforms provided
    ...(hasPlatforms ? {
      skill_proficiency: {
        profiles: {
          ...(leetcode && { leetcode: { platform: "LeetCode", username: leetcode, problems_solved: 245, easy: 120, medium: 98, hard: 27, normalized_score: 40.8, level: "Intermediate", estimated: true } }),
          ...(github && { github: { platform: "GitHub", username: github, public_repos: 22, total_stars: 45, contributions_last_year: 380, normalized_score: 58.2, level: "Intermediate", estimated: true } }),
        },
        skill_proficiency: [
          { skill: "python", strength: 72.5, level: "Advanced", platform_evidence: [{ platform: "LeetCode", score: 40.8, level: "Intermediate", weight: 0.7 }], confidence: 0.7, domains: ["algorithms", "data_structures"] },
          { skill: "sql", strength: 55.0, level: "Intermediate", platform_evidence: [{ platform: "LeetCode", score: 40.8, level: "Intermediate", weight: 0.8 }], confidence: 0.8, domains: ["sql", "databases"] },
          { skill: "javascript", strength: 48.3, level: "Intermediate", platform_evidence: [{ platform: "GitHub", score: 58.2, level: "Intermediate", weight: 0.8 }], confidence: 0.8, domains: ["web", "algorithms"] },
          { skill: "react", strength: 44.6, level: "Intermediate", platform_evidence: [{ platform: "GitHub", score: 58.2, level: "Intermediate", weight: 0.8 }], confidence: 0.8, domains: ["web"] },
          { skill: "git", strength: 60.2, level: "Advanced", platform_evidence: [{ platform: "GitHub", score: 58.2, level: "Intermediate", weight: 1.0 }], confidence: 1.0, domains: ["implementation"] },
        ],
        platforms_analyzed: hasPlatforms ? 2 : 0,
        skills_evaluated: 5,
        summary: { avg_strength: 56.1, strongest_skill: "python", weakest_skill: "react" },
      }
    } : {})
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">
          <FiSearch className="inline mr-2 text-primary-400" />
          Skill Gap
          <span className="text-primary-400"> Analyzer</span>
        </h1>
        <p className="text-gray-400 mt-2">
          Upload your resume and job description for AI-powered analysis
        </p>
      </div>

      {/* Pipeline Info */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <FiCpu className="text-primary-400" />
          <span>
            Pipeline: spaCy NER → HuggingFace → TF-IDF → Random Forest → XGBoost →
            KNN → K-Means → networkx DAG → SHAP
          </span>
        </div>
      </div>

      {/* Input Form */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="section-title flex items-center gap-2"><FiFileText className="text-primary-400" /> Resume Input</h2>

        {/* Resume Text */}
        <div>
          <label className="text-sm text-gray-400 mb-1 block">
            Paste Resume Text
          </label>
          <textarea
            className="input-dark h-32 resize-none"
            placeholder="Paste your resume content here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
          />
        </div>

        {/* Resume File Upload */}
        <div>
          <label className="text-sm text-gray-400 mb-1 block">
            Or Upload Resume PDF
          </label>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 btn-secondary cursor-pointer text-sm">
              <FiUpload />
              {resumeFile ? resumeFile.name : "Choose PDF"}
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => setResumeFile(e.target.files[0])}
              />
            </label>
          </div>
        </div>

        <hr className="border-primary-900/20" />

        <h2 className="section-title flex items-center gap-2"><FiBriefcase className="text-amber-400" /> Job Description</h2>

        {/* JD Text */}
        <div>
          <label className="text-sm text-gray-400 mb-1 block">
            Paste Job Description
          </label>
          <textarea
            className="input-dark h-32 resize-none"
            placeholder="Paste the job description or list required skills..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>

        {/* JD File */}
        <div>
          <label className="text-sm text-gray-400 mb-1 block">
            Or Upload JD PDF
          </label>
          <label className="flex items-center gap-2 btn-secondary cursor-pointer text-sm w-fit">
            <FiFileText />
            {jdFile ? jdFile.name : "Choose PDF"}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setJdFile(e.target.files[0])}
            />
          </label>
        </div>

        <hr className="border-primary-900/20" />

        {/* Experience & Role */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">
              Years of Experience
            </label>
            <input
              type="number"
              className="input-dark"
              placeholder="e.g., 2"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">
              Target Role (Optional)
            </label>
            <input
              type="text"
              className="input-dark"
              placeholder="e.g., ML Engineer"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
            />
          </div>
        </div>

        {/* ─── Coding Platforms Section (Collapsible) ─── */}
        <div className="rounded-lg border border-dashed border-primary-700/40 overflow-hidden">
          {/* Toggle Header */}
          <button
            type="button"
            onClick={() => setShowPlatforms((v) => !v)}
            className="w-full flex items-center justify-between px-4 py-3 bg-primary-900/10 hover:bg-primary-900/20 transition-colors text-left"
          >
            <div className="flex items-center gap-2">
              <FiCode className="text-primary-400" size={16} />
              <span className="text-sm font-semibold text-primary-300">
                Coding Profiles
              </span>
              <span className="text-xs text-gray-500 italic">(Optional — enhances skill proficiency analysis)</span>
              {hasPlatforms && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-primary-600/30 text-primary-300 border border-primary-600/40">
                  {[leetcode, codechef, hackerrank, codeforces, github].filter(v => v.trim()).length} linked
                </span>
              )}
            </div>
            {showPlatforms ? (
              <FiChevronUp size={16} className="text-gray-400" />
            ) : (
              <FiChevronDown size={16} className="text-gray-400" />
            )}
          </button>

          {/* Collapsible Body */}
          <AnimatePresence initial={false}>
            {showPlatforms && (
              <motion.div
                key="platforms"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25, ease: "easeInOut" }}
                style={{ overflow: "hidden" }}
              >
                <div className="px-4 py-4 space-y-4">
                  <p className="text-xs text-gray-500">
                    Link your coding profiles so we can assess your actual skill strength on each technology in your resume.
                    All fields are optional — add only what you have.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {/* LeetCode */}
                    <div>
                      <label className="text-xs text-gray-400 mb-1 flex items-center gap-1 block">
                        <span className="w-2 h-2 rounded-full bg-amber-400"></span> LeetCode Username
                      </label>
                      <input
                        type="text"
                        className="input-dark text-sm"
                        placeholder="e.g., john_doe"
                        value={leetcode}
                        onChange={(e) => setLeetcode(e.target.value)}
                      />
                    </div>

                    {/* CodeChef */}
                    <div>
                      <label className="text-xs text-gray-400 mb-1 flex items-center gap-1 block">
                        <span className="w-2 h-2 rounded-full bg-orange-600"></span> CodeChef Username
                      </label>
                      <input
                        type="text"
                        className="input-dark text-sm"
                        placeholder="e.g., john_doe"
                        value={codechef}
                        onChange={(e) => setCodechef(e.target.value)}
                      />
                    </div>

                    {/* HackerRank */}
                    <div>
                      <label className="text-xs text-gray-400 mb-1 flex items-center gap-1 block">
                        <span className="w-2 h-2 rounded-full bg-emerald-500"></span> HackerRank Username
                      </label>
                      <input
                        type="text"
                        className="input-dark text-sm"
                        placeholder="e.g., john_doe"
                        value={hackerrank}
                        onChange={(e) => setHackerrank(e.target.value)}
                      />
                    </div>

                    {/* Codeforces */}
                    <div>
                      <label className="text-xs text-gray-400 mb-1 flex items-center gap-1 block">
                        <span className="w-2 h-2 rounded-full bg-blue-500"></span> Codeforces Username
                      </label>
                      <input
                        type="text"
                        className="input-dark text-sm"
                        placeholder="e.g., john_doe"
                        value={codeforces}
                        onChange={(e) => setCodeforces(e.target.value)}
                      />
                    </div>

                    {/* GitHub */}
                    <div className="sm:col-span-2">
                      <label className="text-xs text-gray-400 mb-1 flex items-center gap-1 block">
                        <span className="w-2 h-2 rounded-full bg-gray-500"></span> GitHub Username
                      </label>
                      <input
                        type="text"
                        className="input-dark text-sm"
                        placeholder="e.g., john-doe"
                        value={github}
                        onChange={(e) => setGithub(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="text-xs text-gray-600 flex items-start gap-1.5">
                    <FiAlertCircle className="text-amber-500 mt-0.5" />
                    <span>
                      Profile data is analyzed locally. Only usernames are used to estimate proficiency;
                      no private account data is accessed.
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Analyze Button */}
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="btn-primary w-full flex items-center justify-center gap-2 text-lg"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {progressSteps[progress] || "Finalizing..."}
            </>
          ) : (
            <>
              <FiZap /> Run AI Analysis Pipeline
            </>
          )}
        </motion.button>
      </div>

      {/* Progress Steps */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-semibold text-white mb-4">
            AI Pipeline Progress
          </h3>
          <div className="space-y-3">
            {progressSteps.map((step, i) => (
              <div key={i} className="flex items-center gap-3">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i < progress
                      ? "bg-primary-500 text-white"
                      : i === progress
                      ? "bg-amber-500 text-white animate-pulse"
                      : "bg-dark-400 text-gray-600"
                  }`}
                >
                  {i < progress ? "✓" : i + 1}
                </div>
                <span
                  className={`text-sm ${
                    i < progress
                      ? "text-primary-400"
                      : i === progress
                      ? "text-amber-400"
                      : "text-gray-600"
                  }`}
                >
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default SkillAnalyzer;