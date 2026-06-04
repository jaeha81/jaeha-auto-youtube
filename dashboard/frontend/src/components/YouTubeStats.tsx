import { useEffect, useState } from 'react'

interface Stats {
  connected: boolean
  subscribers: number | null
  total_views: number | null
  video_count: number | null
  published_locally: number
  error?: string
}

function fmt(n: number | null | undefined): string {
  if (n == null) return '—'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

export default function YouTubeStats() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    fetch('/api/youtube/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(console.error)
  }, [])

  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div className="section-title" style={{ marginBottom: 0 }}>YouTube 채널 현황</div>
        <span style={{ fontSize: 12, fontWeight: 600, color: stats?.connected ? '#22c55e' : '#94a3b8' }}>
          {stats?.connected ? '● 연결됨' : '● 미연결'}
        </span>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{fmt(stats?.subscribers)}</div>
          <div className="stat-label">구독자</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{fmt(stats?.total_views)}</div>
          <div className="stat-label">총 조회수</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{fmt(stats?.video_count)}</div>
          <div className="stat-label">YouTube 영상 수</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#22c55e' }}>
            {stats?.published_locally ?? '—'}
          </div>
          <div className="stat-label">발행 완료</div>
        </div>
      </div>

      {stats && !stats.connected && (
        <div className="alert alert-info">
          YouTube 미연결 상태입니다. 통계를 보려면 Google Cloud Console에서
          OAuth 2.0 credentials.json을 생성하여 프로젝트 루트에 저장하세요.
        </div>
      )}
    </div>
  )
}
