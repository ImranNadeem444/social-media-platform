import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import { SocialAccount, PostWithTargets } from '../types'
import { socialAccountsService } from '../services/socialAccountsService'
import { postsService } from '../services/postsService'
import { FaInstagram, FaFacebook } from 'react-icons/fa'

type TargetPlatform = 'instagram' | 'facebook' | 'all'

export const CreatePost: React.FC = () => {
  const navigate = useNavigate()

  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [selectedTarget, setSelectedTarget] = useState<TargetPlatform>('all')
  const [caption, setCaption] = useState('')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [publishResult, setPublishResult] = useState<PostWithTargets | null>(null)

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    try {
      const data = await socialAccountsService.getSocialAccounts()

      const supportedAccounts = data.filter((account) => {
        const platform = account.platform.toLowerCase()
        return platform === 'instagram' || platform === 'facebook'
      })

      setAccounts(supportedAccounts)
    } catch (err) {
      console.error('Error loading social accounts:', err)
      setError('Failed to load your social accounts')
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]

    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Image size must be less than 10MB')
      return
    }

    setSelectedImage(file)
    setError(null)
    setPublishResult(null)

    const reader = new FileReader()
    reader.onload = (event) => {
      setImagePreview(event.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handlePublish = async () => {
    if (!selectedImage) {
      setError('Please select an image')
      return
    }

    setIsLoading(true)
    setError(null)
    setPublishResult(null)

    try {
      const result = await postsService.createPost(
        selectedTarget,
        caption || null,
        selectedImage
      )

      setPublishResult(result)

      // Reset form only if fully successful
      if (result.status === 'published') {
        setCaption('')
        setSelectedImage(null)
        setImagePreview(null)
      }
    } catch (err) {
      console.error('Error publishing post:', err)
      const errorMsg =
        err instanceof Error ? err.message : 'Failed to publish post'
      setError(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const instagramAccounts = accounts.filter(
    (a) => a.platform.toLowerCase() === 'instagram'
  )

  const facebookAccounts = accounts.filter(
    (a) => a.platform.toLowerCase() === 'facebook'
  )

  const hasInstagram = instagramAccounts.length > 0
  const hasFacebook = facebookAccounts.length > 0

  if (accounts.length === 0) {
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Create Post</h1>
            <p className="text-gray-600 mt-2">
              Share content to your connected social media accounts
            </p>
          </div>

          <Alert
            type="warning"
            title="No Social Accounts"
            message="Please connect an Instagram or Facebook account first before creating a post."
          />

          <div className="mt-6">
            <Button onClick={() => navigate('/accounts')}>
              Go to Accounts
            </Button>
          </div>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Post</h1>
          <p className="text-gray-600 mt-2">
            Share content to your connected social media accounts
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          {/* Image Upload */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Image *
            </label>

            {!imagePreview ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  disabled={isLoading}
                  className="hidden"
                  id="image-input"
                />

                <label htmlFor="image-input" className="cursor-pointer block">
                  <p className="text-gray-600 text-lg mb-2">
                    📷 Click to upload an image
                  </p>
                  <p className="text-gray-500 text-sm">
                    PNG, JPG, GIF or WebP (max 10MB)
                  </p>
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative w-full bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-auto max-h-96 object-contain"
                  />
                </div>

                <Button
                  variant="secondary"
                  onClick={() => {
                    setImagePreview(null)
                    setSelectedImage(null)
                  }}
                  disabled={isLoading}
                >
                  Change Image
                </Button>
              </div>
            )}
          </div>

          {/* Caption */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Caption
            </label>

            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              disabled={isLoading}
              placeholder="Write your caption here..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 resize-none"
            />
          </div>

          {/* Platform Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Post to *
            </label>

            <div className="flex gap-3 flex-wrap">
              {hasInstagram && (
                <button
                  onClick={() => setSelectedTarget('instagram')}
                  disabled={isLoading}
                  title="Post to Instagram"
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedTarget === 'instagram'
                      ? 'bg-pink-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  } disabled:opacity-50`}
                >
                  <FaInstagram />
                  Instagram
                </button>
              )}

              {hasFacebook && (
                <button
                  onClick={() => setSelectedTarget('facebook')}
                  disabled={isLoading}
                  title="Post to Facebook"
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedTarget === 'facebook'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  } disabled:opacity-50`}
                >
                  <FaFacebook />
                  Facebook
                </button>
              )}

              {hasInstagram && hasFacebook && (
                <button
                  onClick={() => setSelectedTarget('all')}
                  disabled={isLoading}
                  title="Post to all platforms"
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedTarget === 'all'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  } disabled:opacity-50`}
                >
                  <FaInstagram />
                  <FaFacebook />
                  All
                </button>
              )}
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6">
              <Alert type="error" title="Error" message={error} />
            </div>
          )}

          {/* Publishing Results */}
          {publishResult && (
            <div className="mb-6 bg-gray-50 rounded-lg p-6 border border-gray-200">
              <h3 className="font-semibold text-lg mb-4">
                {publishResult.status === 'published'
                  ? '✅ Publishing Complete'
                  : publishResult.status === 'partial'
                    ? '⚠️ Partial Success'
                    : '❌ Publishing Failed'}
              </h3>

              <div className="space-y-3">
                {publishResult.targets.map((target) => {
                  const platformName =
                    target.platform.charAt(0).toUpperCase() +
                    target.platform.slice(1)
                  const accountDisplay = target.account_name
                    ? `${platformName} — ${target.account_name}`
                    : target.account_id
                      ? `${platformName} — @${target.account_id}`
                      : platformName

                  return (
                    <div key={target.id} className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {target.status === 'published' ? (
                          <span className="text-green-500 font-bold">✓</span>
                        ) : (
                          <span className="text-red-500 font-bold">✗</span>
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">
                          {accountDisplay}
                        </p>
                        {target.status === 'published' ? (
                          <p className="text-sm text-green-600">Published</p>
                        ) : (
                          <p className="text-sm text-red-600">
                            {target.error_message || 'Publishing failed'}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Publish Button */}
          <div className="flex gap-4">
            <Button
              onClick={handlePublish}
              isLoading={isLoading}
              disabled={isLoading || !selectedImage}
            >
              Publish
            </Button>

            <Button
              variant="secondary"
              onClick={() => navigate('/dashboard')}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </AppShell>
  )
}