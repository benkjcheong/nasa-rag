import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export const searchAPI = async (query, topK = 10) => {
  const response = await api.post('/search', {
    query,
    top_k: topK
  })
  return response.data
}

export const getMethodResults = async (query, topK = 10) => {
  const response = await api.post('/methods', {
    query,
    top_k: topK
  })
  return response.data
}