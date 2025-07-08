from __future__ import annotations
import os
import sqlite3
from fastapi import APIRouter, HTTPException
# 불필요한 Any import 제거 (미사용 경고 해결)

router = APIRouter()

# 환경변수로 지정된 DB 경로 (기본: 프로젝트 루트의 loop.db)
DB_PATH = os.getenv("PRISMA_DB_PATH", os.path.join(os.getcwd(), "loop.db"))

@router.get("/api/db/tables")
async def list_tables() -> dict[str, list[str]]:
    """DB에 존재하는 모든 테이블 목록을 반환합니다."""
    if not os.path.isfile(DB_PATH):
        raise HTTPException(status_code=500, detail=f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        _ = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # 테이블 이름 문자열 리스트로 가져오기
        name_rows: list[tuple[str]] = cursor.fetchall()
        tables = [name for (name,) in name_rows]
        conn.close()
        return {"tables": tables}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/db/table/{table_name}")
async def get_table(table_name: str, limit: int = 100) -> dict[str, object]:
    """지정된 테이블의 최대 limit개 행을 반환합니다."""
    if not os.path.isfile(DB_PATH):
        raise HTTPException(status_code=500, detail=f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        _ = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"테이블 '{table_name}' 없음")
        _ = cursor.execute(f"SELECT * FROM {table_name} LIMIT ?;", (limit,))
        # 행 데이터를 리스트로 가져오기 (칼럼 순서에 맞춰 값 리스트)
        rows: list[tuple[object, ...]] = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        conn.close()
        data = [dict(zip(cols, row)) for row in rows]
        return {"table": table_name, "rows": data}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e)) 