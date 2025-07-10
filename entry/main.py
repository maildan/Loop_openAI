#!/usr/bin/env python3
"""
Loop AI Entry Point
Node.js 의 `index.ts`/`main.ts` 와 동일한 책임을 수행합니다.
`python -m loop_ai` 또는 `loop-ai` CLI 로 실행할 수 있도록 설계되었습니다.
"""
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import os
import uvicorn


def main() -> None:  # pragma: no cover
    """FastAPI 앱을 실행하는 메인 함수."""
    env = os.getenv("NODE_ENV", "production")
    is_dev = env == "development"

    # 모든 환경에서 Render 할당 포트를 사용
    port = int(os.getenv("PORT", "8080"))
    # 개발 모드에서는 워커를 1로 고정하여 리로드가 즉시 작동하게 함
    worker_count = 1 if is_dev else (os.cpu_count() or 1)
    uvicorn.run(
        "src.inference.api.server:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,
        log_level="debug" if is_dev else "warning",
        workers=worker_count,
    )


if __name__ == "__main__":  # pragma: no cover
    main() 