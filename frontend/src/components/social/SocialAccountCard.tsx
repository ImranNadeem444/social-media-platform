import React from 'react'
import { SocialAccount } from '../../types'

interface SocialAccountCardProps {
  account: SocialAccount
}

const platformIcons: Record<string, string> = {
  instagram: '📷',
  facebook: '👥',
  twitter: '🐦',
  linkedin: '💼',
}

const getPlatformDisplay = (platform: string) => {
  return platform.charAt(0).toUpperCase() + platform.slice(1)
}

export const SocialAccountCard: React.FC<SocialAccountCardProps> = ({ account }) => {
  const icon = platformIcons[account.platform.toLowerCase()] || '🔗'
  const connectedDate = new Date(account.created_at)
  const dateString = connectedDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{icon}</span>
          <div>
            <h3 className="font-semibold text-gray-900">
              {getPlatformDisplay(account.platform)}
            </h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-sm font-medium text-green-700">Connected</span>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-600">Account</p>
          <p className="font-medium text-gray-900">
            {account.account_name || `@${account.account_id}`}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-500">
            Connected {dateString}
          </p>
        </div>
      </div>
    </div>
  )
}
