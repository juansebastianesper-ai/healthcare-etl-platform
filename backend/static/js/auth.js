const API_BASE = '/api';

function getTokens() {
    return {
        access: localStorage.getItem('access_token'),
        refresh: localStorage.getItem('refresh_token'),
    };
}

function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

async function fetchJWT() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const response = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (response.ok) {
            const data = await response.json();
            setTokens(data.access, data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
        }
    } catch (e) {
        console.warn('JWT fetch failed, session auth used instead');
    }
}

function getCSRFToken() {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

async function apiRequest(url, options = {}) {
    const tokens = getTokens();
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
        ...options.headers,
    };

    if (tokens.access) {
        headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    const config = { ...options, headers, credentials: 'include' };

    if (options.body && !(options.body instanceof FormData)) {
        config.body = JSON.stringify(options.body);
    }

    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
        config.body = options.body;
    }

    let response = await fetch(`${API_BASE}${url}`, config);

    if (response.status === 401 && tokens.refresh) {
        const refreshed = await refreshToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getTokens().access}`;
            config.headers = headers;
            response = await fetch(`${API_BASE}${url}`, config);
        } else {
            clearTokens();
            window.location.href = '/login/';
            return null;
        }
    }

    return response;
}

async function refreshToken() {
    try {
        const response = await fetch(`${API_BASE}/auth/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: getTokens().refresh }),
        });
        if (response.ok) {
            const data = await response.json();
            setTokens(data.access, data.refresh);
            return true;
        }
        clearTokens();
        return false;
    } catch {
        clearTokens();
        return false;
    }
}

function logout() {
    fetch('/logout/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() },
        credentials: 'include',
    }).finally(() => {
        clearTokens();
        window.location.href = '/login/';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const btn = loginForm.querySelector('button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Ingresando...';
            await fetchJWT();
            loginForm.submit();
        });
    }
});
