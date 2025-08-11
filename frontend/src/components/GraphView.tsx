import React, { useMemo } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import type { GraphEdge, GraphNode } from '../types'

type Props = {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export default function GraphView({ nodes, edges }: Props) {
  const elements = useMemo(() => {
    return [
      ...nodes.map((n) => ({ data: { id: n.id, label: n.label, type: n.type, score: n.score ?? 0 } })),
      ...edges.map((e, i) => ({ data: { id: `e${i}`, source: e.source, target: e.target, relation: e.relation, weight: e.weight } })),
    ]
  }, [nodes, edges])

  const stylesheet = [
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        'font-size': 10,
        color: '#111827',
        'background-color': (ele: any) => (ele.data('type') === 'input' ? '#3b82f6' : '#10b981'),
        width: (ele: any) => 16 + 10 * (ele.data('score') || 0),
        height: (ele: any) => 16 + 10 * (ele.data('score') || 0),
      },
    },
    {
      selector: 'edge',
      style: {
        width: (ele: any) => Math.max(1, Math.min(6, ele.data('weight') * 4)),
        'line-color': (ele: any) => {
          const rel = ele.data('relation')
          if (rel === 'cites') return '#f59e0b'
          if (rel === 'author') return '#8b5cf6'
          if (rel === 'venue') return '#ef4444'
          return '#6b7280'
        },
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': '#6b7280',
      },
    },
  ]

  return (
    <div className="w-full h-full">
      <CytoscapeComponent
        elements={elements as any}
        style={{ width: '100%', height: '100%' }}
        stylesheet={stylesheet as any}
        layout={{ name: 'cose', animate: false }}
      />
    </div>
  )
}