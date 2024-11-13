// auth.js - Load this file FIRST
console.log('Auth.js is loading...');
document.addEventListener('DOMContentLoaded', function() {
    // Add axios interceptor to automatically add the token to all requests
    axios.interceptors.request.use(function (config) {
        const token = localStorage.getItem('token');
        console.log("Token _ auth:", token);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    }, function (error) {
        return Promise.reject(error);
    });
});

// Helper functions that can be used across files
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

function handleLogout() {
    localStorage.removeItem('token');
    window.location.href = '/login/';
}
