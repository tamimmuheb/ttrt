export type GraphNode = {
  id: string
  type: 'input' | 'paper'
  label: string
  score?: number
}

export type GraphEdge = {
  source: string
  target: string
  relation: 'similarity' | 'cites' | 'author' | 'venue'
  weight: number
}

export type GraphResult = {
  nodes: GraphNode[]
  edges: GraphEdge[]
  communities: { id: number; members: string[] }[]
}

export type Paper = {
  paperId: string
  title: string
  abstract?: string
  authors: string[]
  year?: number
  venue?: string
  url?: string
  externalIds?: Record<string, any>
  citationCount?: number
  referenceCount?: number
  embedding?: number[] | null
  rank?: number
  community?: number
  summary?: string
  bibtex_key?: string
}

export type PipelineResponse = {
  query: string
  paper_count: number
  graph: GraphResult
  papers: Paper[]
  hypothesis: string
  latex: string
  bibtex: string
  artifacts: { latex_filename: string; bib_filename: string }
}