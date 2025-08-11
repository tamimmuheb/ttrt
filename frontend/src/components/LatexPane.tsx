import React from 'react'

type Props = {
  latex: string
  bibtex: string
  latexFilename?: string
  bibFilename?: string
}

export default function LatexPane({ latex, bibtex, latexFilename = 'hypothesis.tex', bibFilename = 'references.bib' }: Props) {
  const download = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const copy = async (content: string) => {
    await navigator.clipboard.writeText(content)
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium">LaTeX</h3>
          <div className="flex gap-2">
            <button className="px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200" onClick={() => copy(latex)}>Copy</button>
            <button className="px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200" onClick={() => download(latex, latexFilename)}>Download</button>
          </div>
        </div>
        <pre className="bg-white p-3 rounded border border-gray-100 overflow-auto max-h-64 text-xs">{latex}</pre>
      </div>
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium">BibTeX</h3>
          <div className="flex gap-2">
            <button className="px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200" onClick={() => copy(bibtex)}>Copy</button>
            <button className="px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200" onClick={() => download(bibtex, bibFilename)}>Download</button>
          </div>
        </div>
        <pre className="bg-white p-3 rounded border border-gray-100 overflow-auto max-h-64 text-xs">{bibtex}</pre>
      </div>
    </div>
  )
}