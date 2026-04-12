/**
 * Dream Decoder - Authentication Service
 * Handles user authentication, token management, and auth state
 */

class AuthService {
    constructor() {
        this.TOKEN_KEY = 'dream_decoder_token';
        this.USER_KEY = 'dream_decoder_user';
        this.DEFAULT_RENDER_BACKEND_URL = 'https://dream-decoder-7fy3.onrender.com';
    }

    /**
     * Helper to make fetch requests with API_BASE and error handling
     */
    async _fetch(endpoint, options) {
        try {
            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const isRenderHost = window.location.hostname.endsWith('.onrender.com');
            const runtimeBase = (typeof window !== 'undefined' && window.DREAM_DECODER_API_BASE)
                ? window.DREAM_DECODER_API_BASE
                : '';
            const baseUrl = typeof API_BASE !== 'undefined'
                ? API_BASE
                : ((isLocal || isRenderHost) ? '' : (runtimeBase || this.DEFAULT_RENDER_BACKEND_URL).replace(/\/+$/, ''));
            const url = `${baseUrl}${endpoint}`;
            const response = await fetch(url, options);
            response.__requestUrl = url;
            return response;
        } catch (error) {
            if (error.message === 'Failed to fetch') {
                throw new Error('Could not connect to the server. Please ensure the backend is running.');
            }
            throw error;
        }
    }

    /**
     * Safely parse API responses that may not be JSON on error pages.
     */
    async _parseResponse(response) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            return await response.json();
        }

        const text = await response.text();
        if (!response.ok) {
            if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                const requestUrl = response.__requestUrl || 'unknown URL';
                throw new Error(`Server returned HTML instead of JSON from ${requestUrl}. Backend URL is incorrect or endpoint is missing.`);
            }
            throw new Error(text || 'Unexpected server response');
        }

        return { message: text };
    }

    /**
     * Get stored authentication token
     */
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    /**
     * Get stored user data
     */
    getUser() {
        const userJson = localStorage.getItem(this.USER_KEY);
        return userJson ? JSON.parse(userJson) : null;
    }

    /**
     * Save authentication data
     */
    saveAuth(token, user) {
        localStorage.setItem(this.TOKEN_KEY, token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    }

    /**
     * Clear authentication data
     */
    clearAuth() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Sign up a new user
     */
    async signup(username, email, password, languagePreference = 'en') {
        const response = await this._fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password,
                language_preference: languagePreference
            })
        });

        const data = await this._parseResponse(response);

        if (!response.ok) {
            throw new Error(data.error || 'Signup failed');
        }

        // Save auth data
        this.saveAuth(data.token, data.user);

        return data;
    }

    /**
     * Log in an existing user
     */
    async login(usernameOrEmail, password) {
        const response = await this._fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: usernameOrEmail,
                password
            })
        });

        const data = await this._parseResponse(response);

        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }

        // Save auth data
        this.saveAuth(data.token, data.user);

        return data;
    }

    /**
     * Log out the current user
     */
    async logout() {
        const token = this.getToken();

        if (token) {
            try {
                await this._fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Logout request failed:', error);
            }
        }

        // Clear local auth data
        this.clearAuth();
    }

    /**
     * Delete user account
     */
    async deleteAccount() {
        const token = this.getToken();

        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await this._fetch('/api/auth/account', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await this._parseResponse(response);

        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete account');
        }

        // Clear auth data
        this.clearAuth();

        return data;
    }

    /**
     * Get current user info from server
     */
    async getCurrentUser() {
        const token = this.getToken();

        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await this._fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await this._parseResponse(response);

        if (!response.ok) {
            // Token might be expired
            if (response.status === 401) {
                this.clearAuth();
            }
            throw new Error(data.error || 'Failed to get user info');
        }

        // Update stored user data
        localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));

        return data.user;
    }

    /**
     * Update language preference
     */
    async updateLanguage(language) {
        const token = this.getToken();

        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await this._fetch('/api/auth/language', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language })
        });

        const data = await this._parseResponse(response);

        if (!response.ok) {
            throw new Error(data.error || 'Failed to update language');
        }

        // Update stored user data
        localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));

        return data.user;
    }

    /**
     * Add Authorization header to fetch options
     */
    getAuthHeaders() {
        const token = this.getToken();
        return token ? {
            'Authorization': `Bearer ${token}`
        } : {};
    }
}

// Create singleton instance
const authService = new AuthService();
