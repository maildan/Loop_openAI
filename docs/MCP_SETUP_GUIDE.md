# Loop AI MCP 서버 설정 가이드

## 개요

이 문서는 Loop AI에 Model Context Protocol (MCP) 서버를 설정하는 방법을 설명합니다. MCP는 LLM 애플리케이션에 추가 컨텍스트를 통합하기 위한 표준 프로토콜입니다.

## 사전 요구사항

- Python 3.10 이상
- pip 또는 uv 패키지 관리자
- OpenAI API 키

## 설치

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:

```bash
export OPENAI_API_KEY=your_api_key_here
export REDIS_URL=redis://localhost:6379  # 선택 사항: 캐싱 활성화
```

## MCP 서버 구성

Loop AI의 MCP 서버는 다음 기능을 제공합니다:

- 웹 검색 (Exa Search 통합)
- 위치 정보 검색
- 맞춤법 검사

### 서버 구조

```
src/inference/api/
├── server.py           # FastAPI 서버 및 MCP 설정
├── handlers/
│   ├── web_search_handler.py   # 웹 검색 핸들러
│   ├── location_handler.py     # 위치 정보 핸들러
│   └── chat_handler.py         # 채팅 핸들러
```

### MCP 엔드포인트

- `/mcp` - MCP 서버 엔드포인트 (Streamable HTTP 트랜스포트)

## 로컬에서 실행하기

1. 서버 실행:

```bash
python run_server.py
```

2. MCP Inspector로 테스트:

```bash
mcp dev src/inference/api/server.py
```

브라우저에서 `http://127.0.0.1:6274`로 접속하여 MCP Inspector를 사용할 수 있습니다.

## 클라이언트 설정

Claude Desktop이나 Q CLI에서 MCP 서버를 사용하려면 다음 설정을 사용하세요:

```json
{
  "mcpServers": {
    "loop_ai": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp/"
      ]
    }
  }
}
```

## 배포

서버를 배포할 때는 다음 사항을 고려하세요:

1. 적절한 인증 메커니즘 구현
2. HTTPS 사용
3. 적절한 로깅 및 모니터링 설정
4. 스케일링 전략 수립

## 문제 해결

**Q: MCP 서버가 시작되지 않습니다.**

A: 다음을 확인하세요:
- 모든 필수 패키지가 설치되었는지
- OPENAI_API_KEY가 올바르게 설정되었는지
- 포트 8000이 사용 가능한지

**Q: MCP 도구 호출이 실패합니다.**

A: 로그를 확인하고 다음을 확인하세요:
- API 키가 유효한지
- 네트워크 연결이 안정적인지
- 요청 형식이 올바른지

## 참고 자료

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [FastMCP 문서](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 