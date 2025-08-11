import React, { useMemo, useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { runPipeline } from './api'
import type { PipelineResponse } from './types'
import GraphView from './components/GraphView'
import PaperList from './components/PaperList'
import LatexPane from './components/LatexPane'
import SettingsDrawer from './components/SettingsDrawer'

function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve((reader.result as string).split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export default function App() {
  const [query, setQuery] = useState('graph neural networks for citation recommendation')
  const [text, setText] = useState('')
  const [topK, setTopK] = useState(15)
  const [polish, setPolish] = useState(true)
  const [pdfBase64, setPdfBase64] = useState<string | undefined>(undefined)
  const fileRef = useRef<HTMLInputElement | null>(null)

  const { mutate, data, isPending, error } = useMutation({
    mutationFn: runPipeline,
  })

  const onSubmit = () => {
    mutate({ query, text: text || undefined, pdf_base64: pdfBase64, top_k: topK, polish_latex: polish })
  }

  const onPickPdf = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      const b64 = await readFileAsBase64(f)
      setPdfBase64(b64)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <header className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="text-lg font-semibold">Research GNN Agent</div>
          <div className="text-sm text-gray-600">Serverless AI literature explorer</div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-4 grid grid-cols-12 gap-4">
        <section className="col-span-12 lg:col-span-4 space-y-3">
          <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
            <label className="block text-sm font-medium text-gray-700">Query</label>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your research question"
            />
            <label className="block text-sm font-medium text-gray-700 mt-3">Optional text</label>
            <textarea
              className="mt-1 w-full border rounded px-3 py-2 h-28"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste notes or abstract"
            />
            <div className="mt-3">
              <label className="text-sm font-medium text-gray-700">Or upload PDF</label>
              <div className="flex items-center gap-2 mt-1">
                <input ref={fileRef} type="file" accept="application/pdf" onChange={onPickPdf} />
                {pdfBase64 && <span className="text-xs text-green-600">PDF attached</span>}
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm">Top K</label>
                <input
                  type="number"
                  className="w-full border rounded px-2 py-1"
                  value={topK}
                  min={5}
                  max={50}
                  onChange={(e) => setTopK(parseInt(e.target.value || '15'))}
                />
              </div>
              <div className="flex items-end gap-2">
                <input id="polish" type="checkbox" checked={polish} onChange={(e) => setPolish(e.target.checked)} />
                <label htmlFor="polish" className="text-sm">Polish LaTeX</label>
              </div>
            </div>
            <button
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 disabled:opacity-50"
              onClick={onSubmit}
              disabled={isPending}
            >
              {isPending ? 'Running...' : 'Run Pipeline'}
            </button>
            {error && <div className="text-sm text-red-600 mt-2">{(error as any).message || 'Error'}</div>}
          </div>

          {data && (
            <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
              <div className="font-medium mb-2">Hypothesis</div>
              <div className="text-gray-800 text-sm whitespace-pre-wrap">{data.hypothesis}</div>
            </div>
          )}

          {data && (
            <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
              <div className="font-medium mb-3">Papers ({data.paper_count})</div>
              <PaperList papers={[...data.papers].sort((a,b) => (b.rank||0)-(a.rank||0))} />
            </div>
          )}
        </section>

        <section className="col-span-12 lg:col-span-8 grid grid-rows-2 gap-4">
          <div className="bg-white rounded-lg shadow p-3 border border-gray-100 min-h-[320px]">
            <div className="font-medium mb-2">Graph</div>
            <div className="h-[400px]">
              {data ? (
                <GraphView nodes={data.graph.nodes} edges={data.graph.edges} />
              ) : (
                <div className="text-sm text-gray-500 p-4">Run the pipeline to see the graph.</div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
            <div className="font-medium mb-3">LaTeX & BibTeX</div>
            <LatexPane latex={data?.latex || ''} bibtex={data?.bibtex || ''} />
          </div>
        </section>
      </main>

      <SettingsDrawer />
    </div>
  )
}