"""
서양 판타지 이름 생성 모듈
LOTR, 해리포터 스타일의 이름을 생성합니다.
"""

from typing import Final, Literal, TypeAlias, overload

# 타입 별칭 정의
GenderType: TypeAlias = Literal["male", "female"]

# 🏰 서양 판타지 이름 (LOTR, 해리포터 스타일)
western_fantasy_names: Final[dict[str, list[str]]] = {
    "female": [
        # 엘프 이름들
        "갈라드리엘", "아르웬", "타우리엘", "레골라스", "엘론드", "길갈라드",
        "님로델", "미스란디어", "케레브린달", "이두릴", "넨야", "빌야",
        # 마법사/마녀 이름들
        "허마이오니", "루나", "진니", "몰리", "맥고나갈", "벨라트릭스", "나르시사",
        "안드로메다", "님파도라", "플뢰르", "가브리엘", "라벤더", "파바티",
        # 공주/귀족 이름들
        "이사벨라", "빅토리아", "알렉산드라", "카타리나", "아나스타시아", "엘리자베스",
        "샬롯", "아멜리아", "소피아", "올리비아", "에밀리", "그레이스", "로즈마리",
        # 여신/천사 이름들
        "세라핌", "체루빔", "가브리엘라", "라파엘라", "우리엘라", "미카엘라",
        "아리엘", "카시엘", "라구엘", "라지엘", "하니엘", "카마엘",
    ],
    "male": [
        # 기사/전사 이름들
        "아서", "랜슬롯", "갈라하드", "퍼시발", "가웨인", "트리스탄", "모드레드",
        "보르스", "케이", "베디베르", "라이오넬", "에렉", "아그라베인",
        # 마법사 이름들
        "간달프", "사루만", "라다가스트", "알라타르", "팔란도", "메를린",
        "덤블도어", "스네이프", "루핀", "시리우스", "볼드모트", "그린델왈드",
        # 왕/귀족 이름들
        "아라곤", "보로미르", "파라미르", "데네토르", "세오덴", "에오메르", "엘렌딜",
        "이실두르", "아나리온", "발란딜", "알다리온", "엘렌딜", "이실두르",
        # 신/영웅 이름들
        "오딘", "토르", "로키", "발더", "티르", "헤이드마르", "시그문드", "시구르드",
        "프로도", "샘", "메리", "피핀", "빌보", "김리", "레골라스", "보로미르",
    ],
}

@overload
def generate_western_fantasy_name(gender: Literal["male"]) -> str: ...

@overload
def generate_western_fantasy_name(gender: Literal["female"]) -> str: ...

@overload
def generate_western_fantasy_name(gender: GenderType = "female") -> str: ...

def generate_western_fantasy_name(gender: GenderType = "female") -> str:
    """서양 판타지 스타일 이름 생성
    
    Args:
        gender: 성별 ("male" 또는 "female")
        
    Returns:
        생성된 서양 판타지 스타일 이름
    """
    import random
    
    # gender 값은 매개변수 타입이 보장하므로 추가 검사는 생략
        
    return random.choice(western_fantasy_names[gender]) 