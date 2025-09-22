// Centralized constants for the frontend application
// Add all shared hardcoded values here for maintainability

export const DEFAULT_SOURCE_LANGUAGE = "ja";
export const DEFAULT_TARGET_LANGUAGE = "en";

// API URL is loaded from env, fallback for dev
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://0.0.0.0:5000";

