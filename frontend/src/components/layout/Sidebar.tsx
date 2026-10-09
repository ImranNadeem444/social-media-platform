import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

interface NavItem {
  label: string
  path: string
  icon: string
  disabled?: boolean
  comingSoon?: boolean
}

const mainNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Accounts', path: '/accounts', icon: '👤' },
  { label: 'Create Post', path: '/create-post', icon: '✏️' },
  { label: 'Posts', path: '/posts', icon: '📝', comingSoon: true },
]

const bottomNavItems: NavItem[] = [
  { label: 'Settings', path: '/settings', icon: '⚙️' },
]

export const Sidebar: React.FC = () => {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)

  const handleLogout = () => {
    logout()
  }

  const isActive = (path: string) => location.pathname === path

  const navItemClasses = (active: boolean, disabled: boolean = false) => `
    flex items-center gap-3 px-4 py-3 text-base rounded-lg transition-all
    ${disabled ? 'opacity-50 cursor-not-allowed text-gray-500' : ''}
    ${!disabled && active ? 'bg-primary-50 text-primary-700 font-medium' : ''}
    ${!disabled && !active ? 'text-gray-700 hover:bg-gray-100' : ''}
  `

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden md:flex flex-col w-64 bg-white border-r border-gray-200 fixed left-0 top-0 h-screen">
        {/* Logo */}
        <div className="px-6 py-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Social Media Manager</h2>
          <p className="text-xs text-gray-500 mt-1">Professional Edition</p>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-3 py-6 space-y-1">
          {mainNavItems.map((item) => {
            const disabled = item.comingSoon
            const content = (
              <>
                <span className="text-lg">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {item.comingSoon && (
                  <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                    Soon
                  </span>
                )}
              </>
            )

            if (disabled) {
              return (
                <div
                  key={item.path}
                  className={`flex items-center gap-3 px-4 py-3 text-base rounded-lg ${navItemClasses(false, true)}`}
                >
                  {content}
                </div>
              )
            }

            return (
              <Link
                key={item.path}
                to={item.path}
                className={navItemClasses(isActive(item.path), disabled)}
              >
                {content}
              </Link>
            )
          })}
        </nav>

        {/* Separator */}
        <div className="px-3 py-2">
          <div className="h-px bg-gray-200" />
        </div>

        {/* Bottom Navigation */}
        <nav className="px-3 py-4 space-y-1 border-b border-gray-200">
          {bottomNavItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={navItemClasses(isActive(item.path))}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User Profile */}
        {user && (
          <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-medium text-sm">
                {user.email.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.email}
                </p>
                <p className="text-xs text-gray-500">Account</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-200 rounded-lg transition-colors text-left"
            >
              Sign out
            </button>
          </div>
        )}
      </div>

      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-50"
        aria-label="Toggle menu"
      >
        <span className="text-xl">☰</span>
      </button>

      {/* Mobile Sidebar */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setIsOpen(false)} />
      )}
      <div
        className={`
          md:hidden fixed left-0 top-0 h-screen w-64 bg-white z-40 transform transition-transform
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="px-6 py-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Social Media Manager</h2>
        </div>

        {/* Main Navigation */}
        <nav className="px-3 py-6 space-y-1">
          {mainNavItems.map((item) => {
            const disabled = item.comingSoon
            const content = (
              <>
                <span className="text-lg">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {item.comingSoon && (
                  <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                    Soon
                  </span>
                )}
              </>
            )

            if (disabled) {
              return (
                <div
                  key={item.path}
                  className={`flex items-center gap-3 px-4 py-3 text-base rounded-lg ${navItemClasses(false, true)}`}
                >
                  {content}
                </div>
              )
            }

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={navItemClasses(isActive(item.path), disabled)}
              >
                {content}
              </Link>
            )
          })}
        </nav>

        {/* Separator */}
        <div className="px-3 py-2">
          <div className="h-px bg-gray-200" />
        </div>

        {/* Bottom Navigation */}
        <nav className="px-3 py-4 space-y-1">
          {bottomNavItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={navItemClasses(isActive(item.path))}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User Profile */}
        {user && (
          <div className="absolute bottom-0 left-0 right-0 px-4 py-4 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-medium text-sm">
                {user.email.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                handleLogout()
                setIsOpen(false)
              }}
              className="w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-200 rounded-lg transition-colors text-left"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </>
  )
}
