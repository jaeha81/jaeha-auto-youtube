import { useEffect, useState } from 'react'

interface PipelineSummary {
  total: number
  draft: number
  scripted: number
  seo_ready: number
  queued: number
  published: number
}

interface Episode {
  episode: string
  status: string
  title: string
}

interface Props {
  detailed?: boolean
}

const STAGES: { key: keyof Omit<PipelineSummary, 'total'>; label: string; desc: string }[] = [
  { key: 'draft',     label: '초안',     desc: '노트 작성됨' },
  { key: 'scripted',  label: '스크립트', desc: '스크립트 생성됨' },
  { key: 'seo_ready', label: 'SEO 완료', desc: 'SEO 메타데이터 완료' },
  { key: 'queued',    label: '촬영 완료', desc: '영상 파일 대기 중' },
  { key: 'published', label: '발행됨',   desc: 'YouTube 업로드 완료' },
]

export default function PipelineView({ detailed = false }: Props) {
  const [summary, setSummary] = useState<PipelineSummary | null>(null)
  const [episodes, setEpisodes] = useState<Episode[]>([])
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/pipeline/summary')
      .then(r => r.json())
      .then(setSummary)
      .catch(console.error)

    if (detailed) {
      fetch('/api/pipeline/episodes')
        .then(r => r.json())
        .then(setEpisodes)
        .catch(console.error)
    }
  }, [detailed])

  const filtered = selected ? episodes.filter(e => e.status === selected) : []

  return (
    <div>
      <div className="section-title">파이프라인 현황</div>
      <div className="pipeline-grid">
        {STAGES.map((stage, i) => (
          <div
            key={stage.key}
            className={`pipeline-stage${detailed ? ' clickable' : ''}${selected === stage.key ? ' selected' : ''}`}
            onClick={() => detailed && setSelected(selected === stage.key ? null : stage.key)}
          >
            {i < STAGES.length - 1 && <span className="stage-arrow">›</span>}
            <div className="stage-count">
              {summary ? summary[stage.key] : '—'}
            </div>
            <div className="stage-name">{stage.label}</div>
            <div className="stage-desc">{stage.desc}</div>
          </div>
        ))}
      </div>

      {detailed && selected && (
        <div className="card" style={{ marginTop: 12 }}>
          <div style={{ fontWeight: 600, fontSize: 13, color: '#64748b', marginBottom: 12 }}>
            {STAGES.find(s => s.key === selected)?.label} 단계 에피소드
          </div>
          {filtered.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: 14 }}>해당 단계의 에피소드가 없습니다.</p>
          ) : (
            filtered.map(ep => (
              <div key={ep.episode} className="ep-pill">
                <span>
                  <span className="ep-num">EP{ep.episode}</span>
                  <span style={{ color: '#374151' }}>{ep.title || '(제목 없음)'}</span>
                </span>
                <span className={`badge badge-${ep.status}`}>
                  {STAGES.find(s => s.key === ep.status)?.label ?? ep.status}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
