import axios from 'axios'
import type { PipelineResponse } from './types'

export type PipelineRequest = {
  query: string
  text?: string
  pdf_base64?: string
  top_k?: number
  polish_latex?: boolean
}

const DEFAULT_BASE = ''

export function getApiBase(): string {
  return localStorage.getItem('apiBase') || import.meta.env.VITE_API_BASE || DEFAULT_BASE
}

export function setApiBase(url: string) {
  localStorage.setItem('apiBase', url)
}

export async function runPipeline(input: PipelineRequest): Promise<PipelineResponse> {
  const base = getApiBase()
  const url = base ? `${base.replace(/\/$/, '')}/pipeline` : '/pipeline'
  const { data } = await axios.post(url, input, {
    headers: { 'Content-Type': 'application/json' },
  })
  return data as PipelineResponse
}