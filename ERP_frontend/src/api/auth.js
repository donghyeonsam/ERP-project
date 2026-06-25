import axios from 'axios'
import http from './http'

export const authApi = {
  login: (username, password) =>
    axios.post(`/dj-rest-auth/login/`, { username, password }, { withCredentials: true }),

  logout: () =>
    axios.post(`/dj-rest-auth/logout/`, {}, { withCredentials: true }),

  register: (data) =>
    axios.post(`/dj-rest-auth/registration/`, data, { withCredentials: true }),

  refreshToken: () =>
    axios.post(`/dj-rest-auth/token/refresh/`, {}, { withCredentials: true }),

  getMe: () => http.get('employees/me/'),
}