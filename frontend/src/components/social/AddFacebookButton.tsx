import { useState } from 'react'
import { Button } from '../ui/Button'
import api from '../../services/api'
import AuthorizationLinkDisplay from './AuthorizationLinkDisplay'

interface AuthorizeResponse {
  authorization_url: string
}

export const AddFacebookButton: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [authorizationUrl, setAuthorizationUrl] = useState<string | null>(null)
  const [showLink, setShowLink] = useState(false)

  const handleAddFacebook = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await api.get<AuthorizeResponse>(
        '/social-accounts/facebook/authorize'
      )
      const { authorization_url } = response.data

      if (!authorization_url) {
        setError('Failed to get authorization URL. Please try again.')
        setIsLoading(false)
        return
      }

      setAuthorizationUrl(authorization_url)
      setShowLink(true)
      setIsLoading(false)
    } catch (err) {
      console.error('Error getting Facebook authorization URL:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to connect Facebook. Please try again.'
      )
      setIsLoading(false)
    }
  }

  const handleDirectAuth = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await api.get<AuthorizeResponse>(
        '/social-accounts/facebook/authorize'
      )
      const { authorization_url } = response.data

      if (!authorization_url) {
        setError('Failed to get authorization URL. Please try again.')
        setIsLoading(false)
        return
      }

      window.location.href = authorization_url
    } catch (err) {
      console.error('Error getting Facebook authorization URL:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to connect Facebook. Please try again.'
      )
      setIsLoading(false)
    }
  }

  if (showLink && authorizationUrl) {
    return (
      <div className="space-y-4">
        <AuthorizationLinkDisplay url={authorizationUrl} platform="facebook" />
        <div className="flex gap-2">
          <Button
            onClick={handleDirectAuth}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            Authorize Myself
          </Button>
          <Button
            onClick={() => {
              setShowLink(false)
              setAuthorizationUrl(null)
            }}
            className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800"
          >
            Done
          </Button>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center">
          <p className="text-sm text-red-700 mb-4">{error}</p>
          <Button
            onClick={handleAddFacebook}
            isLoading={isLoading}
            disabled={isLoading}
          >
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-4xl">👥</span>
          <div>
            <h3 className="font-semibold text-gray-900">Connect Facebook</h3>
            <p className="text-sm text-gray-600 mt-1">
              Link your Facebook Business Pages or share a link to authorize on behalf of someone else
            </p>
          </div>
        </div>
        <Button
          onClick={handleAddFacebook}
          isLoading={isLoading}
          disabled={isLoading}
        >
          Connect
        </Button>
      </div>
    </div>
  )
}
