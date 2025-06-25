#!/usr/bin/env python3
"""
Loop AI 서버 런처
모듈화된 서버를 실행하는 스크립트
"""

import os
import sys
import uvicorn

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Loop AI 서버 시작 중...")
    print("📍 주소: http://localhost:8080")
    print("📖 API 문서: http://localhost:8080/docs")
    print("💾 맞춤법 검사: http://localhost:8080/api/spellcheck")
    print("💬 채팅: http://localhost:8080/api/chat")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "src.inference.api.server:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1) 