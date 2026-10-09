import React from 'react'
import { Link } from 'react-router-dom'

interface QuickAction {
  title: string
  description: string
  icon: string
  link: string
  disabled?: boolean
}

const actions: QuickAction[] = [
  {
    title: 'Create Post',
    description: 'Publish content across your accounts',
    icon: '✏️',
    link: '/create',
    disabled: true,
  },
  {
    title: 'View Posts',
    description: 'Manage your published posts',
    icon: '📝',
    link: '/posts',
    disabled: true,
  },
  {
    title: 'Connect Account',
    description: 'Add another social media account',
    icon: '🔗',
    link: '#connect-account',
    disabled: false,
  },
]

export const QuickActions: React.FC = () => {
  return (
    <div className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {actions.map((action) => {
          const baseClasses = `
            bg-white rounded-lg border border-gray-200 p-6
            transition-all
          `

          const content = (
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{action.title}</p>
                <p className="text-gray-900 font-semibold mt-2">
                  {action.description}
                </p>
              </div>
              <span className="text-3xl ml-4">{action.icon}</span>
            </div>
          )

          if (action.disabled) {
            return (
              <div key={action.title} className={`${baseClasses} opacity-50 cursor-not-allowed`}>
                {content}
                <p className="text-xs text-gray-500 mt-4">Coming soon</p>
              </div>
            )
          }

          if (action.link === '#connect-account') {
            return (
              <div key={action.title} className={`${baseClasses} hover:shadow-md cursor-pointer`}>
                {content}
              </div>
            )
          }

          return (
            <Link
              key={action.title}
              to={action.link}
              className={`${baseClasses} hover:shadow-md`}
            >
              {content}
            </Link>
          )
        })}
      </div>
    </div>
  )
}
