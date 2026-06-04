from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard.api.routes import pipeline, youtube

app = FastAPI(title="프로슈테크 빌더 대시보드 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(youtube.router, prefix="/api/youtube", tags=["youtube"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "프로슈테크 빌더 대시보드"}
