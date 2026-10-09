import React, { useState } from 'react'
import { SocialAccount } from '../../types'
import { Button } from '../ui/Button'
import { ConfirmDialog } from '../ui/ConfirmDialog'
import { socialAccountsService } from '../../services/socialAccountsService'

interface PlatformCardProps {
  platform: string
  icon: string
  accounts: SocialAccount[]
  isComingSoon?: boolean
  onConnect?: () => Promise<void>
  onDisconnect?: (accountId: number) => Promise<void>
}

export const PlatformCard: React.FC<PlatformCardProps> = ({
  platform,
  icon,
  accounts,
  isComingSoon = false,
  onConnect,
  onDisconnect,
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [disconnectingId, setDisconnectingId] = useState<number | null>(null)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isDisconnecting, setIsDisconnecting] = useState(false)

  const handleConnect = async () => {
    if (isComingSoon || !onConnect) return

    setIsLoading(true)
    setError(null)

    try {
      await onConnect()
    } catch (err) {
      console.error(`Error connecting ${platform}:`, err)
      setError(
        err instanceof Error
          ? err.message
          : `Failed to connect ${platform}. Please try again.`
      )
      setIsLoading(false)
    }
  }

  const handleDisconnect = async (accountId: number) => {
    setIsDisconnecting(true)
    try {
      await socialAccountsService.disconnectAccount(accountId)
      setShowConfirm(false)
      setDisconnectingId(null)
      if (onDisconnect) {
        await onDisconnect(accountId)
      }
    } catch (err) {
      console.error(`Error disconnecting ${platform} account:`, err)
      setError(
        err instanceof Error
          ? err.message
          : `Failed to disconnect. Please try again.`
      )
    } finally {
      setIsDisconnecting(false)
    }
  }

  const platformDisplay = platform.charAt(0).toUpperCase() + platform.slice(1)
  const accountToDisconnect = accounts.find((a) => a.id === disconnectingId)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{icon}</span>
          <h3 className="text-lg font-semibold text-gray-900">
            {platformDisplay}
          </h3>
        </div>
      </div>

      {/* Connection Status */}
      <div className="mb-6">
        <p className="text-sm text-gray-600 mb-2">Connected</p>
        <p className="text-2xl font-bold text-gray-900">{accounts.length}</p>
      </div>

      {/* Connected Accounts List */}
      {accounts.length > 0 && (
        <div className="mb-6 space-y-3 pb-6 border-b border-gray-200">
          {accounts.map((account) => (
            <div key={account.id} className="space-y-2">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  <p className="font-medium text-gray-900">
                    {account.account_name || `@${account.account_id}`}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setDisconnectingId(account.id)
                    setShowConfirm(true)
                  }}
                  disabled={disconnectingId !== null}
                  className="text-xs text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
                >
                  Remove
                </button>
              </div>
              <p className="text-xs text-gray-500 ml-4">
                Connected{' '}
                {new Date(account.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 text-sm text-red-700 bg-red-50 rounded p-3">
          {error}
        </div>
      )}

      {/* Action Button */}
      <div className="flex gap-2">
        {isComingSoon ? (
          <Button disabled variant="secondary" className="flex-1">
            Coming Soon
          </Button>
        ) : (
          <Button
            onClick={handleConnect}
            isLoading={isLoading}
            disabled={isLoading}
            className="flex-1"
          >
            + Add {platformDisplay}
          </Button>
        )}
      </div>

      {/* Disconnect Confirmation Dialog */}
      {showConfirm && accountToDisconnect && (
        <ConfirmDialog
          title={`Disconnect ${accountToDisconnect.account_name || accountToDisconnect.account_id}?`}
          message="Your account will be removed from Social Media Manager."
          confirmText="Disconnect"
          cancelText="Cancel"
          isLoading={isDisconnecting}
          isDangerous={true}
          onConfirm={() => handleDisconnect(accountToDisconnect.id)}
          onCancel={() => {
            setShowConfirm(false)
            setDisconnectingId(null)
            setError(null)
          }}
        />
      )}
    </div>
  )
}
