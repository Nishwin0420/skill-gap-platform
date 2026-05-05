import React from "react";
import { NavLink } from "react-router-dom";
import {
  FiHome, FiSearch, FiBarChart2, FiTrendingUp,
  FiBook, FiActivity, FiClock,
  FiLayers, FiMessageSquare
} from "react-icons/fi";

function Navbar() {
  const navItems = [
    { path: "/", label: "Dashboard", icon: <FiHome size={20} /> },
    { path: "/analyze", label: "Skill Analyzer", icon: <FiSearch size={20} /> },
    { path: "/results", label: "Results", icon: <FiBarChart2 size={20} /> },
    { path: "/market", label: "Market Trends", icon: <FiTrendingUp size={20} /> },
    { path: "/learning-path", label: "Learning Path", icon: <FiBook size={20} /> },
    { path: "/compare", label: "Compare Roles", icon: <FiLayers size={20} /> },
    { path: "/interview-prep", label: "Interview Prep", icon: <FiMessageSquare size={20} /> },
    { path: "/history", label: "History", icon: <FiClock size={20} /> },
  ];

  return (
    <nav className="fixed left-0 top-0 h-screen w-64 bg-dark-950 border-r border-dark-700/50 flex flex-col z-50">
      {/* Logo */}
      <div className="px-6 py-8 border-b border-dark-700/50">
        <div className="flex flex-col">
          <h1 className="font-heading font-bold text-white text-2xl tracking-wide leading-none">
            SkillGap<span className="text-primary-400">.</span>
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-dark-400 mt-2 font-medium">
            Career Intelligence
          </p>
        </div>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 px-3 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            {item.icon}
            <span className="text-sm font-medium">{item.label}</span>
          </NavLink>
        ))}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-dark-700/50 bg-dark-900/50">
        <div className="flex items-center gap-2 text-xs text-dark-400">
          <FiActivity size={14} className="text-primary-500" />
          <span>v3.0 • Premium</span>
        </div>
        <p className="text-[10px] text-dark-500 mt-1">
          scikit-learn • HuggingFace • SHAP
        </p>
      </div>
    </nav>
  );
}

export default Navbar;
