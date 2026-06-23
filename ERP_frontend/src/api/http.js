import axios from 'axios'

const http = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

function processQueue(error) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve()
  })
  failedQueue = []
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => http(original)).catch((e) => Promise.reject(e))
      }
      original._retry = true
      isRefreshing = true
      try {
        // TODO: confirm backend exposes this auth endpoint
        await axios.post(
          'http://localhost:8000/dj-rest-auth/token/refresh/',
          {},
          { withCredentials: true },
        )
        processQueue(null)
        return http(original)
      } catch (refreshError) {
        processQueue(refreshError)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  },
)

export default http
