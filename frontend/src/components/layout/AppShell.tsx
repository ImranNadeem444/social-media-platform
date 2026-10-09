import React from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface AppShellProps {
  children: React.ReactNode
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <Header />

      {/* Main Content */}
      <main className="flex-1 md:ml-64 md:mt-16">
        <div className="p-6 md:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
