import { useCallback, useEffect, useState } from 'react'

interface Episode {
  episode: string
  status: 'draft' | 'scripted' | 'seo_ready' | 'queued' | 'published'
  title: string
  has_script: boolean
  has_seo: boolean
  has_video: boolean
  published: boolean
}

interface UploadPreview {
  episode: string
  title: string
  description: string
  tags: string[]
  visibility: string
  category: string
}

const STATUS_LABELS: Record<string, string> = {
  draft:     '초안',
  scripted:  '스크립트',
  seo_ready: 'SEO 완료',
  queued:    '대기 중',
  published: '발행됨',
}

export default function EpisodeManager() {
  const [episodes, setEpisodes] = useState<Episode[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<Record<string, boolean>>({})
  const [uploadPreview, setUploadPreview] = useState<UploadPreview | null>(null)
  const [uploading, setUploading] = useState(false)
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const loadEpisodes = useCallback(async () => {
    try {
      const data: Episode[] = await fetch('/api/pipeline/episodes').then(r => r.json())
      setEpisodes(data)
    } catch (e) {
      setMsg({ type: 'error', text: `에피소드 목록 로드 실패: ${e}` })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadEpisodes() }, [loadEpisodes])

  const handleGenerate = async (episode: string, mock = true) => {
    setGenerating(g => ({ ...g, [episode]: true }))
    setMsg(null)
    try {
      const res = await fetch('/api/pipeline/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ episode, mock }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail ?? '생성 실패')
      }
      const { job_id } = await res.json()

      for (let i = 0; i < 60; i++) {
        await new Promise(r => setTimeout(r, 2000))
        const status = await fetch(`/api/pipeline/job/${job_id}`).then(r => r.json())
        if (status.status === 'done') {
          setMsg({ type: 'success', text: `EP${episode} 생성 완료!` })
          await loadEpisodes()
          return
        }
        if (status.status === 'error') {
          throw new Error(status.error || '생성 중 오류 발생')
        }
      }
      throw new Error('타임아웃: 생성이 너무 오래 걸립니다')
    } catch (e: unknown) {
      setMsg({ type: 'error', text: `생성 실패: ${e instanceof Error ? e.message : String(e)}` })
    } finally {
      setGenerating(g => ({ ...g, [episode]: false }))
    }
  }

  const handleUploadPreview = async (episode: string) => {
    setMsg(null)
    try {
      const data = await fetch(`/api/youtube/upload-preview/${episode}`).then(r => r.json())
      if (data.detail) throw new Error(data.detail)
      setUploadPreview(data)
    } catch (e: unknown) {
      setMsg({ type: 'error', text: `미리보기 로드 실패: ${e instanceof Error ? e.message : String(e)}` })
    }
  }

  const handleUploadConfirm = async () => {
    if (!uploadPreview) return
    setUploading(true)
    try {
      const res = await fetch(`/api/youtube/upload/${uploadPreview.episode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmed: true }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail ?? '업로드 실패')
      }
      const result = await res.json()
      setUploadPreview(null)
      setMsg({ type: 'success', text: `업로드 완료! ${result.url ?? ''}` })
      await loadEpisodes()
    } catch (e: unknown) {
      setMsg({ type: 'error', text: `업로드 실패: ${e instanceof Error ? e.message : String(e)}` })
    } finally {
      setUploading(false)
    }
  }

  if (loading) return <div className="loading">에피소드 목록 로딩 중...</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div className="section-title" style={{ marginBottom: 0 }}>에피소드 관리</div>
        <button className="btn btn-outline" onClick={loadEpisodes}>↻ 새로고침</button>
      </div>

      {msg && (
        <div className={`alert alert-${msg.type}`}>{msg.text}</div>
      )}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {episodes.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#94a3b8', fontSize: 14 }}>
            에피소드가 없습니다.<br />
            <span style={{ fontSize: 13 }}>content/source-notes/ 폴더에 ep001.md 형식으로 노트를 추가하세요.</span>
          </div>
        ) : (
          <table className="episode-table">
            <thead>
              <tr>
                <th>번호</th>
                <th>제목</th>
                <th>상태</th>
                <th style={{ textAlign: 'center' }}>스크립트</th>
                <th style={{ textAlign: 'center' }}>SEO</th>
                <th style={{ textAlign: 'center' }}>영상</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {episodes.map(ep => (
                <tr key={ep.episode}>
                  <td>
                    <span className="ep-num">EP{ep.episode}</span>
                  </td>
                  <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {ep.title || <span style={{ color: '#94a3b8' }}>(제목 없음)</span>}
                  </td>
                  <td>
                    <span className={`badge badge-${ep.status}`}>
                      {STATUS_LABELS[ep.status] ?? ep.status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={ep.has_script ? 'check' : 'cross'}>
                      {ep.has_script ? '✓' : '✗'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={ep.has_seo ? 'check' : 'cross'}>
                      {ep.has_seo ? '✓' : '✗'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={ep.has_video ? 'check' : 'cross'}>
                      {ep.has_video ? '✓' : '✗'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {ep.status === 'draft' && (
                        <button
                          className="btn btn-primary"
                          disabled={generating[ep.episode]}
                          onClick={() => handleGenerate(ep.episode, true)}
                          title="Mock 모드로 스크립트+SEO 샘플 파일 생성"
                        >
                          {generating[ep.episode] ? '생성 중…' : '생성 (Mock)'}
                        </button>
                      )}
                      {(ep.status === 'seo_ready' || ep.status === 'queued') && (
                        <button
                          className="btn btn-success"
                          onClick={() => handleUploadPreview(ep.episode)}
                        >
                          업로드
                        </button>
                      )}
                      {ep.status === 'published' && (
                        <span style={{ fontSize: 12, color: '#22c55e', fontWeight: 600 }}>✓ 발행됨</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Upload Confirmation Modal */}
      {uploadPreview && (
        <div
          className="modal-overlay"
          onClick={e => { if (e.target === e.currentTarget) setUploadPreview(null) }}
        >
          <div className="modal">
            <h2>YouTube 업로드 확인</h2>
            <div className="modal-field">
              <label>에피소드</label>
              <div className="value">EP{uploadPreview.episode}</div>
            </div>
            <div className="modal-field">
              <label>제목</label>
              <div className="value">{uploadPreview.title}</div>
            </div>
            <div className="modal-field">
              <label>설명 (앞부분)</label>
              <div className="value">{uploadPreview.description.slice(0, 300)}{uploadPreview.description.length > 300 ? '…' : ''}</div>
            </div>
            <div className="modal-field">
              <label>태그</label>
              <div className="value">{uploadPreview.tags.join(', ')}</div>
            </div>
            <div className="modal-field">
              <label>공개 설정</label>
              <div className="value">{uploadPreview.visibility}</div>
            </div>
            <p style={{ fontSize: 13, color: '#64748b', marginTop: 14, lineHeight: 1.6 }}>
              위 정보로 YouTube에 업로드합니다. 업로드 후에는 취소할 수 없습니다.
            </p>
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setUploadPreview(null)}>
                취소
              </button>
              <button
                className="btn btn-success"
                disabled={uploading}
                onClick={handleUploadConfirm}
              >
                {uploading ? '업로드 중…' : '업로드 확인'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
