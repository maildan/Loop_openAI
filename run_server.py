#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
Loop AI 서버 런처
모듈화된 서버를 실행하는 스크립트
"""

"""Deprecated launcher: 유지보수 편의를 위해 `entry.main`에 위임."""

from entry.main import main  # type: ignore[import-not-found]


if __name__ == "__main__":  # pragma: no cover
    main() 