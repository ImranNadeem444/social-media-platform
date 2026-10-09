import api from './api'
import { User, AuthResponse } from '../types'

export interface RegisterResponse {
  id: number
  email: string
}

export const authService = {
  async register(email: string, password: string): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>('/auth/register', {
      email,
      password,
    })
    return response.data
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new URLSearchParams({
      username: email,
      password,
    })

    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  logout(): void {
    localStorage.removeItem('access_token')
  },
}
