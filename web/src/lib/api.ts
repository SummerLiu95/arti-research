import type { Graph, RelationshipDetail, RelationshipPage, RelationType } from '@/types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface RelationshipQuery {
  type?: RelationType
  company?: string
  minScore?: number
  page?: number
  pageSize?: number
}

export async function fetchRelationships(q: RelationshipQuery): Promise<RelationshipPage> {
  const params = new URLSearchParams()
  if (q.type) params.set('type', q.type)
  if (q.company) params.set('company', q.company)
  if (q.minScore != null) params.set('min_score', String(q.minScore))
  params.set('page', String(q.page ?? 1))
  params.set('page_size', String(q.pageSize ?? 20))
  const resp = await fetch(`${BASE}/relationships?${params}`)
  if (!resp.ok) throw new Error(`查询失败: ${resp.status}`)
  return resp.json()
}

export async function fetchRelationshipDetail(id: number): Promise<RelationshipDetail> {
  const resp = await fetch(`${BASE}/relationships/${id}`)
  if (!resp.ok) throw new Error(`关系不存在: ${id}`)
  return resp.json()
}

export async function fetchGraph(center?: string): Promise<Graph> {
  const params = center ? `?center=${encodeURIComponent(center)}` : ''
  const resp = await fetch(`${BASE}/graph${params}`)
  if (!resp.ok) throw new Error(`关系图查询失败: ${resp.status}`)
  return resp.json()
}
