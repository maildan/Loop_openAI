#!/usr/bin/env python3
from __future__ import annotations
"""core.py
최신 Python 3.10+ 스타일의 이세계/판타지 이름 생성 모듈.
싱글톤 `NameGenerator` 를 통해 다양한 스타일의 이름을 생성한다.
외부 모듈에 공개되는 편의 함수는 아래와 같다.
- generate_name
- generate_multiple_names
- batch_generate_by_categories
모듈 사용 예::
    from utils.name_generator import generate_name
    print(generate_name(style="western", gender="male"))
"""

# 표준 라이브러리
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache
from typing import ClassVar, Final, Literal, TypeAlias, TypedDict, cast

# 내부 서브 모듈 (각 스타일별 구체적 생성 로직)
from .western_fantasy import generate_western_fantasy_name
from .isekai_anime import generate_isekai_anime_name
from .composed_name import generate_composed_name
from .class_name import generate_by_class
from .elemental_name import generate_elemental_name
from .noble_name import generate_noble_name, format_noble_name

# ---------------------------------------------------------------------------
# 타입 & 템플릿 정의
# ---------------------------------------------------------------------------
GenderType: TypeAlias = Literal["male", "female"]
ElementType: TypeAlias = Literal[
    "fire", "water", "earth", "air", "light", "dark",
    "lightning", "ice", "steel", "nature",
]

class CharacterDetail(TypedDict):
    """개별 캐릭터의 메타 데이터"""
    name: str
    gender: GenderType
    style: str
    character_class: str
    element: str
    personality: str

class BatchCharacterInfo(TypedDict):
    name: str
    type: str
    origin: str

class NobleFamilyInfo(TypedDict):
    family_name: str
    lord: str
    lady: str
    type: str

BatchResultItem: TypeAlias = BatchCharacterInfo | NobleFamilyInfo

# ---------------------------------------------------------------------------
# Enum 정의
# ---------------------------------------------------------------------------
class NameStyle(Enum):
    """이름 생성 스타일 열거형"""
    ISEKAI = auto()
    WESTERN = auto()
    COMPOSED = auto()
    CLASS = auto()
    ELEMENTAL = auto()
    NOBLE = auto()
    MIXED = auto()
    
    @classmethod
    def from_string(cls, value: str) -> "NameStyle":
        mapping: dict[str, NameStyle] = {
            "isekai": cls.ISEKAI,
            "western": cls.WESTERN,
            "composed": cls.COMPOSED,
            "class": cls.CLASS,
            "elemental": cls.ELEMENTAL,
            "noble": cls.NOBLE,
            "mixed": cls.MIXED,
        }
        return mapping.get(value.lower(), cls.MIXED)

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    
    @classmethod
    def from_string(cls, value: str) -> "Gender":
        return cls.MALE if value.lower() == "male" else cls.FEMALE

# ---------------------------------------------------------------------------
# 설정 데이터 클래스
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class NameGeneratorConfig:
    """`NameGenerator` 의 동작을 제어하는 설정"""
    default_style: NameStyle = NameStyle.ISEKAI
    default_gender: Gender = Gender.FEMALE
    default_count: int = 10
    max_batch_size: int = 50
    enable_caching: bool = True
    
    personalities: list[str] = field(default_factory=lambda: [
        "용감한", "지혜로운", "신비로운", "우아한", "강인한", "온화한",
        "냉정한", "열정적인", "순수한", "교활한", "매력적인", "카리스마 있는",
        "고독한", "자유로운", "창의적인", "충성스러운", "호기심 많은", "결단력 있는",
    ])

