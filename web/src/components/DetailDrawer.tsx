import { useEffect, useState } from 'react'
import { fetchRelationshipDetail } from '@/lib/api'
import type { RelationshipDetail } from '@/types'

const FACTOR_LABEL: Record<string, string> = {
  type_weight: '关系类型权重',
  status_factor: '事实状态系数',
  evidence_count_factor: '证据数量系数',
  independence_factor: '证据独立性系数',
  recency_factor: '时效衰减系数',
  evidence_count: '证据条数',
  latest_evidence_at: '最新证据时间',
}

interface Props {
  relId: number | null
  onClose: () => void
}

/** 详情抽屉：证据链 + 评分构成拆解（可解释性核心）。 */
export default function DetailDrawer({ relId, onClose }: Props) {
  const [detail, setDetail] = useState<RelationshipDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (relId == null) return
    setDetail(null)
    setError(null)
    fetchRelationshipDetail(relId).then(setDetail).catch((e) => setError(String(e)))
  }, [relId])

  if (relId == null) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end" data-testid="detail-drawer">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <aside className="relative h-full w-[480px] overflow-y-auto bg-white p-6 shadow-xl">
        <button onClick={onClose} className="absolute right-4 top-4 text-slate-400 hover:text-slate-700">✕</button>
        {error && <p className="text-red-600">{error}</p>}
        {!detail && !error && <p className="text-slate-500">加载中…</p>}
        {detail && (
          <>
            <h2 className="text-lg font-semibold">
              {detail.from_entity.name} → {detail.to_entity.name}
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              {detail.type} · {detail.status} · 相关度 {detail.relevance_score ?? '—'}
            </p>
            {detail.notes && <p className="mt-3 text-sm">{detail.notes}</p>}

            {detail.score_breakdown && (
              <section className="mt-6">
                <h3 className="font-medium">评分构成</h3>
                <ul className="mt-2 space-y-1 text-sm">
                  {Object.entries(detail.score_breakdown).map(([k, v]) => (
                    <li key={k} className="flex justify-between border-b border-slate-100 py-1">
                      <span className="text-slate-600">{FACTOR_LABEL[k] ?? k}</span>
                      <span className="font-mono">{typeof v === 'number' ? v.toFixed(2) : v ?? '—'}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            <section className="mt-6">
              <h3 className="font-medium">证据链（{detail.evidences.length}）</h3>
              <ul className="mt-2 space-y-4">
                {detail.evidences.map((ev) => (
                  <li key={ev.id} className="rounded-lg border p-3 text-sm">
                    <p className="text-slate-700">{ev.excerpt}</p>
                    <p className="mt-2 text-xs text-slate-500">
                      {ev.publisher} · {ev.locator ?? '无定位'}
                    </p>
                    <a
                      href={ev.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-1 block text-xs text-blue-600 hover:underline"
                    >
                      {ev.source_url}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          </>
        )}
      </aside>
    </div>
  )
}
