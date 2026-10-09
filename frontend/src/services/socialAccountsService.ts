import api from './api'
import { SocialAccount } from '../types'

export interface AuthorizationUrlResponse {
  authorization_url: string
}

export const socialAccountsService = {
  async getSocialAccounts(): Promise<SocialAccount[]> {
    const response = await api.get<SocialAccount[]>('/social-accounts')
    return response.data
  },

  async getInstagramAuthorizationUrl(): Promise<AuthorizationUrlResponse> {
    const response = await api.get<AuthorizationUrlResponse>('/social-accounts/instagram/authorize')
    return response.data
  },

  async disconnectAccount(socialAccountId: number): Promise<void> {
    await api.delete(`/social-accounts/${socialAccountId}`)
  },
}
