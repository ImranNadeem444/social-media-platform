import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import api from '../services/api'

interface FacebookPage {
  id: string
  name: string
  tasks?: string[]
}

interface PagesResponse {
  pages: FacebookPage[]
  selection_token: string
}

export const FacebookPageSelector: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [pages, setPages] = useState<FacebookPage[]>([])
  const [selectedPageIds, setSelectedPageIds] = useState<Set<string>>(new Set())
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectionToken = searchParams.get('selection_token')

  useEffect(() => {
    if (!selectionToken) {
      setError('Missing selection token. Please try again.')
      setIsLoading(false)
      return
    }

    loadPages()
  }, [selectionToken])

  const loadPages = async () => {
    if (!selectionToken) return

    try {
      setIsLoading(true)
      setError(null)
      const response = await api.get<PagesResponse>(
        `/social-accounts/facebook/pages?selection_token=${encodeURIComponent(selectionToken)}`
      )
      setPages(response.data.pages)

      if (response.data.pages.length === 0) {
        setError('No Facebook Pages available for this account.')
      }
    } catch (err) {
      console.error('Error loading Facebook pages:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to load Facebook pages'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const togglePageSelection = (pageId: string) => {
    const newSelected = new Set(selectedPageIds)
    if (newSelected.has(pageId)) {
      newSelected.delete(pageId)
    } else {
      newSelected.add(pageId)
    }
    setSelectedPageIds(newSelected)
  }

  const handleConnect = async () => {
    if (selectedPageIds.size === 0) {
      setError('Please select at least one page.')
      return
    }

    if (!selectionToken) {
      setError('Selection token missing.')
      return
    }

    try {
      setIsConnecting(true)
      setError(null)
      await api.post('/social-accounts/facebook/connect', {
        selection_token: selectionToken,
        selected_page_ids: Array.from(selectedPageIds),
      })
      navigate('/accounts')
    } catch (err) {
      console.error('Error connecting Facebook pages:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to connect pages'
      )
    } finally {
      setIsConnecting(false)
    }
  }

  if (isLoading) {
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto">
          <p className="text-center text-gray-600">Loading Facebook pages...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Connect Facebook Pages
          </h1>
          <p className="text-gray-600">
            Select the Pages you want to connect to Social Media Manager.
          </p>
        </div>

        {error && <div className="mb-6"><Alert type="error" message={error} /></div>}

        {pages.length > 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="space-y-4 mb-6">
              {pages.map((page) => (
                <label key={page.id} className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedPageIds.has(page.id)}
                    onChange={() => togglePageSelection(page.id)}
                    className="w-4 h-4"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{page.name}</p>
                    {page.tasks && page.tasks.length > 0 && (
                      <p className="text-sm text-gray-500 mt-1">
                        Permissions: {page.tasks.join(', ')}
                      </p>
                    )}
                  </div>
                </label>
              ))}
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleConnect}
                isLoading={isConnecting}
                disabled={selectedPageIds.size === 0 || isConnecting}
              >
                Connect Selected Pages ({selectedPageIds.size})
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/accounts')}
                disabled={isConnecting}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Alert
            type="warning"
            message="No Facebook Pages available for this account."
          />
        )}
      </div>
    </AppShell>
  )
}
