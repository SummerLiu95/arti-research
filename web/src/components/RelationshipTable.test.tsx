import { render, screen, fireEvent } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import RelationshipTable from './RelationshipTable'
import type { RelationshipPage } from '@/types'

const mockPage: RelationshipPage = {
  total: 2,
  page: 1,
  page_size: 20,
  items: [
    {
      id: 1,
      from_entity: { id: 2, name: 'TSMC', aliases: [], ticker: 'NYSE:TSM', is_listed: true },
      to_entity: { id: 1, name: 'NVIDIA', aliases: [], ticker: 'NASDAQ:NVDA', is_listed: true },
      type: 'supplier',
      status: 'confirmed',
      relevance_score: 80,
      valid_from: null,
      valid_to: null,
      notes: null,
    },
    {
      id: 2,
      from_entity: { id: 3, name: 'AMD', aliases: [], ticker: 'NASDAQ:AMD', is_listed: true },
      to_entity: { id: 1, name: 'NVIDIA', aliases: [], ticker: 'NASDAQ:NVDA', is_listed: true },
      type: 'peer',
      status: 'inferred',
      relevance_score: null,
      valid_from: null,
      valid_to: null,
      notes: null,
    },
  ],
}

describe('RelationshipTable', () => {
  it('渲染关系行与评分', () => {
    render(<RelationshipTable page={mockPage} loading={false} onSelect={() => {}} onPageChange={() => {}} />)
    expect(screen.getByText('TSMC → NVIDIA')).toBeTruthy()
    expect(screen.getByText('80')).toBeTruthy()
    expect(screen.getByText('供应商')).toBeTruthy()
    expect(screen.getByText('推断')).toBeTruthy()
  })

  it('无评分显示占位符', () => {
    render(<RelationshipTable page={mockPage} loading={false} onSelect={() => {}} onPageChange={() => {}} />)
    expect(screen.getByText('—')).toBeTruthy()
  })

  it('点击行触发 onSelect', () => {
    const onSelect = vi.fn()
    render(<RelationshipTable page={mockPage} loading={false} onSelect={onSelect} onPageChange={() => {}} />)
    fireEvent.click(screen.getByTestId('rel-row-1'))
    expect(onSelect).toHaveBeenCalledWith(1)
  })

  it('加载中显示提示', () => {
    render(<RelationshipTable page={null} loading={true} onSelect={() => {}} onPageChange={() => {}} />)
    expect(screen.getByText('加载中…')).toBeTruthy()
  })
})
