import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './router/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { Accounts } from './pages/Accounts'
import { CreatePost } from './pages/CreatePost'
import { FacebookPageSelector } from './pages/FacebookPageSelector'
import InstagramOAuthSuccess from './pages/InstagramOAuthSuccess'
import InstagramOAuthError from './pages/InstagramOAuthError'
import FacebookOAuthSuccess from './pages/FacebookOAuthSuccess'
import FacebookOAuthError from './pages/FacebookOAuthError'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/instagram/success" element={<InstagramOAuthSuccess />} />
          <Route path="/instagram/error" element={<InstagramOAuthError />} />
          <Route path="/facebook/success" element={<FacebookOAuthSuccess />} />
          <Route path="/facebook/error" element={<FacebookOAuthError />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounts"
            element={
              <ProtectedRoute>
                <Accounts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/facebook/select-pages"
            element={
              <ProtectedRoute>
                <FacebookPageSelector />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-post"
            element={
              <ProtectedRoute>
                <CreatePost />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
