"""
원소/속성별 이름 생성 모듈
불, 물, 바람 등 원소/속성에 특화된 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload
import random

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]
ElementType: TypeAlias = Literal[
    "fire", "water", "earth", "air", "light", "dark", 
    "lightning", "ice", "steel", "nature",
    "불", "물", "대지", "바람", "빛", "어둠", "번개", "얼음", "강철", "자연"
]

# 🌈 원소/속성별 이름
elemental_names: Final[dict[str, tuple[str, ...]]] = {
    "fire": ("이그니스", "플람마", "블레이즈", "인페르노", "파이로", "볼케이노"),
    "water": ("아쿠아", "마리나", "오케아노스", "히드로", "글라시에스", "나이아드"),
    "earth": ("테라", "가이아", "크리스탈", "석영", "다이아몬드", "에메랄드"),
    "air": ("벤투스", "시엘", "스카이", "에어리얼", "실프", "스톰"),
    "light": ("룩스", "루미나", "솔라", "레디안트", "오로라", "셀레스"),
    "dark": ("테네브라", "셰이드", "노크턴", "이클립스", "님버스", "오브시디안"),
    "lightning": ("볼트", "썬더", "라이트닝", "일렉트라", "스파크", "쇼크"),
    "ice": ("프로스트", "글레이셜", "윈터", "블리자드", "아이스", "스노우"),
    "steel": ("페룸", "메탈릭", "아이언", "스틸", "포지", "메탈"),
    "nature": ("플로라", "실바", "네이처", "블룸", "그로우", "리프"),
}

# 한글 속성명을 영어로 변환하는 매핑
element_map: Final[dict[str, str]] = {
    "불": "fire", "물": "water", "바람": "air", "대지": "earth",
    "빛": "light", "어둠": "dark", "번개": "lightning", "얼음": "ice",
    "강철": "steel", "자연": "nature"
}

@overload
def generate_elemental_name(element: Literal["fire", "water", "earth", "air", "light", "dark", "lightning", "ice", "steel", "nature"], gender: Literal["male"]) -> str: ...

@overload
def generate_elemental_name(element: Literal["fire", "water", "earth", "air", "light", "dark", "lightning", "ice", "steel", "nature"], gender: Literal["female"]) -> str: ...

@overload
def generate_elemental_name(element: Literal["불", "물", "대지", "바람", "빛", "어둠", "번개", "얼음", "강철", "자연"], gender: GenderType = "female") -> str: ...

@overload
def generate_elemental_name(element: ElementType, gender: GenderType = "female") -> str: ...

def generate_elemental_name(element: ElementType, gender: GenderType = "female") -> str:
    """원소/속성 기반 이름 생성
    
    Args:
        element: 원소/속성 이름 (영문 또는 한글)
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 원소/속성 기반 이름
    """
    # 한글 속성명을 영어로 변환
    element_key = element_map.get(element, element)
    
    if element_key in elemental_names:
        base_name = random.choice(elemental_names[element_key])

        # 성별에 따른 어미 추가
        if gender == "female":
            if random.random() < 0.5:
                base_name += random.choice(["리아", "나", "네", "아", "에"])
        else:
            if random.random() < 0.5:
                base_name += random.choice(["스", "드", "로", "토", "무스"])

        return base_name
    else:
        # 속성이 없으면 기본 이름 생성
        from .isekai_anime import generate_isekai_anime_name
        # 타입 안전성을 위해 리터럴 문자열 사용
        if gender == "male":
            return generate_isekai_anime_name("male")
        else:
            return generate_isekai_anime_name("female") 