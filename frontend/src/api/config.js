// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// API Endpoints
export const ENDPOINTS = {
  // Resume Analysis
  ANALYZE_RESUME: '/analyze-resume',
  HEALTH: '/health',
  
  // Auth
  LOGIN: '/auth/login',
  SIGNUP: '/auth/signup',
  LOGOUT: '/auth/logout',
  ME: '/auth/me',
  
  // Profile
  PROFILE: '/profile',
  
  // Analysis History
  ANALYSES_HISTORY: '/analyses/history',
  ANALYSIS_DETAIL: '/analyses', // + /:id
  
  // Learning Progress
  LEARNING_PROGRESS: '/learning/progress',
};

// API Helper Functions
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  // Don't set Content-Type for FormData (browser sets it automatically with boundary)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Something went wrong');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Resume Analysis API
export const analyzeResume = async (file, targetRole) => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('target_role', targetRole);
  
  return apiRequest(ENDPOINTS.ANALYZE_RESUME, {
    method: 'POST',
    body: formData,
  });
};

// Auth API
export const login = async (email, password) => {
  return apiRequest(ENDPOINTS.LOGIN, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
};

export const signup = async (name, email, password) => {
  return apiRequest(ENDPOINTS.SIGNUP, {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  });
};

export const logout = async () => {
  return apiRequest(ENDPOINTS.LOGOUT, {
    method: 'POST',
  });
};

export const getCurrentUser = async () => {
  return apiRequest(ENDPOINTS.ME, {
    method: 'GET',
  });
};

// Profile API
export const getProfile = async () => {
  return apiRequest(ENDPOINTS.PROFILE, {
    method: 'GET',
  });
};

export const updateProfile = async (profileData) => {
  return apiRequest(ENDPOINTS.PROFILE, {
    method: 'PUT',
    body: JSON.stringify(profileData),
  });
};

// Analysis History API
export const getAnalysisHistory = async (page = 1, perPage = 10) => {
  return apiRequest(`${ENDPOINTS.ANALYSES_HISTORY}?page=${page}&per_page=${perPage}`, {
    method: 'GET',
  });
};

export const getAnalysisDetail = async (analysisId) => {
  return apiRequest(`${ENDPOINTS.ANALYSIS_DETAIL}/${analysisId}`, {
    method: 'GET',
  });
};

export const deleteAnalysis = async (analysisId) => {
  return apiRequest(`${ENDPOINTS.ANALYSIS_DETAIL}/${analysisId}`, {
    method: 'DELETE',
  });
};

// Learning Progress API
export const getLearningProgress = async () => {
  return apiRequest(ENDPOINTS.LEARNING_PROGRESS, {
    method: 'GET',
  });
};

export const addLearningSkill = async (skillData) => {
  return apiRequest(ENDPOINTS.LEARNING_PROGRESS, {
    method: 'POST',
    body: JSON.stringify(skillData),
  });
};

export const updateLearningProgress = async (progressId, data) => {
  return apiRequest(`${ENDPOINTS.LEARNING_PROGRESS}/${progressId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

export const deleteLearningProgress = async (progressId) => {
  return apiRequest(`${ENDPOINTS.LEARNING_PROGRESS}/${progressId}`, {
    method: 'DELETE',
  });
};

// Health Check
export const checkHealth = async () => {
  return apiRequest(ENDPOINTS.HEALTH, {
    method: 'GET',
  });
};

