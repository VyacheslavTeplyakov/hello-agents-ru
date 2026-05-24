import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Таймаут 2 минуты
  headers: {
    'Content-Type': 'application/json'
  }
})

// Перехватчик запросов
apiClient.interceptors.request.use(
  (config) => {
    console.log('Отправка запроса:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Ошибка запроса:', error)
    return Promise.reject(error)
  }
)

// Перехватчик ответов
apiClient.interceptors.response.use(
  (response) => {
    console.log('Получен ответ:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('Ошибка ответа:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

/**
 * Сформировать план путешествия
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    return response.data
  } catch (error: any) {
    console.error('Ошибка формирования плана путешествия:', error)
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка формирования плана путешествия')
  }
}

/**
 * Проверка работоспособности
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('Ошибка проверки работоспособности:', error)
    throw new Error(error.message || 'Ошибка проверки работоспособности')
  }
}

export default apiClient
