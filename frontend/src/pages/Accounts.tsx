import { AppShell } from '../components/layout/AppShell'
import { AddInstagramButton } from '../components/social/AddInstagramButton'
import { AddFacebookButton } from '../components/social/AddFacebookButton'
import { socialAccountsService } from '../services/socialAccountsService'
import { SocialAccount } from '../types'
import { useState, useEffect } from 'react'
import { FaInstagram, FaFacebook } from 'react-icons/fa'

export const Accounts: React.FC = () => {
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [disconnectingId, setDisconnectingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    try {
      const data = await socialAccountsService.getSocialAccounts()
      setAccounts(data)
    } catch (error) {
      console.error('Error loading social accounts:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async (accountId: number) => {
    setDisconnectingId(accountId)
    setError(null)
    try {
      await socialAccountsService.disconnectAccount(accountId)
      await loadAccounts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect account')
    } finally {
      setDisconnectingId(null)
    }
  }

  const instagramAccounts = accounts.filter(
    (a) => a.platform.toLowerCase() === 'instagram'
  )
  const facebookAccounts = accounts.filter(
    (a) => a.platform.toLowerCase() === 'facebook'
  )

  const PlatformSection: React.FC<{
    title: string
    icon: React.ReactNode
    accounts: SocialAccount[]
    addButton: React.ReactNode
  }> = ({ title, icon, accounts, addButton }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="text-4xl">{icon}</div>
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      </div>

      {isLoading ? (
        <div className="py-12 text-center">
          <p className="text-gray-500">Loading accounts...</p>
        </div>
      ) : accounts.length > 0 ? (
        <>
          <div className="space-y-3 mb-6">
            {accounts.map((account) => (
              <div
                key={account.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {account.account_name || `@${account.account_id}`}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Connected{' '}
                    {new Date(account.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                </div>
                <button
                  onClick={() => handleDisconnect(account.id)}
                  disabled={disconnectingId === account.id}
                  className="ml-4 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {disconnectingId === account.id ? 'Removing...' : 'Remove'}
                </button>
              </div>
            ))}
          </div>
          <div className="border-t border-gray-200 pt-6">
            {addButton}
          </div>
        </>
      ) : (
        <div className="py-12 text-center">
          <p className="text-gray-500 mb-6">
            No {title.toLowerCase()} accounts connected yet.
          </p>
          {addButton}
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  )

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Connected Accounts</h1>
          <p className="text-gray-600 mt-3">
            Manage your Instagram and Facebook accounts in one place.
          </p>
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Instagram Section */}
          <PlatformSection
            title="Instagram"
            icon={<FaInstagram className="text-pink-600" />}
            accounts={instagramAccounts}
            addButton={<AddInstagramButton />}
          />

          {/* Facebook Section */}
          <PlatformSection
            title="Facebook"
            icon={<FaFacebook className="text-blue-600" />}
            accounts={facebookAccounts}
            addButton={<AddFacebookButton />}
          />
        </div>
      </div>
    </AppShell>
  )
}
