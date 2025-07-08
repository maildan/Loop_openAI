#!/usr/bin/env python3
"""
🔥 Fantasy & Isekai Name Generator v3.0 🔥
에밀리아, 카구야, 림루 같은 진짜 이세계/판타지 이름 생성기

기능:
- 이세계 애니메이션 스타일 이름
- 서양 판타지 이름
- 일본 라이트노벨 이름
- 조합형 이름 생성
- 캐릭터 클래스별 이름
"""

from typing import List, Dict, Union, Optional

# 모듈화된 name_generator 패키지에서 모든 기능 가져오기
from .name_generator.core import (
    NameGenerator,
    CharacterDetail,
    BatchCharacterInfo,
    NobleFamilyInfo,
    BatchResultItem,
    generate_name,
    generate_multiple_names,
    batch_generate_by_categories,
    name_generator
)

# 개별 생성 함수들도 직접 접근 가능하도록 노출
from .name_generator import (
    generate_western_fantasy_name,
    generate_isekai_anime_name,
    generate_composed_name,
    generate_by_class,
    generate_elemental_name,
    generate_noble_name,
    format_noble_name
)

# 타입 내보내기
__all__ = [
    'NameGenerator',
    'CharacterDetail',
    'BatchCharacterInfo',
    'NobleFamilyInfo',
    'BatchResultItem',
    'generate_name',
    'generate_multiple_names',
    'batch_generate_by_categories',
    'name_generator',
    'generate_western_fantasy_name',
    'generate_isekai_anime_name',
    'generate_composed_name',
    'generate_by_class',
    'generate_elemental_name',
    'generate_noble_name',
    'format_noble_name'
] 