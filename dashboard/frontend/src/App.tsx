import { useState } from 'react'
import EpisodeManager from './components/EpisodeManager'
import PipelineView from './components/PipelineView'
import YouTubeStats from './components/YouTubeStats'

type Tab = 'overview' | 'episodes' | 'pipeline'

const TAB_LABELS: Record<Tab, string> = {
  overview: '개요',
  episodes: '에피소드',
  pipeline: '파이프라인',
}

export default function App() {
  const [tab, setTab] = useState<Tab>('overview')

  return (
    <div>
      <header className="app-header">
        <h1>📺 프로슈테크 빌더 대시보드</h1>
        <nav className="nav-tabs">
          {(Object.keys(TAB_LABELS) as Tab[]).map(t => (
            <button
              key={t}
              className={`nav-tab${tab === t ? ' active' : ''}`}
              onClick={() => setTab(t)}
            >
              {TAB_LABELS[t]}
            </button>
          ))}
        </nav>
      </header>

      <main className="main-content">
        {tab === 'overview' && (
          <>
            <YouTubeStats />
            <PipelineView />
          </>
        )}
        {tab === 'episodes' && <EpisodeManager />}
        {tab === 'pipeline' && <PipelineView detailed />}
      </main>
    </div>
  )
}
