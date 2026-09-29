export type RelationType = 'supplier' | 'customer' | 'partner' | 'investor_or_investee' | 'peer'
export type RelationStatus = 'confirmed' | 'inferred' | 'unknown'

export interface Entity {
  id: number
  name: string
  aliases: string[]
  ticker: string | null
  is_listed: boolean
}

export interface Relationship {
  id: number
  from_entity: Entity
  to_entity: Entity
  type: RelationType
  status: RelationStatus
  relevance_score: number | null
  valid_from: string | null
  valid_to: string | null
  notes: string | null
}

export interface Evidence {
  id: number
  source_url: string
  publisher: string
  published_at: string | null
  retrieved_at: string
  locator: string | null
  excerpt: string | null
  access_note: string | null
}

export interface RelationshipDetail extends Relationship {
  score_breakdown: Record<string, number | string | null> | null
  evidences: Evidence[]
}

export interface RelationshipPage {
  total: number
  page: number
  page_size: number
  items: Relationship[]
}

export interface Graph {
  nodes: { id: string; label: string; ticker: string | null; is_listed: boolean }[]
  edges: {
    id: string
    source: string
    target: string
    type: RelationType
    status: RelationStatus
    relevance_score: number | null
  }[]
}
