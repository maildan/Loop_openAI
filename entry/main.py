#!/usr/bin/env python3
"""
Loop AI Entry Point
Node.js 의 `index.ts`/`main.ts` 와 동일한 책임을 수행합니다.
`python -m loop_ai` 또는 `loop-ai` CLI 로 실행할 수 있도록 설계되었습니다.
"""
from __future__ import annotations

import uvicorn


def main() -> None:  # pragma: no cover
    """FastAPI 앱을 실행하는 메인 함수."""
    uvicorn.run(
        "src.inference.api.server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":  # pragma: no cover
    main() 