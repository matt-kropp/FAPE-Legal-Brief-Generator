import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/check_auth')
      setIsAuthenticated(true)
      setUser(response.data.user)
    } catch (error) {
      setIsAuthenticated(false)
      setUser(null)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/login', { username, password })
      setIsAuthenticated(true)
      setUser(response.data.user)
      return true
    } catch (error) {
      return false
    }
  }

  const logout = async () => {
    try {
      await axios.get('/api/logout')
      setIsAuthenticated(false)
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
