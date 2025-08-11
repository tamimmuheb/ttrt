import React from 'react'
import type { Paper } from '../types'

export default function PaperList({ papers }: { papers: Paper[] }) {
  return (
    <div className="space-y-3">
      {papers.map((p) => (
        <div key={p.paperId} className="bg-white rounded-lg shadow p-3 border border-gray-100">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="text-sm text-gray-500">Rank: {p.rank?.toFixed(4)}</div>
              <div className="font-medium text-gray-900">{p.title}</div>
              <div className="text-xs text-gray-600 mt-0.5">{p.authors.join(', ')}</div>
              <div className="text-xs text-gray-500">{p.venue} {p.year ? `(${p.year})` : ''}</div>
            </div>
            {p.url && (
              <a className="text-blue-600 text-sm hover:underline" href={p.url} target="_blank" rel="noreferrer">
                View
              </a>
            )}
          </div>
          {p.summary && <div className="text-sm text-gray-800 mt-2">{p.summary}</div>}
        </div>
      ))}
    </div>
  )
}