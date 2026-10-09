import { useSearchParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'

export default function InstagramOAuthError() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const error = searchParams.get('error') || 'An unknown error occurred'

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6 flex justify-center text-6xl">
          ✕
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Authorization Failed
        </h1>

        <p className="text-gray-700 mb-4">
          Could not connect your Instagram account.
        </p>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-800 break-words">
            <strong>Error:</strong> {decodeURIComponent(error)}
          </p>
        </div>

        <div className="space-y-2">
          <Button
            onClick={() => navigate('/accounts')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            Try Again
          </Button>
          <Button
            onClick={() => navigate('/dashboard')}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800"
          >
            Go to Dashboard
          </Button>
        </div>

        <p className="text-xs text-gray-500 mt-4">
          If the problem persists, please contact support.
        </p>
      </div>
    </div>
  )
}
