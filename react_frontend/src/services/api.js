import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getFarm = (farmId) =>
  api.get(`/farms/${farmId}`)

export const getFarmLocation = (farmId) =>
  api.get(`/farms/${farmId}/location`)

export const collectFarmFeatures = (farmId, cycleId, observationDate) =>
  api.get(
    `/farms/${farmId}/cycles/${cycleId}/features`,
    { params: { observation_date: observationDate } }
  )

export const createPrediction = (farmId, cycleId) =>
  api.post(`/predictions/farms/${farmId}/cycles/${cycleId}/predict`)

export const getFarmPredictions = (farmId) =>
  api.get(`/predictions/farms/${farmId}/predictions`)

export default api