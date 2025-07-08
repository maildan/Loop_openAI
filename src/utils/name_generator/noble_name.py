"""
귀족 이름 생성 모듈
귀족/가문 이름과 개인 이름을 조합하여 귀족 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload
import random

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]

# 귀족 성씨 목록
noble_surnames: Final[list[str]] = [
    "그레이라트", "라트레이야", "보레아스", "아스라", "드라고니아", "펜드래곤",
    "플란타지넷", "하프스부르크", "로마노프", "메디치", "몬테크리스토", "다르타냥",
    "발루아", "부르봉", "합스부르크", "폰 아인즈베른", "토오사카", "엔즈워스",
    "마토", "에미야",
]

@overload
def generate_noble_name(gender: Literal["male"]) -> tuple[str, str]: ...

@overload
def generate_noble_name(gender: Literal["female"]) -> tuple[str, str]: ...

@overload
def generate_noble_name(gender: GenderType = "female") -> tuple[str, str]: ...

def generate_noble_name(gender: GenderType = "female") -> tuple[str, str]:
    """귀족 이름 생성 (이름 + 성)
    
    Args:
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 귀족 이름과 성씨 튜플 (이름, 성)
    """
    from .western_fantasy import generate_western_fantasy_name
    
    # 타입 안전성을 위해 리터럴 문자열 사용
    if gender == "male":
        first_name = generate_western_fantasy_name("male")
    else:
        first_name = generate_western_fantasy_name("female")
        
    surname = random.choice(noble_surnames)
    
    return first_name, surname

def format_noble_name(first_name: str, surname: str) -> str:
    """귀족 이름을 형식에 맞게 포맷팅
    
    Args:
        first_name: 이름
        surname: 성씨
        
    Returns:
        형식에 맞게 포맷팅된 귀족 이름
    """
    return f"{first_name} {surname}" 