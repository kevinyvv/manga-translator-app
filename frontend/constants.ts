// Centralized constants for the frontend application
// Add all shared hardcoded values here for maintainability

export const DEFAULT_SOURCE_LANGUAGE = "ja";
export const DEFAULT_TARGET_LANGUAGE = "en";

// API URL is loaded from env, fallback for dev
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";


// Add more constants as needed, e.g.:
// export const TIMEOUT_MS = 10000;
