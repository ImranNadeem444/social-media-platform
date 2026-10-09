import { AppShell } from '../components/layout/AppShell'
import { useAuth } from '../hooks/useAuth'
import { socialAccountsService } from '../services/socialAccountsService'
import { SocialAccount } from '../types'
import { useState, useEffect } from 'react'
import { FaInstagram, FaFacebook } from 'react-icons/fa'

export const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(true)

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

  const instagramCount = accounts.filter(
    (a) => a.platform.toLowerCase() === 'instagram'
  ).length

  const facebookCount = accounts.filter(
    (a) => a.platform.toLowerCase() === 'facebook'
  ).length

  const StatCard: React.FC<{
    icon: React.ReactNode
    label: string
    value: number
    isLoading: boolean
  }> = ({ icon, label, value, isLoading }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-4">
        <div className="text-4xl text-gray-600">{icon}</div>
        <div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-4xl font-bold text-gray-900 mt-1">
            {isLoading ? '—' : value}
          </p>
        </div>
      </div>
    </div>
  )

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-3">
            Welcome back, {user?.email}. Manage your social media accounts from the Accounts page.
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            icon={<span className="text-gray-400">📊</span>}
            label="Total Connections"
            value={accounts.length}
            isLoading={isLoading}
          />
          <StatCard
            icon={<FaInstagram className="text-pink-600" />}
            label="Instagram"
            value={instagramCount}
            isLoading={isLoading}
          />
          <StatCard
            icon={<FaFacebook className="text-blue-600" />}
            label="Facebook"
            value={facebookCount}
            isLoading={isLoading}
          />
        </div>
      </div>
    </AppShell>
  )
}
