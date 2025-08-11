import React, { useEffect, useState } from 'react'
import { getApiBase, setApiBase } from '../api'

export default function SettingsDrawer() {
  const [open, setOpen] = useState(false)
  const [apiBase, setBase] = useState('')

  useEffect(() => {
    setBase(getApiBase())
  }, [])

  return (
    <div className="fixed bottom-4 right-4">
      <button
        className="px-3 py-2 bg-gray-800 text-white rounded shadow hover:bg-gray-700"
        onClick={() => setOpen((v) => !v)}
      >
        Settings
      </button>
      {open && (
        <div className="mt-2 w-80 bg-white border border-gray-200 rounded shadow p-3">
          <div className="font-medium mb-2">API Settings</div>
          <label className="block text-sm text-gray-700 mb-1">API Base URL</label>
          <input
            value={apiBase}
            onChange={(e) => setBase(e.target.value)}
            className="w-full border rounded px-2 py-1 text-sm"
            placeholder="https://your-api-id.execute-api.us-east-1.amazonaws.com"
          />
          <div className="flex justify-end mt-3 gap-2">
            <button className="px-2 py-1 text-sm" onClick={() => setOpen(false)}>Close</button>
            <button
              className="px-2 py-1 text-sm bg-blue-600 text-white rounded"
              onClick={() => { setApiBase(apiBase); setOpen(false) }}
            >Save</button>
          </div>
        </div>
      )}
    </div>
  )
}