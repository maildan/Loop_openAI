# MCP 통합 아키텍처

## 개요

이 문서는 Loop AI 프로젝트에서 Model Context Protocol(MCP) 서버를 통합하는 아키텍처에 대해 설명합니다. MCP는 AI 모델에게 외부 도구와 데이터에 접근할 수 있는 표준화된 방법을 제공하는 프로토콜입니다.

## 아키텍처 다이어그램

```
+------------------+        +------------------+
|                  |        |                  |
|  Frontend        |        |  AI Model        |
|  (Next.js)       |        |  (Claude/GPT)    |
|                  |        |                  |
+--------+---------+        +--------+---------+
         |                           |
         | HTTP                      | MCP Protocol
         |                           |
+--------v---------+        +--------v---------+
|                  |        |                  |
|  Loop AI API     |<------>|  MCP Server      |
|  (FastAPI)       |  HTTP  |  (FastMCP)       |
|                  |        |                  |
+--------+---------+        +--------+---------+
         |                           |
         |                           |
+--------v---------+        +--------v---------+
|                  |        |                  |
|  Handlers        |        |  MCP Tools       |
|                  |        |                  |
+------------------+        +------------------+
         |                           |
         |                           |
+--------v---------+        +--------v---------+
|                  |        |                  |
|  External APIs   |        |  Data Sources    |
|  & Services      |        |                  |
|                  |        |                  |
+------------------+        +------------------+
```

## MCP 서버 구성

Loop AI의 MCP 서버는 FastMCP 라이브러리를 사용하여 구현되었습니다. 이 서버는 AI 모델이 웹 검색, 위치 정보 검색 등 다양한 외부 도구에 접근할 수 있도록 합니다.

### 서버 초기화

```python
# MCP 서버 설정
if MCP_AVAILABLE:
    try:
        # MCP 서버 초기화
        mcp_server = FastMCP("loop_ai", stateless_http=True)
        logger.info("✅ MCP 서버 초기화 완료")
        
        # FastAPI 앱에 MCP 서버 마운트
        app.mount("/mcp", mcp_server.streamable_http_app())
        logger.info("✅ MCP 서버 마운트 완료 (/mcp)")
    except Exception as e:
        logger.error(f"❌ MCP 서버 초기화 실패: {e}")
        mcp_server = None
```

## MCP 도구 구현

Loop AI는 다음과 같은 MCP 도구를 구현하고 있습니다:

### 1. 웹 검색 도구

웹 검색 도구는 사용자 쿼리에 대한 웹 검색 결과를 제공합니다.

```python
@mcp_server.tool()
def web_search(query: str, num_results: int = 5):
    """웹에서 정보를 검색합니다."""
    try:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            web_search_handler.search(query=query, num_results=min(num_results, 10))
        )
        return results.get("results", [])
    except Exception as e:
        logger.error(f"MCP 웹 검색 도구 오류: {e}")
        return {"error": str(e)}
```

### 2. 위치 정보 도구 (계획됨)

```python
@mcp_server.tool()
def location_info(query: str):
    """위치 정보를 검색합니다."""
    try:
        suggestions = location_handler.suggest_locations(query)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"MCP 위치 정보 도구 오류: {e}")
        return {"error": str(e)}
```

## MCP 도구 매핑

웹 검색 핸들러는 다양한 검색 소스에 대한 MCP 도구 매핑을 제공합니다:

```python
# MCP tools 매핑
self.search_tools = {
    "web": "mcp_Exa_Search_web_search_exa",
    "research": "mcp_Exa_Search_research_paper_search_exa", 
    "wiki": "mcp_Exa_Search_wikipedia_search_exa",
    "github": "mcp_Exa_Search_github_search_exa",
    "company": "mcp_Exa_Search_company_research_exa"
}
```

## 클라이언트 연결

AI 모델 클라이언트(Claude Desktop, Q CLI 등)에서 Loop AI의 MCP 서버에 연결하려면 다음과 같은 설정을 사용합니다:

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

## 개발 모드

개발 단계에서는 MCP 서버를 비활성화하고 시뮬레이션 결과를 사용할 수 있습니다:

```python
# 개발 중에는 MCP 서버 비활성화
logger.info("ℹ️ MCP 서버는 개발 단계에서 비활성화되어 있습니다")
```

시뮬레이션 결과는 `_generate_simulation_results` 메서드를 통해 생성됩니다:

```python
def _generate_simulation_results(self, query: str, num_results: int = 5) -> List[Dict]:
    """시뮬레이션 검색 결과 생성"""
    # 검색어에 따라 다양한 결과 생성
    # ...
```

## 배포 고려사항

MCP 서버를 프로덕션 환경에 배포할 때는 다음 사항을 고려해야 합니다:

1. **인증 및 보안**: MCP 엔드포인트에 적절한 인증 메커니즘 구현
2. **HTTPS**: 모든 통신에 HTTPS 사용
3. **로깅 및 모니터링**: MCP 도구 호출에 대한 로깅 및 모니터링 설정
4. **스케일링**: 높은 요청 볼륨을 처리하기 위한 스케일링 전략 수립
5. **에러 처리**: MCP 도구 호출 실패 시 적절한 폴백 메커니즘 구현

## 향후 계획

1. **추가 MCP 도구**: 맞춤법 검사, 스토리 생성 등 추가 도구 구현
2. **도구 권한 관리**: 도구별 액세스 제어 구현
3. **도구 사용량 모니터링**: 도구 사용량 및 성능 모니터링 구현
4. **실시간 웹 검색 통합**: 시뮬레이션에서 실제 웹 검색 API로 전환

## 참고 자료

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [FastMCP 문서](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 