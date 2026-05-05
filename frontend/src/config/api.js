/**
 * API Configuration
 * ==================
 * Centralized API base URL that automatically switches between:
 * - Local development: http://127.0.0.1:8000/api
 * - Production (Vercel → Railway): uses REACT_APP_BACKEND_URL env variable
 *
 * Set REACT_APP_BACKEND_URL in Vercel's Environment Variables to your
 * Railway backend URL, e.g.:
 *   https://skill-gap-backend.up.railway.app
 *
 * Usage in any component:
 *   import API_BASE from "../config/api";
 *   const response = await axios.get(`${API_BASE}/dashboard-stats`);
 */

const API_BASE =
  process.env.REACT_APP_BACKEND_URL
    ? `${process.env.REACT_APP_BACKEND_URL}/api`
    : "http://localhost:8000/api";

export default API_BASE;
