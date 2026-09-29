import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import type { Graph, RelationType } from '@/types'

export const TYPE_COLOR: Record<RelationType, string> = {
  supplier: '#2563eb',             // 蓝
  customer: '#16a34a',             // 绿
  partner: '#9333ea',              // 紫
  investor_or_investee: '#ea580c', // 橙
  peer: '#64748b',                 // 灰
}

interface Props {
  graph: Graph
  onSelectEdge: (relId: number) => void
}

/** Cytoscape 关系网络图：节点=公司，边=关系（颜色=类型，宽度=相关度）。 */
export default function GraphView({ graph, onSelectEdge }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const cy = cytoscape({
      container: ref.current,
      elements: [
        ...graph.nodes.map((n) => ({ data: { id: n.id, label: n.label } })),
        ...graph.edges.map((e) => ({
          data: {
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.type,
            color: TYPE_COLOR[e.type],
            width: 1 + ((e.relevance_score ?? 0) / 100) * 5,
          },
        })),
      ],
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#0f172a',
            color: '#0f172a',
            'font-size': 11,
            'text-valign': 'bottom',
            'text-margin-y': 6,
          },
        },
        {
          selector: 'edge',
          style: {
            label: 'data(label)',
            'line-color': 'data(color)',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': 'data(color)',
            width: 'data(width)',
            'curve-style': 'bezier',
            'font-size': 9,
            color: '#475569',
          },
        },
      ],
      layout: { name: 'cose', animate: false, nodeRepulsion: 8000 },
    })
    cy.on('tap', 'edge', (evt) => onSelectEdge(Number(evt.target.id())))
    return () => cy.destroy()
  }, [graph, onSelectEdge])

  return <div ref={ref} className="h-[420px] w-full rounded-lg border bg-white" data-testid="graph-view" />
}
