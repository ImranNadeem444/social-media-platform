import React from 'react'
import { useLocation } from 'react-router-dom'

const pageNames: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/accounts': 'Accounts',
  '/create': 'Create Post',
  '/posts': 'Posts',
  '/settings': 'Settings',
}

export const Header: React.FC = () => {
  const location = useLocation()
  const pageTitle = pageNames[location.pathname] || 'Dashboard'

  return (
    <div className="hidden md:block fixed top-0 left-64 right-0 h-16 bg-white border-b border-gray-200 z-30">
      <div className="h-full px-8 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">{pageTitle}</h1>
      </div>
    </div>
  )
}
