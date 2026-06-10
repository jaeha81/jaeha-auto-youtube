import { useCallback, useEffect, useState } from 'react'

interface Topic {
  priority: number
  title: string
  content_axis: string
  angle: string
  target_keywords: string[]
  reason: string
}

interface Strategy {
  generated_date: string
  mock: boolean
  insights: string[]
  next_topics: Topic[]
}

export default function StrategyPanel() {
  const [strategy, setStrategy] = useState<Strategy | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState<'strategy' | 'autopilot' | null>(null)
  const [msg, setMsg] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)

  const loadStrategy = useCallback(async () => {
    try {
      const data = await fetch('/api/strategy/latest').then(r => r.json())
      setStrategy(data.available ? data.strategy : null)
    } catch (e) {
      setMsg({ type: 'error', text: `전략 로드 실패: ${e}` })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadStrategy() }, [loadStrategy])

  const pollJob = async (jobId: string, label: string) => {
    for (let i = 0; i < 90; i++) {
      await new Promise(r => setTimeout(r, 2000))
      const status = await fetch(`/api/strategy/job/${jobId}`).then(r => r.json())
      if (status.status === 'done') {
        setMsg({ type: 'success', text: `${label} 완료!` })
        return
      }
      if (status.status === 'error') {
        throw new Error(status.error || `${label} 중 오류 발생`)
      }
    }
    throw new Error(`타임아웃: ${label}이(가) 너무 오래 걸립니다`)
  }

  const handleRunStrategy = async (mock: boolean) => {
    setRunning('strategy')
    setMsg({ type: 'info', text: '성과 데이터를 분석하고 있습니다…' })
    try {
      const { job_id } = await fetch('/api/strategy/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mock }),
      }).then(r => r.json())
      await pollJob(job_id, '전략 분석')
      await loadStrategy()
    } catch (e: unknown) {
      setMsg({ type: 'error', text: `전략 분석 실패: ${e instanceof Error ? e.message : String(e)}` })
    } finally {
      setRunning(null)
    }
  }

  const handleAutopilot = async (mock: boolean) => {
    setRunning('autopilot')
    setMsg({ type: 'info', text: '에이전트 주행 중… (동기화 → 스크립트 → SEO → 썸네일 브리프)' })
    try {
      const { job_id } = await fetch('/api/strategy/autopilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mock }),
      }).then(r => r.json())
      await pollJob(job_id, '에이전트 주행')
      setMsg({ type: 'success', text: '에이전트 주행 완료! 에피소드 탭에서 결과를 확인하세요. 업로드는 검토 후 직접 승인해야 합니다.' })
    } catch (e: unknown) {
      setMsg({ type: 'error', text: `에이전트 주행 실패: ${e instanceof Error ? e.message : String(e)}` })
    } finally {
      setRunning(null)
    }
  }

  if (loading) return <div className="loading">콘텐츠 전략 로딩 중...</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
        <div className="section-title" style={{ marginBottom: 0 }}>콘텐츠 전략 (에이전트 주행)</div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            className="btn btn-outline"
            disabled={running !== null}
            onClick={() => handleRunStrategy(true)}
            title="API 없이 구조 확인용 샘플 전략 생성"
          >
            전략 분석 (Mock)
          </button>
          <button
            className="btn btn-primary"
            disabled={running !== null}
            onClick={() => handleRunStrategy(false)}
            title="성과 데이터 기반 다음 콘텐츠 방향 제안"
          >
            {running === 'strategy' ? '분석 중…' : '전략 분석 실행'}
          </button>
          <button
            className="btn btn-success"
            disabled={running !== null}
            onClick={() => handleAutopilot(false)}
            title="미처리 노트를 찾아 스크립트→SEO→썸네일 브리프까지 자동 생성 (업로드는 별도 승인)"
          >
            {running === 'autopilot' ? '주행 중…' : '🚀 에이전트 주행'}
          </button>
        </div>
      </div>

      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, color: '#64748b', lineHeight: 1.7 }}>
          <strong>에이전트 주행</strong>은 Bucky 동기화 → 미처리 노트 선택 → 스크립트 → SEO → 썸네일 브리프까지 한 번에 실행합니다.
          업로드는 자동 실행되지 않으며, 에피소드 탭에서 검토 후 직접 승인해야 합니다.
        </div>
      </div>

      {!strategy ? (
        <div className="card" style={{ textAlign: 'center', padding: 48, color: '#94a3b8', fontSize: 14 }}>
          아직 전략 제안이 없습니다.<br />
          <span style={{ fontSize: 13 }}>'전략 분석 실행'을 눌러 성과 기반 다음 콘텐츠 방향을 받아보세요.</span>
        </div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ fontWeight: 600, fontSize: 13, color: '#64748b' }}>성과 인사이트</div>
              <div style={{ fontSize: 12, color: '#94a3b8' }}>
                {strategy.generated_date}{strategy.mock ? ' · MOCK' : ''}
              </div>
            </div>
            {strategy.insights.map((insight, i) => (
              <div key={i} style={{ fontSize: 14, lineHeight: 1.7, color: '#374151' }}>• {insight}</div>
            ))}
          </div>

          <div className="section-title">다음 에피소드 제안</div>
          {strategy.next_topics.map(topic => (
            <div key={topic.priority} className="card" style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <span className="ep-num">#{topic.priority}</span>
                <span style={{ fontWeight: 700, fontSize: 15 }}>{topic.title}</span>
                <span className="badge badge-scripted">{topic.content_axis}</span>
              </div>
              <div style={{ fontSize: 14, color: '#374151', lineHeight: 1.6, marginBottom: 8 }}>{topic.angle}</div>
              <div style={{ fontSize: 13, color: '#64748b', marginBottom: 6 }}>
                <strong>근거:</strong> {topic.reason}
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {topic.target_keywords.map(kw => (
                  <span key={kw} className="badge badge-draft">{kw}</span>
                ))}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
