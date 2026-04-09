import React from "react";
import { NavLink } from "react-router-dom";
import {
  FiHome, FiSearch, FiBarChart2, FiTrendingUp,
  FiBook, FiCpu, FiActivity, FiClock,
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
    <nav className="fixed left-0 top-0 h-screen w-64 bg-dark-300 border-r border-primary-900/20 flex flex-col z-50">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-primary-900/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
            <FiCpu size={22} className="text-white" />
          </div>
          <div>
            <h1 className="font-heading font-bold text-white text-lg leading-tight">
              SkillGap AI
            </h1>
            <p className="text-xs text-gray-500">Intelligence Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
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
            <span className="text-sm">{item.label}</span>
          </NavLink>
        ))}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-primary-900/20">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <FiActivity size={14} className="text-primary-500" />
          <span>v2.1 • AI Powered</span>
        </div>
        <p className="text-xs text-gray-700 mt-1">
          scikit-learn • HuggingFace • SHAP
        </p>
      </div>
    </nav>
  );
}

export default Navbar;
