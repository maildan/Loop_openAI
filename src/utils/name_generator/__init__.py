"""
name_generator 패키지
이세계/판타지 이름 생성을 위한 모듈 모음
"""

# 모든 함수를 직접 임포트
from .core import (
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

from .western_fantasy import generate_western_fantasy_name
from .isekai_anime import generate_isekai_anime_name
from .composed_name import generate_composed_name
from .class_name import generate_by_class
from .elemental_name import generate_elemental_name
from .noble_name import generate_noble_name, format_noble_name

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
    'format_noble_name',
] 