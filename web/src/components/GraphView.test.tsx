import { describe, expect, it } from 'vitest'
import { buildElements } from './GraphView'
import type { Graph } from '@/types'

// 回归测试：API 的节点 id 与边 id 都是 "1".."N"，直接喂给 cytoscape 会因 id 碰撞静默丢边
const graphWithCollidingIds: Graph = {
  nodes: [
    { id: '1', label: 'TSMC', ticker: 'NYSE:TSM', is_listed: true },
    { id: '2', label: 'NVIDIA', ticker: 'NASDAQ:NVDA', is_listed: true },
  ],
  edges: [
    { id: '1', source: '1', target: '2', type: 'supplier', status: 'confirmed', relevance_score: 70 },
  ],
}

describe('buildElements（id 碰撞回归）', () => {
  it('节点与边的 id 全局唯一', () => {
    const els = buildElements(graphWithCollidingIds)
    const ids = els.map((e) => e.data.id)
    expect(new Set(ids).size).toBe(ids.length)
    expect(ids).toContain('n1')
    expect(ids).toContain('e1')
  })

  it('边的 source/target 指向带前缀的节点 id', () => {
    const els = buildElements(graphWithCollidingIds)
    const edge = els[2].data as Record<string, unknown>  // 前两个是节点
    expect(edge.source).toBe('n1')
    expect(edge.target).toBe('n2')
  })

  it('业务关系 id 保留在 relId 字段，供点击回调使用', () => {
    const els = buildElements(graphWithCollidingIds)
    expect((els[2].data as Record<string, unknown>).relId).toBe('1')
  })

  it('边宽度随相关度缩放，无评分为默认宽度', () => {
    const g: Graph = {
      nodes: graphWithCollidingIds.nodes,
      edges: [
        { ...graphWithCollidingIds.edges[0], relevance_score: 100 },
        { ...graphWithCollidingIds.edges[0], id: '2', relevance_score: null },
      ],
    }
    const els = buildElements(g)
    expect((els[2].data as Record<string, unknown>).width).toBe(6)
    expect((els[3].data as Record<string, unknown>).width).toBe(1)
  })
})
