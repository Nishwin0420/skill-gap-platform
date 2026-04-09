/**
 * API Configuration
 * ==================
 * Centralized API base URL that automatically switches between:
 * - Local development: http://127.0.0.1:8000/api
 * - Production (Vercel → Render): uses REACT_APP_API_URL env variable
 *
 * Usage in any component:
 *   import { API_BASE } from "../config/api";
 *   const response = await axios.get(`${API_BASE}/dashboard-stats`);
 *   const response = await axios.post(`${API_BASE}/analyze-full`, formData);
 */

const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000/api";

export default API_BASE;
