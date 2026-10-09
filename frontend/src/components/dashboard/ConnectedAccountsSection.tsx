import React, { useState, useEffect } from 'react'
import { SocialAccount } from '../../types'
import { socialAccountsService } from '../../services/socialAccountsService'
import { SocialAccountCard } from '../social/SocialAccountCard'
import { AddInstagramButton } from '../social/AddInstagramButton'

interface ConnectedAccountsSectionProps {
  refreshTrigger?: number
}

export const ConnectedAccountsSection: React.FC<ConnectedAccountsSectionProps> = ({
  refreshTrigger = 0,
}) => {
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAccounts()
  }, [refreshTrigger])

  const loadAccounts = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await socialAccountsService.getSocialAccounts()
      setAccounts(data)
    } catch (err) {
      console.error('Error loading social accounts:', err)
      setError('Unable to load your connected accounts.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Connected Accounts</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gray-200 rounded" />
                  <div>
                    <div className="h-5 w-24 bg-gray-200 rounded" />
                  </div>
                </div>
                <div className="h-4 w-16 bg-gray-200 rounded" />
              </div>
              <div className="space-y-3">
                <div className="h-4 w-32 bg-gray-200 rounded" />
                <div className="h-3 w-24 bg-gray-200 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Connected Accounts</h2>
        <div className="bg-white rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={loadAccounts}
            className="text-red-700 hover:text-red-900 font-medium underline"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  if (accounts.length === 0) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Connected Accounts</h2>
        <div className="text-center py-12">
          <p className="text-3xl mb-4">📱</p>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No social accounts connected
          </h3>
          <p className="text-gray-600 mb-8">
            Connect Instagram to start managing your social media accounts from one place.
          </p>
          <AddInstagramButton />
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Connected Accounts</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map((account) => (
          <SocialAccountCard key={account.id} account={account} />
        ))}
      </div>

      {/* Add Account Card */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Add Another Account
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AddInstagramButton />
        </div>
      </div>
    </div>
  )
}
