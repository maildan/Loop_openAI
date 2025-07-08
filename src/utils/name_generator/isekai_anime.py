"""
이세계 애니메이션 스타일 이름 생성 모듈
에밀리아, 카구야, 림루 같은 이세계/애니메이션 스타일의 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload
from enum import Enum, auto
import random

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]

# 애니메이션 스타일 열거형
class AnimeStyle(Enum):
    ISEKAI = auto()  # 이세계물
    FANTASY = auto()  # 판타지
    SCHOOL = auto()  # 학원물
    MAGIC = auto()  # 마법소녀/소년
    MIXED = auto()  # 혼합

# 🌟 이세계 애니메이션 여주인공 이름들 (에밀리아, 카구야 스타일)
isekai_female_protagonists: Final[list[str]] = [
    # Re:Zero 스타일
    "에밀리아", "렘", "람", "베아트리체", "펠트", "프리실라", "크루쉬", "아나스타시아",
    "엘자", "메일리", "프레데리카", "페트라", "로즈월", "에키드나", "티폰", "세크메트",
    # 카구야님 스타일 (일본+서양 믹스)
    "카구야", "치카", "미코", "하야사카", "이시가미", "시로가네", "카시와기", "마키",
    "타나바타", "이바라", "오시노", "오가", "시라누이", "사부카와", "키요스미",
    # 오버로드 스타일
    "알베도", "샤르티어", "아우라", "마레", "나베랄", "루푸스레기나", "유리", "엔트마",
    "솔류션", "세바스", "데미우르고스", "코키토스", "빅팀", "플레이아데스",
    # 전생슬라임 스타일
    "시즈", "시온", "슈나", "소우에이", "소우카", "베니마루", "하쿠로", "리그르드",
    "가비루", "트레이니", "라미리스", "밀림", "카리온", "클레이맨", "레온",
    # 던전밥 스타일
    "마르실", "파린", "치루치크", "이즈츠미", "라이오스", "센시", "나마리",
    # 리제로 추가
    "파우제", "루크니카", "구스테코", "볼라키아", "플뢰겔", "하르트",
    # 이세계 고전 이름들 (서양+동양 믹스)
    "아리아", "루나", "셀레스티아", "오로라", "이사벨라", "빅토리아", "샬롯", "로제리아",
    "에스텔", "카밀라", "레오나", "디아나", "플로라", "실비아",
    # 마법소녀 스타일
    "사쿠라", "토모요", "메이링", "유키토", "케르베로스", "유에", "에리올", "미도리",
    "아카네", "시로", "쿠로", "아오", "키이로", "무라사키",
    # 하렘 이세계 히로인 이름들
    "아스나", "유키", "실리카", "리즈벳", "사치", "유이", "시논", "리파", "스구하",
]

# 🌟 이세계 애니메이션 남주인공 이름들 (키리토, 나츠키 스타일)
isekai_male_protagonists: Final[list[str]] = [
    # SAO 스타일
    "키리토", "클라인", "아길", "엔드리", "레콘", "유지오", "유진", "카즈토",
    # Re:Zero 스타일
    "스바루", "라인하르트", "빌헬름", "알", "가르피엘", "오토", "리카르도",
    # 오버로드 스타일
    "아인즈", "판도라즈 액터", "세바스", "코키토스", "데미우르고스", "마레", "제로",
    # 전생슬라임 스타일
    "림루", "베니마루", "소우에이", "하쿠로", "리그르드", "가비루", "디아블로",
    # 던전밥 스타일
    "라이오스", "치루치크", "마르실", "나마리", "센시",
    # 귀멸의 칼날 스타일
    "탄지로", "젠이츠", "이노스케", "겐야", "산지", "렌고쿠", "기유", "오바나이",
    # 이세계 고전 이름들 (서양+동양 믹스)
    "아스란", "레온", "카이토", "유토", "하루토", "소우마", "류지", "켄타",
    "유우키", "신지", "카오루", "카즈야", "타쿠야", "료마", "하야테",
    # 마법소년 스타일
    "시란", "샤오란", "유키토", "토우야", "에리올", "쿠로가네", "후마",
    # 하렘 이세계 주인공 이름들
    "키리토", "나츠키", "카즈마", "루데우스", "하지메", "신지", "이치카", "바사라",
    # 무협/사무라이 스타일
    "무사시", "코지로", "한조", "겐지", "료마", "사노스케", "켄신", "사이토",
]

@overload
def generate_isekai_anime_name(gender: Literal["male"]) -> str: ...

@overload
def generate_isekai_anime_name(gender: Literal["female"]) -> str: ...

@overload
def generate_isekai_anime_name(gender: GenderType = "female") -> str: ...

def generate_isekai_anime_name(gender: GenderType = "female") -> str:
    """이세계 애니메이션 스타일 이름 생성
    
    Args:
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 이세계 애니메이션 스타일 이름
    """
    # 성별에 따라 다른 이름 목록 사용
    match gender:
        case "female":
            return random.choice(isekai_female_protagonists)
        case "male":
            return random.choice(isekai_male_protagonists)
        # 두 Literal 타입을 모두 처리했으므로 추가 분기는 불필요
            
def get_anime_name_by_style(style: AnimeStyle, gender: GenderType = "female") -> str:
    """특정 애니메이션 스타일에 맞는 이름 생성
    
    Args:
        style: 애니메이션 스타일
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 이름
    """
    # 스타일별 이름 생성
    match style:
        case AnimeStyle.ISEKAI:
            # 이세계물 스타일 (Re:Zero, 전생슬라임 등)
            if gender == "female":
                return random.choice([name for name in isekai_female_protagonists[:40]])
            else:
                return random.choice([name for name in isekai_male_protagonists[:30]])
        case AnimeStyle.FANTASY:
            # 판타지 스타일 (던전밥, 오버로드 등)
            if gender == "female":
                return random.choice([name for name in isekai_female_protagonists[40:60]])
            else:
                return random.choice([name for name in isekai_male_protagonists[30:50]])
        case AnimeStyle.SCHOOL:
            # 학원물 스타일 (카구야님, 하이큐 등)
            if gender == "female":
                return random.choice([name for name in isekai_female_protagonists[60:80]])
            else:
                return random.choice([name for name in isekai_male_protagonists[50:70]])
        case AnimeStyle.MAGIC:
            # 마법소녀/소년 스타일
            if gender == "female":
                return random.choice([name for name in isekai_female_protagonists[80:]])
            else:
                return random.choice([name for name in isekai_male_protagonists[70:]])
        case _:
            # 기본값은 혼합 스타일
            return generate_isekai_anime_name(gender) 