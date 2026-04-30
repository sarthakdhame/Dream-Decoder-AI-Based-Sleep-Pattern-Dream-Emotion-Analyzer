/**
 * Dream Decoder - API Client
 * Handles all API communication with the backend
 */

const DEFAULT_RENDER_BACKEND_URL = 'https://dream-decoder-ai-based-sleep-pattern.onrender.com';
const RUNTIME_API_BASE = (typeof window !== 'undefined' && window.DREAM_DECODER_API_BASE)
    ? window.DREAM_DECODER_API_BASE
    : '';
const PROD_API_BASE = (RUNTIME_API_BASE || DEFAULT_RENDER_BACKEND_URL).replace(/\/+$/, '');
const isLocalHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const isRenderHost = window.location.hostname.endsWith('.onrender.com');
const API_BASE = (isLocalHost || isRenderHost)
    ? ''
    : PROD_API_BASE;

/**
 * Make an API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // Add authentication headers if available
    if (typeof authService !== 'undefined' && authService.isAuthenticated()) {
        const authHeaders = authService.getAuthHeaders();
        defaultOptions.headers = { ...defaultOptions.headers, ...authHeaders };
    }

    const config = { ...defaultOptions, ...options };

    // Merge headers properly
    if (options.headers) {
        config.headers = { ...defaultOptions.headers, ...options.headers };
    }

    try {
        const method = (config.method || 'GET').toUpperCase();
        let response;
        let lastError;

        // Retry idempotent GET requests once to absorb transient Render connection resets.
        for (let attempt = 0; attempt < 2; attempt++) {
            try {
                response = await fetch(url, config);
                lastError = null;
                break;
            } catch (err) {
                lastError = err;
                if (method !== 'GET' || attempt === 1) {
                    throw err;
                }
            }
        }

        if (!response && lastError) {
            throw lastError;
        }

        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            console.error('Non-JSON response received:', text.substring(0, 200));
            throw new Error(`Server returned non-JSON response (${response.status}) from ${url}. Verify backend deployment URL and route availability.`);
        }

        if (!response.ok) {
            // Handle 401 Unauthorized - redirect to login
            if (response.status === 401 && typeof authService !== 'undefined') {
                authService.clearAuth();
                window.location.href = '/login.html';
                return;
            }
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);

        // Handle network errors (Failed to fetch)
        if (error.message === 'Failed to fetch') {
            throw new Error(`Could not connect to the server. Ensure backend is reachable at ${API_BASE || 'http://localhost:5000'} and avoid opening files via file://.`);
        }

        throw error;
    }
}

// ==========================================
// DREAMS API
// ==========================================

/**
 * Create a new dream entry
 */
async function createDream(contentOrPayload) {
    const payload = typeof contentOrPayload === 'string'
        ? { content: contentOrPayload }
        : contentOrPayload;

    return apiRequest('/api/dreams', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

/**
 * Get all dreams with pagination
 */
async function getDreams(limit = 50, offset = 0) {
    return apiRequest(`/api/dreams?limit=${limit}&offset=${offset}`);
}

/**
 * Get compact Jungian reports for journal tab.
 */
async function getDreamReports(limit = 80, offset = 0) {
    return apiRequest(`/api/dreams/reports?limit=${limit}&offset=${offset}`);
}

/**
 * Get a specific dream by ID
 */
async function getDream(id) {
    return apiRequest(`/api/dreams/${id}`);
}

/**
 * Delete a dream
 */
async function deleteDream(id) {
    return apiRequest(`/api/dreams/${id}`, {
        method: 'DELETE',
    });
}

/**
 * Delete only the Jungian report for a dream
 */
async function deleteJungianReport(id) {
    return apiRequest(`/api/dreams/${id}/jungian-report`, {
        method: 'DELETE',
    });
}

/**
 * Get recent dreams
 */
async function getRecentDreams(days = 7) {
    return apiRequest(`/api/dreams/recent?days=${days}`);
}

// ==========================================
// SLEEP API
// ==========================================

/**
 * Create a new sleep record
 */
async function createSleepRecord(data) {
    return apiRequest('/api/sleep', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * Get all sleep records
 */
async function getSleepRecords(limit = 50, offset = 0) {
    return apiRequest(`/api/sleep?limit=${limit}&offset=${offset}`);
}

/**
 * Get recent sleep records with stats
 */
async function getRecentSleep(days = 7) {
    return apiRequest(`/api/sleep/recent?days=${days}`);
}

/**
 * Get sleep statistics
 */
async function getSleepStats(days = 7) {
    return apiRequest(`/api/sleep/stats?days=${days}`);
}

/**
 * Delete a sleep record
 */
async function deleteSleepRecord(id) {
    return apiRequest(`/api/sleep/${id}`, {
        method: 'DELETE',
    });
}

/**
 * Delete all sleep records for the authenticated user
 */
async function deleteAllSleepRecords() {
    return apiRequest('/api/sleep/all', {
        method: 'DELETE',
    });
}

// ==========================================
// ANALYSIS API
// ==========================================

/**
 * Analyze text without saving
 */
async function analyzeText(text) {
    return apiRequest('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ text }),
    });
}

/**
 * Get Jungian specialized analysis
 */
async function getJungianAnalysis(text) {
    return apiRequest('/api/analyze/jungian', {
        method: 'POST',
        body: JSON.stringify({ text }),
    });
}


// INSIGHTS API


/**
 * Get personalized insights
 */
async function getInsights(days = 7) {
    return apiRequest(`/api/insights?days=${days}`);
}

/**
 * Get trend data for charts
 */
async function getTrends(days = 30) {
    return apiRequest(`/api/trends?days=${days}`);
}


// HEALTH CHECK

/**
 * Check if API is healthy
 */
async function healthCheck() {
    return apiRequest('/api/health');
}
/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}
