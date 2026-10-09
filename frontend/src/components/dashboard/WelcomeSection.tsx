import React from 'react'
import { useAuth } from '../../hooks/useAuth'

export const WelcomeSection: React.FC = () => {
  const { user } = useAuth()

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-gray-900">
        {getGreeting()}, {user?.email.split('@')[0]}
      </h1>
      <p className="text-gray-600 mt-2">
        Manage your connected social accounts and publish content from one place.
      </p>
    </div>
  )
}
