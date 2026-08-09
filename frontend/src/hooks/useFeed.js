import { useState, useEffect } from 'react'
import axios from 'axios'

const BASE = 'http://localhost:8000'

export function useFeed(filters = {}) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchFeed = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.get(`${BASE}/feed`, { params: filters })
      setItems(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchFeed() }, [JSON.stringify(filters)])

  return { items, loading, error, refetch: fetchFeed }
}
