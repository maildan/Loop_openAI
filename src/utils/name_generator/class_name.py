"""
캐릭터 클래스별 이름 생성 모듈
마법사, 기사, 도적 등 캐릭터 클래스에 특화된 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload
import random

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]
ClassType: TypeAlias = Literal[
    "마법사", "기사", "도적", "성직자", "용사", "전사", "궁수", 
    "소환사", "용기사", "암살자", "광전사", "정령사", "주술사", 
    "연금술사", "음유시인", "무희"
]

# 🎭 캐릭터 클래스별 이름 패턴
class_name_patterns: Final[dict[str, tuple[str, ...]]] = {
    "마법사": ("미스틱", "아르카나", "셀레스티아", "루나리아", "아스트라", "에테리아"),
    "기사": ("아르케인", "매지카", "메를린", "간달프", "미스터", "세이지"),
    "도적": ("섀도우", "실프", "니야", "로그", "팬텀", "미스트"),
    "성직자": ("세라핌", "엔젤", "홀리", "디바인", "세인트", "프리스티스"),
    "용사": ("헤로인", "챔피언", "세이비어", "레스큐어", "가디언", "프로텍터"),
    "전사": ("워리어", "버서커", "팔라딘", "나이트", "가디언", "디펜더"),
    "궁수": ("아처", "레인저", "스나이퍼", "헌터", "트래커", "마크스맨"),
    "소환사": ("서머너", "네크로맨서", "드루이드", "비스트마스터", "엘레멘탈리스트"),
    "용기사": ("드래곤나이트", "드래곤슬레이어", "드래곤마스터", "드래곤테이머"),
    "암살자": ("어쌔신", "쉐도우", "나이트블레이드", "닌자", "스텔스", "실루엣"),
    "광전사": ("버서커", "레이지", "매드니스", "퓨리", "블러드레이지", "배틀매니악"),
    "정령사": ("엘레멘탈리스트", "스피릿마스터", "소울바인더", "스피릿워커"),
    "주술사": ("샤먼", "보두", "헥서", "커서", "위치닥터", "오컬티스트"),
    "연금술사": ("알케미스트", "포션마스터", "트랜스뮤터", "엘릭서", "믹서"),
    "음유시인": ("바드", "송스트레스", "포엣", "라이머", "멜로디", "하모니"),
    "무희": ("댄서", "퍼포머", "엔터테이너", "아크로뱃", "발레리나", "리듬마스터"),
}

@overload
def generate_by_class(character_class: ClassType, gender: Literal["male"]) -> str: ...

@overload
def generate_by_class(character_class: ClassType, gender: Literal["female"]) -> str: ...

@overload
def generate_by_class(character_class: str, gender: GenderType = "female") -> str: ...

def generate_by_class(character_class: str, gender: GenderType = "female") -> str:
    """클래스별 특화 이름 생성
    
    Args:
        character_class: 캐릭터 클래스명
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 클래스 특화 이름
    """
    from .composed_name import isekai_syllables
    
    if character_class in class_name_patterns:
        base_name = random.choice(class_name_patterns[character_class])

        # 조합으로 변형
        if random.random() < 0.3:  # 30% 확률로 조합형으로 변형
            syllable = random.choice(isekai_syllables["middle"])
            return f"{base_name[:2]}{syllable}{base_name[2:]}"

        return base_name
    else:
        # 클래스가 없으면 기본 이름 생성
        from .isekai_anime import generate_isekai_anime_name
        # 타입 안전성을 위해 리터럴 문자열 사용
        if gender == "male":
            return generate_isekai_anime_name("male")
        else:
            return generate_isekai_anime_name("female") 