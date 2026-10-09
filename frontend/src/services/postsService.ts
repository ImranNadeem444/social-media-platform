import api from './api'
import { PostWithTargets } from '../types'

export const postsService = {
  async createPost(
    target: 'instagram' | 'facebook' | 'all',
    caption: string | null,
    image: File
  ): Promise<PostWithTargets> {
    const formData = new FormData()
    formData.append('target', target)
    if (caption) {
      formData.append('caption', caption)
    }
    formData.append('image', image)

    const response = await api.post<PostWithTargets>('/posts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
