import apiClient from './client'
import type { User, UserCreate, UserUpdate } from '@/types'

export const usersApi = {
  getAll: () => apiClient.get<User[]>('/users/'),
  getById: (id: number) => apiClient.get<User>(`/users/${id}`),
  create: (data: UserCreate) => apiClient.post<User>('/users/', data),
  update: (id: number, data: UserUpdate) => apiClient.patch<User>(`/users/${id}`, data),
  delete: (id: number) => apiClient.delete(`/users/${id}`)
}
