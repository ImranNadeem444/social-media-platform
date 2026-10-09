export interface User {
  id: number
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface SocialAccount {
  id: number
  platform: string
  account_id: string
  account_name: string | null
  token_expires_at: string | null
  created_at: string
  updated_at: string
}

export interface PostTarget {
  id: number
  post_id: number
  social_account_id: number
  platform: string
  account_name: string | null
  account_id: string | null
  status: string
  platform_media_id: string | null
  platform_post_id: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface Post {
  id: number
  user_id: number
  social_account_id: number
  platform: string
  caption: string | null
  image_path: string
  status: string
  instagram_media_id: string | null
  facebook_post_id: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface PostWithTargets {
  id: number
  user_id: number
  caption: string | null
  image_path: string
  status: string
  targets: PostTarget[]
  created_at: string
  updated_at: string
}

export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export interface ApiError {
  detail: string | string[]
  status?: number
}
