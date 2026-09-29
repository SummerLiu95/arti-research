import type { RelationshipPage, RelationType } from '@/types'
import { TYPE_COLOR } from '@/components/GraphView'

const TYPE_LABEL: Record<RelationType, string> = {
  supplier: '供应商',
  customer: '客户',
  partner: '合作伙伴',
  investor_or_investee: '投资/被投',
  peer: '可比公司',
}

const STATUS_LABEL = { confirmed: '已确认', inferred: '推断', unknown: '未知' } as const

interface Props {
  page: RelationshipPage | null
  loading: boolean
  onSelect: (id: number) => void
  onPageChange: (page: number) => void
}

export default function RelationshipTable({ page, loading, onSelect, onPageChange }: Props) {
  if (loading) return <p className="py-8 text-center text-slate-500">加载中…</p>
  if (!page) return null

  const totalPages = Math.max(1, Math.ceil(page.total / page.page_size))
  return (
    <div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-slate-500">
            <th className="py-2">关系</th>
            <th>类型</th>
            <th>状态</th>
            <th className="text-right">相关度</th>
          </tr>
        </thead>
        <tbody>
          {page.items.map((r) => (
            <tr
              key={r.id}
              className="cursor-pointer border-b hover:bg-slate-50"
              onClick={() => onSelect(r.id)}
              data-testid={`rel-row-${r.id}`}
            >
              <td className="py-2">
                {r.from_entity.name} → {r.to_entity.name}
              </td>
              <td>
                <span
                  className="rounded-full px-2 py-0.5 text-xs text-white"
                  style={{ backgroundColor: TYPE_COLOR[r.type] }}
                >
                  {TYPE_LABEL[r.type]}
                </span>
              </td>
              <td>{STATUS_LABEL[r.status]}</td>
              <td className="text-right font-mono">{r.relevance_score ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-3 flex items-center justify-between text-sm text-slate-500">
        <span>共 {page.total} 条</span>
        <div className="space-x-2">
          <button disabled={page.page <= 1} onClick={() => onPageChange(page.page - 1)} className="disabled:opacity-40">
            上一页
          </button>
          <span>{page.page} / {totalPages}</span>
          <button disabled={page.page >= totalPages} onClick={() => onPageChange(page.page + 1)} className="disabled:opacity-40">
            下一页
          </button>
        </div>
      </div>
    </div>
  )
}
