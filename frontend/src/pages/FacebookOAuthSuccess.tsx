import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'

export default function FacebookOAuthSuccess() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)

  const message = searchParams.get('message') || 'Facebook authorization completed'

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6 flex justify-center text-6xl">
          ✓
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Success!
        </h1>

        <p className="text-gray-700 mb-4">
          {decodeURIComponent(message)}
        </p>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-green-800">
            ✓ Pages are encrypted and secure<br/>
            ✓ Ready to publish<br/>
            ✓ Tokens are server-side only
          </p>
        </div>

        {loading ? (
          <p className="text-gray-600 text-sm mb-4">
            Redirecting to dashboard...
          </p>
        ) : null}

        <Button
          onClick={() => navigate('/dashboard')}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
        >
          Go to Dashboard
        </Button>

        <p className="text-xs text-gray-500 mt-4">
          This page will auto-redirect in a moment.
        </p>
      </div>
    </div>
  )
}
