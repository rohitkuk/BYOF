import { useState, useEffect } from 'react'
import axios from 'axios'

const BASE = ''

export function usePreferences() {
  const [preferences, setPreferences] = useState({ categories: [], subcategories: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`${BASE}/preferences`)
      .then(r => setPreferences(r.data))
      .finally(() => setLoading(false))
  }, [])

  const updatePreferences = async (data) => {
    await axios.post(`${BASE}/preferences`, data)
    setPreferences(data)
  }

  return { preferences, loading, updatePreferences }
}
