import { useState } from 'react'
import { Button } from '../ui/Button'

interface AuthorizationLinkDisplayProps {
  url: string
  platform: 'instagram' | 'facebook'
}

export default function AuthorizationLinkDisplay({ url, platform }: AuthorizationLinkDisplayProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const platformName = platform.charAt(0).toUpperCase() + platform.slice(1)

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-blue-900 mb-3">
        Share {platformName} Authorization Link
      </h3>

      <p className="text-blue-800 text-sm mb-4">
        Copy this link and share it with the person who owns the {platformName} account.
        They will authorize the connection on their own device. No password needed.
      </p>

      <div className="bg-white border border-blue-300 rounded p-3 mb-4 flex items-center justify-between">
        <code className="text-sm text-gray-700 overflow-auto flex-1 break-all">
          {url}
        </code>
      </div>

      <Button
        onClick={handleCopy}
        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
      >
        {copied ? (
          <>
            ✓ Copied!
          </>
        ) : (
          <>
            📋 Copy Link
          </>
        )}
      </Button>

      <div className="mt-4 p-3 bg-blue-100 rounded text-sm text-blue-900">
        <p className="font-semibold mb-2">Instructions for the account owner:</p>
        <ol className="list-decimal list-inside space-y-1">
          <li>Click the link (works on phone or computer)</li>
          <li>Log in to {platformName} if needed</li>
          <li>Click "Allow" to authorize the connection</li>
          <li>The account will automatically appear in your dashboard</li>
        </ol>
      </div>
    </div>
  )
}
