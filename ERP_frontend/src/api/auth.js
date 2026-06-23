import axios from 'axios'
import http from './http'

const AUTH_BASE = 'http://localhost:8000'

// TODO: confirm backend exposes these auth endpoints at /dj-rest-auth/
export const authApi = {
  login: (username, password) =>
    axios.post(`${AUTH_BASE}/dj-rest-auth/login/`, { username, password }, { withCredentials: true }),

  logout: () =>
    axios.post(`${AUTH_BASE}/dj-rest-auth/logout/`, {}, { withCredentials: true }),

  register: (data) =>
    axios.post(`${AUTH_BASE}/dj-rest-auth/registration/`, data, { withCredentials: true }),

  refreshToken: () =>
    axios.post(`${AUTH_BASE}/dj-rest-auth/token/refresh/`, {}, { withCredentials: true }),

  getMe: () => http.get('employees/me/'),
}
