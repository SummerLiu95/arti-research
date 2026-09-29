import { useCallback, useEffect, useState } from 'react'
import GraphView from '@/components/GraphView'
import RelationshipTable from '@/components/RelationshipTable'
import DetailDrawer from '@/components/DetailDrawer'
import { fetchGraph, fetchRelationships } from '@/lib/api'
import type { Graph, RelationshipPage, RelationType } from '@/types'

export default function Home() {
  const [graph, setGraph] = useState<Graph | null>(null)
  const [page, setPage] = useState<RelationshipPage | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [type, setType] = useState<RelationType | ''>('')
  const [company, setCompany] = useState('')
  const [pageNum, setPageNum] = useState(1)
  const [selectedId, setSelectedId] = useState<number | null>(null)

  useEffect(() => {
    fetchGraph('NVIDIA').then(setGraph).catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    setLoading(true)
    fetchRelationships({
      type: type || undefined,
      company: company || undefined,
      page: pageNum,
    })
      .then(setPage)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [type, company, pageNum])

  const onSelect = useCallback((id: number) => setSelectedId(id), [])

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">NVIDIA 供应链与合作关系</h1>
        <p className="mt-1 text-sm text-slate-500">
          数据来源：SEC EDGAR 等公开披露 · 不构成投资建议
        </p>
      </header>

      {error && <p className="rounded bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      {graph && <GraphView graph={graph} onSelectEdge={onSelect} />}

      <section className="flex gap-3">
        <select
          value={type}
          onChange={(e) => { setType(e.target.value as RelationType | ''); setPageNum(1) }}
          className="rounded border px-3 py-1.5 text-sm"
        >
          <option value="">全部类型</option>
          <option value="supplier">供应商</option>
          <option value="customer">客户</option>
          <option value="partner">合作伙伴</option>
          <option value="investor_or_investee">投资/被投</option>
          <option value="peer">可比公司</option>
        </select>
        <input
          value={company}
          onChange={(e) => { setCompany(e.target.value); setPageNum(1) }}
          placeholder="按公司名筛选…"
          className="rounded border px-3 py-1.5 text-sm"
        />
      </section>

      <RelationshipTable page={page} loading={loading} onSelect={onSelect} onPageChange={setPageNum} />

      <DetailDrawer relId={selectedId} onClose={() => setSelectedId(null)} />
    </main>
  )
}