# ---------------------------------------------------------------------------
# 이름 생성기 (싱글톤)
# ---------------------------------------------------------------------------
class NameGenerator:
    """통합 이름 생성기 (Singleton)"""

    _instance: ClassVar[NameGenerator | None] = None
    
    # 상수 & 매핑
    DEFAULT_BATCH_SIZE: Final[int] = 5
    MAX_CACHE_SIZE: Final[int] = 1024

    ELEMENT_MAP: Final[dict[str, str]] = {
        # 한글 ↔ 영어 매핑 포함
        "불": "fire", "fire": "fire",
        "물": "water", "water": "water",
        "바람": "air", "air": "air",
        "대지": "earth", "earth": "earth",
        "빛": "light", "light": "light",
        "어둠": "dark", "dark": "dark",
        "번개": "lightning", "lightning": "lightning",
        "얼음": "ice", "ice": "ice",
        "강철": "steel", "steel": "steel",
        "자연": "nature", "nature": "nature",
    }
    VALID_ELEMENTS: Final[set[str]] = set(ELEMENT_MAP.values())

    # ---------------------------------------------------------------------
    # 싱글톤 구현
    # ---------------------------------------------------------------------
    def __new__(cls, config: NameGeneratorConfig | None = None):  # noqa: D401
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: NameGeneratorConfig | None = None):  # noqa: D401
        if getattr(self, "_initialized", False):
            return  # 이미 초기화 완료
            
        self.config: NameGeneratorConfig = config if config else NameGeneratorConfig()
        self._initialized: bool = True
    
    # ------------------------------------------------------------------
    # 내부 유틸리티
    # ------------------------------------------------------------------
    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def _random_personality(self) -> str:
        return random.choice(self.config.personalities)
    
    def _normalize_element(self, element: str | None) -> str | None:
        if not element:
            return None
        return self.ELEMENT_MAP.get(element.lower())
    
    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------
    def generate_name(
        self, 
        style: str | NameStyle | None = None,
        gender: str | Gender | None = None,
        character_class: str | None = None,
        element: str | None = None,
    ) -> str:
        """단일 이름 생성"""
        style_enum: NameStyle = (
            NameStyle.from_string(style) if isinstance(style, str) else style or self.config.default_style
        )
        gender_enum: Gender = (
            Gender.from_string(gender) if isinstance(gender, str) else gender or self.config.default_gender
        )
        gender_lit: GenderType = gender_enum.value

        # 클래스 기반 우선
        if character_class:
            return generate_by_class(character_class, gender_lit)
        
        # 원소 기반 우선 (검증 포함)
        if element and (normalized := self._normalize_element(element)) in self.VALID_ELEMENTS:
            return generate_elemental_name(cast(ElementType, normalized), gender_lit)
        
        # 스타일별 분기
        match style_enum:
            case NameStyle.ISEKAI:
                return generate_isekai_anime_name(gender_lit)
            case NameStyle.WESTERN:
                return generate_western_fantasy_name(gender_lit)
            case NameStyle.COMPOSED:
                return generate_composed_name(gender_lit)
            case NameStyle.NOBLE:
                first, surname = generate_noble_name(gender_lit)
                return format_noble_name(first, surname)
            case NameStyle.ELEMENTAL:
                rand_element = cast(ElementType, random.choice(tuple(self.VALID_ELEMENTS)))
                return generate_elemental_name(rand_element, gender_lit)
            case _:
                # MIXED: 랜덤 스타일 재귀 호출
                rand_style = random.choice([
                    NameStyle.ISEKAI,
                    NameStyle.WESTERN,
                    NameStyle.COMPOSED,
                ])
                return self.generate_name(rand_style, gender_enum)
    
    def generate_multiple_names(
        self, 
        count: int | None = None,
        gender: str | Gender | None = None,
        style: str | NameStyle | None = None,
    ) -> list[CharacterDetail]:
        """여러 개의 이름을 상세 정보와 함께 반환"""
        count = count or self.config.default_count
        gender_enum: Gender = (
            Gender.from_string(gender) if isinstance(gender, str) else gender or self.config.default_gender
        )
        style_enum: NameStyle = (
            NameStyle.from_string(style) if isinstance(style, str) else style or self.config.default_style
        )
        gender_lit: GenderType = gender_enum.value
        
        results: list[CharacterDetail] = []
        for _ in range(min(count, self.config.max_batch_size)):
            # mixed 스타일이면 라운드마다 랜덤 지정
            current_style = (
                random.choice([
                    NameStyle.ISEKAI,
                    NameStyle.WESTERN,
                    NameStyle.COMPOSED,
                    NameStyle.ELEMENTAL,
                    NameStyle.NOBLE,
                ])
                if style_enum == NameStyle.MIXED
                else style_enum
            )

            element_opt: str | None = None
            if random.random() < 0.3:  # 30% 확률로 원소 부여
                element_opt = random.choice(list(self.VALID_ELEMENTS))

            class_opt: str | None = None
            if random.random() < 0.2:  # 20% 확률로 캐릭터 클래스 부여
                class_opt = random.choice(
                    ["전사", "마법사", "궁수", "도적", "성직자", "기사", "암살자", "드루이드"]
                )

            name = self.generate_name(current_style, gender_enum, class_opt, element_opt)
            
            results.append(
                {
                    "name": name,
                    "gender": gender_lit,
                    "style": current_style.name.lower(),
                    "character_class": class_opt or "일반",
                    "element": element_opt or "없음",
                    "personality": self._random_personality(),
                }
            )
        return results
    
    def batch_generate_by_categories(self, count_per_category: int | None = None) -> dict[str, list[BatchResultItem]]:
        """카테고리별 이름 또는 가문 정보를 모아 반환"""
        count_per_category = count_per_category or self.DEFAULT_BATCH_SIZE
        result: dict[str, list[BatchResultItem]] = {}

        # 이세계 애니메이션
        isekai: list[BatchResultItem] = []
        for _ in range(count_per_category):
            random_gender: GenderType = random.choice(["male", "female"])
            isekai.append(
                {
                    "name": generate_isekai_anime_name(random_gender),
                    "type": "isekai_anime",
                    "origin": "Re:Zero 스타일",
                }
            )
        result["isekai_anime"] = isekai

        # 서양 판타지
        western: list[BatchResultItem] = []
        for _ in range(count_per_category):
            random_gender = random.choice(["male", "female"])
            western.append(
                {
                    "name": generate_western_fantasy_name(random_gender),
                    "type": "western_fantasy",
                    "origin": "반지의 제왕 스타일",
                }
            )
        result["western_fantasy"] = western

        # 조합형
        composed: list[BatchResultItem] = []
        for _ in range(count_per_category):
            random_gender = random.choice(["male", "female"])
            composed.append(
                {
                    "name": generate_composed_name(random_gender),
                    "type": "composed",
                    "origin": "음절 조합",
                }
            )
        result["composed"] = composed

        # 귀족 가문
        noble: list[BatchResultItem] = []
        for _ in range(count_per_category):
            lord_first, surname = generate_noble_name("male")
            lady_first, _ = generate_noble_name("female")
            noble.append(
                {
                    "family_name": surname,
                    "lord": format_noble_name(lord_first, surname),
                    "lady": format_noble_name(lady_first, surname),
                    "type": "noble_family",
                }
            )
        result["noble_family"] = noble

        return result

# ---------------------------------------------------------------------------
# 전역 싱글톤 및 편의 함수
# ---------------------------------------------------------------------------
name_generator: Final[NameGenerator] = NameGenerator()

generate_name = name_generator.generate_name  # type: ignore[assignment]
generate_multiple_names = name_generator.generate_multiple_names  # type: ignore[assignment]
batch_generate_by_categories = name_generator.batch_generate_by_categories  # type: ignore[assignment]
