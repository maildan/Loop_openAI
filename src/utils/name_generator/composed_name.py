"""
조합형 이름 생성 모듈
음절을 조합하여 새로운 이세계/판타지 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload
import random
from functools import lru_cache

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]
SyllableType: TypeAlias = Literal["prefix", "middle", "suffix"]

# 💫 조합용 음절 (진짜 이세계 느낌나는)
isekai_syllables: Final[dict[str, tuple[str, ...]]] = {
    "prefix": (
        # 일본어 느낌
        "아", "카", "사", "타", "나", "하", "마", "야", "라", "와",
        "키", "시", "치", "니", "히", "미", "리", "유", "쿠", "스",
        "에", "케", "세", "테", "네", "헤", "메", "레", "웨", "츠",
        "오", "코", "소", "토", "노", "호", "모", "요", "로", "루",
        # 서양어 느낌
        "알", "벨", "셀", "델", "엘", "펠", "겔", "헬", "이", "젤",
        "아르", "베르", "세르", "데르", "에르", "페르", "게르", "헤르",
        "아리", "베리", "세리", "데리", "에리", "페리", "게리", "헤리",
        "아로", "베로", "세로", "데로", "에로", "페로", "게로", "헤로",
    ),
    "middle": (
        "미", "리", "티", "니", "비", "키", "시", "피", "히", "지",
        "라", "나", "마", "사", "카", "타", "파", "하", "야", "와",
        "루", "누", "무", "수", "쿠", "투", "푸", "후", "유", "주",
        "레", "네", "메", "세", "케", "테", "페", "헤", "예", "제",
        "로", "노", "모", "소", "코", "토", "포", "호", "요", "조",
        # 서양어 느낌
        "란", "렌", "린", "론", "룬", "라", "레", "리", "로", "루",
        "탄", "텐", "틴", "톤", "튠", "타", "테", "티", "토", "투",
        "단", "덴", "딘", "돈", "둔", "다", "데", "디", "도", "두",
        "만", "멘", "민", "몬", "문", "마", "메", "미", "모", "무",
        "산", "센", "신", "손", "순", "사", "세", "시", "소", "수",
        "잔", "젠", "진", "존", "준", "자", "제", "지", "조", "주",
    ),
    "suffix": (
        # 여성형 어미
        "아", "야", "나", "라", "마", "사", "카", "타", "파", "하",
        "에", "예", "네", "레", "메", "세", "케", "테", "페", "헤",
        "이", "이", "니", "리", "미", "시", "키", "티", "피", "히",
        "아나", "야나", "나나", "라나", "마나", "사나", "카나", "타나",
        "에나", "예나", "네나", "레나", "메나", "세나", "케나", "테나",
        "이나", "이나", "니나", "리나", "미나", "시나", "키나", "티나",
        "아리아", "야리아", "나리아", "라리아", "마리아", "사리아",
        "에리아", "예리아", "네리아", "레리아", "메리아", "세리아",
        "이리아", "이리아", "니리아", "리리아", "미리아", "시리아",
        # 남성형 어미
        "오", "요", "노", "로", "모", "소", "코", "토", "포", "호",
        "우", "유", "누", "루", "무", "수", "쿠", "투", "푸", "후",
        "온", "욘", "논", "론", "몬", "손", "콘", "톤", "폰", "혼",
        "우스", "유스", "누스", "루스", "무스", "수스", "쿠스", "투스",
        "오르", "요르", "노르", "로르", "모르", "소르", "코르", "토르",
        "우르", "유르", "누르", "루르", "무르", "수르", "쿠르", "투르",
        "오스", "요스", "노스", "로스", "모스", "소스", "코스", "토스",
        "우스", "유스", "누스", "루스", "무스", "수스", "쿠스", "투스",
    ),
}

# 성별에 따른 접미사 그룹
female_suffix_indices: Final[tuple[int, ...]] = tuple(range(0, 60))
male_suffix_indices: Final[tuple[int, ...]] = tuple(range(60, 120))

@lru_cache(maxsize=128)
def get_suffix_by_gender(gender: GenderType) -> tuple[str, ...]:
    """성별에 따른 접미사 반환 (캐싱)
    
    Args:
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        성별에 맞는 접미사 튜플
    """
    all_suffixes = isekai_syllables["suffix"]
    if gender == "female":
        return tuple(all_suffixes[i] for i in female_suffix_indices if i < len(all_suffixes))
    else:
        return tuple(all_suffixes[i] for i in male_suffix_indices if i < len(all_suffixes))

@overload
def generate_composed_name(gender: Literal["male"]) -> str: ...

@overload
def generate_composed_name(gender: Literal["female"]) -> str: ...

@overload
def generate_composed_name(gender: GenderType = "female") -> str: ...

def generate_composed_name(gender: GenderType = "female") -> str:
    """조합형 이름 생성
    
    Args:
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 조합형 이름
    """
    # 접두사와 중간 음절은 공통
    prefix = random.choice(isekai_syllables["prefix"])
    middle = random.choice(isekai_syllables["middle"])
    
    # 성별에 따른 접미사 선택
    gender_suffixes = get_suffix_by_gender(gender)
    suffix = random.choice(gender_suffixes)
    
    # 음절 조합
    name = f"{prefix}{middle}{suffix}"
    
    # 특정 패턴 수정 (발음 자연스럽게)
    name = name.replace("아아", "아").replace("에에", "에").replace("이이", "이")
    name = name.replace("오오", "오").replace("우우", "우")
    
    return name 