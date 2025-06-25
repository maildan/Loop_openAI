#!/usr/bin/env python3
"""
🔥 GIGACHAD Character Converter v2.0 🔥
VL 데이터셋을 기가차드급으로 변환하는 자동화 스크립트

작성자: 기가차드 AI
목적: C001, C002, C003 같은 병신 캐릭터들을 진짜 한국 이름과 개성으로 바꾸기
업데이트: 판타지 장르별 이름, 더 정교한 중복 방지, 완전한 캐릭터 매핑
"""

import json
import os
import re
import random
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse

class GigaChadNameGenerator:
    """기가차드급 한국 이름 생성기 v2.0"""
    
    def __init__(self):
        # 한국 성씨 리스트 (빈도순) - 웹 검색 기반 확장
        self.surnames = [
            "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
            "한", "오", "서", "신", "권", "황", "안", "송", "류", "전",
            "홍", "고", "문", "양", "손", "배", "조", "백", "허", "유",
            "남", "심", "노", "정", "하", "곽", "성", "차", "주", "우",
            "구", "신", "임", "나", "전", "민", "유", "진", "지", "엄",
            "채", "원", "천", "방", "공", "강", "현", "함", "변", "염"
        ]
        
        # 현대 남자 이름 (2글자) - 웹 검색 기반
        self.modern_male_names = [
            "민수", "지훈", "성호", "준영", "현우", "태민", "동현", "승현", "민호", "진우",
            "상훈", "기현", "재욱", "성민", "도현", "건우", "세준", "준서", "시우", "하준",
            "주원", "도윤", "예준", "시윤", "지후", "승우", "연우", "정우", "지환", "건희",
            "현준", "지안", "승민", "재현", "태윤", "민준", "서준", "예성", "도영", "지원",
            "강민", "태현", "민성", "준혁", "성진", "현수", "지성", "윤호", "태준", "정민"
        ]
        
        # 현대 여자 이름 (2글자) - 웹 검색 기반
        self.modern_female_names = [
            "지민", "수현", "예은", "서연", "하은", "지우", "유진", "서현", "민지", "채원",
            "다은", "소영", "혜진", "은지", "수빈", "예린", "지영", "수진", "나연", "시은",
            "가은", "윤서", "하린", "세은", "주은", "서영", "다현", "유나", "예지", "수연",
            "미영", "정은", "혜원", "소연", "지은", "유경", "은서", "채은", "서윤", "나은",
            "수정", "예나", "하영", "서은", "민서", "다영", "지혜", "유진", "서진", "예원"
        ]
        
        # 판타지 남자 이름 (고전적/판타지적) - 이세계 스타일 대폭 확장
        self.fantasy_male_names = [
            # 기존 이름들
            "무영", "검성", "화랑", "천무", "용검", "철기", "강철", "번개", "폭풍", "화염",
            "빙하", "천둥", "바람", "구름", "하늘", "별빛", "달빛", "태양", "광명", "어둠",
            "그림자", "칼날", "방패", "창검", "활시", "마법", "신비", "용맹", "영웅", "전사",
            
            # 이세계 애니메이션 스타일 이름들 (서양풍)
            "아리우스", "카이저", "레오나르드", "세바스찬", "루시퍼", "가브리엘", "라파엘", "미카엘",
            "아드리안", "알렉산더", "루시안", "다미안", "발렌틴", "막시밀리안", "아우구스투스", "율리우스",
            "레이나르드", "발터", "지크프리드", "라그나르", "토르", "오딘", "프레이", "로키",
            "아르투르", "랜슬롯", "갈라하드", "퍼시발", "가웨인", "트리스탄", "가레스", "베디비어",
            
            # 일본풍 이세계 이름들
            "류지", "카즈토", "타츠야", "유키", "히로", "렌", "쇼타", "다이키", "하루토", "소라",
            "아키라", "히카루", "타쿠미", "신지", "케이", "료", "쇼", "진", "레이", "카이",
            "시로", "쿠로", "아오", "미도리", "아카", "키", "텐", "라이", "후우", "미즈",
            
            # 마법사/현자 스타일
            "메를린", "간달프", "사루만", "라다가스트", "알랜드릴", "엘론드", "길갈라드", "이시르",
            "아르케인", "매지카", "스펠바인드", "미스틱", "오라클", "비저너리", "세이지", "마스터",
            
            # 용사/기사 스타일
            "드래곤베인", "소드마스터", "나이트", "팔라딘", "크루세이더", "챔피언", "히어로", "가디언",
            "프로텍터", "디펜더", "워리어", "버서커", "글래디에이터", "듀얼리스트", "블레이드", "소드",
            
            # 이세계 특유의 이름들 (루데우스, 시리우스 스타일)
            "루데우스", "시리우스", "아인즈", "림루", "나츠키", "카즈마", "타냐", "아인크라드",
            "키리토", "아스나", "클라인", "아길", "실리카", "리즈벳", "사치", "유이",
            "레이", "아스카", "신지", "겐도", "카와루", "토지", "케이", "리츠코",
            
            # 원소/속성 기반 이름들
            "이그니스", "아쿠아", "테라", "벤투스", "룩스", "테네브라", "글라키에스", "플람마",
            "풀구르", "토니트루", "솔", "루나", "스텔라", "코스모스", "에테르", "마나"
        ]
        
        # 판타지 여자 이름 (고전적/판타지적) - 이세계 스타일 대폭 확장
        self.fantasy_female_names = [
            # 기존 이름들
            "달님", "별님", "꽃님", "바람", "구름", "하늘", "물결", "노을", "새벽", "황혼",
            "은빛", "금빛", "옥빛", "진주", "산호", "비취", "수정", "다이아", "루비", "사파이어",
            "나비", "꽃잎", "이슬", "향기", "미소", "웃음", "노래", "춤사위", "달무리", "별무리",
            
            # 이세계 애니메이션 스타일 이름들 (서양풍)
            "아리아", "루나", "셀레스티아", "오로라", "이사벨라", "빅토리아", "알렉산드라", "카타리나",
            "아나스타시아", "엘리자베스", "샬롯", "아멜리아", "소피아", "올리비아", "에밀리", "그레이스",
            "로즈마리", "라벤더", "재스민", "릴리", "아이리스", "바이올렛", "다프네", "로렐",
            "세레나", "루시아", "클라라", "마리아", "안나", "엘레나", "니나", "베라",
            
            # 일본풍 이세계 이름들
            "유키", "사쿠라", "아야", "미사키", "리나", "나나", "마이", "에미", "레이", "아이",
            "미유", "카나", "하나", "미카", "사야", "아카네", "시오리", "유이", "미오", "리오",
            "츠키", "호시", "소라", "우미", "야마", "카제", "히카리", "카게", "유메", "아이",
            
            # 여신/성녀 스타일
            "아테나", "아르테미스", "아프로디테", "헤라", "데메테르", "헤스티아", "이시스", "프레이야",
            "브리기드", "모리간", "세레스", "비너스", "미네르바", "다이아나", "주노", "베스타",
            
            # 마법소녀/마녀 스타일
            "위치", "소서리스", "엔챈트리스", "미스트리스", "아르카나", "매지카", "스펠캐스터", "오라클",
            "프리스티스", "시어", "비저너리", "드루이드", "샤먼", "템플러", "아콜라이트", "클레릭",
            
            # 이세계 특유의 이름들
            "아스나", "실리카", "리즈벳", "사치", "유이", "시논", "리파", "스구하",
            "알베도", "샬티어", "아우라", "마레", "코키토스", "데미우르고스", "세바스", "플레이아데스",
            "렘", "램", "에밀리아", "펠트", "프리실라", "크루쉬", "아나스타시아", "베아트리체",
            
            # 원소/속성 기반 이름들
            "아쿠아", "이그니아", "테라", "루나리아", "솔라리아", "스텔라리아", "에테리아", "마나리아",
            "프리즈마", "크리스탈", "오팔", "펄", "엠버", "제이드", "토파즈", "가넷",
            
            # 천사/악마 스타일
            "세라핌", "체루빔", "가브리엘라", "라파엘라", "우리엘라", "미카엘라", "아리엘", "카시엘",
            "릴리스", "모르가나", "세이렌", "메두사", "키르케", "헤카테", "페르세포네", "판도라"
        ]
        
        # 무협/사극 남자 이름
        self.historical_male_names = [
            "검무", "철혈", "광풍", "뇌전", "화산", "빙검", "용호", "맹호", "독수리", "매화",
            "소나무", "대나무", "철산", "금강", "옥룡", "은호", "청룡", "백호", "주작", "현무"
        ]
        
        # 무협/사극 여자 이름  
        self.historical_female_names = [
            "월화", "설화", "춘화", "매화", "국화", "연화", "옥화", "금화", "은화", "주화",
            "청화", "백화", "홍화", "자화", "황화", "녹화", "보화", "향화", "미화", "선화"
        ]
        
        # SF/미래 남자 이름
        self.scifi_male_names = [
            "네오", "제로", "알파", "베타", "감마", "델타", "오메가", "프라임", "매트릭스", "사이버",
            "디지털", "바이너리", "코드", "해커", "시스템", "프로그램", "데이터", "네트워크", "서버", "클라우드"
        ]
        
        # SF/미래 여자 이름
        self.scifi_female_names = [
            "루나", "스텔라", "오로라", "노바", "갤럭시", "코스모", "플라즈마", "에너지", "레이저", "홀로그램",
            "사이버", "디지털", "바이트", "픽셀", "벡터", "매트릭스", "알고리즘", "인터페이스", "시스템", "네트워크"
        ]
        
        # 캐릭터 성격 형용사 (확장)
        self.personalities = [
            "용감한", "지혜로운", "친절한", "냉정한", "유머러스한", "진지한", "낙천적인", "신중한",
            "열정적인", "차분한", "호기심 많은", "의리 있는", "고집 센", "섬세한", "활발한", "내성적인",
            "정의로운", "교활한", "순수한", "현실적인", "꿈 많은", "실용적인", "감성적인", "이성적인",
            "야심찬", "겸손한", "자신감 넘치는", "신비로운", "매력적인", "카리스마 있는", "영리한", "창의적인"
        ]
        
        # 말투 패턴 (확장)
        self.speech_patterns = [
            "정중하고 예의 바른 말투", "친근하고 편안한 말투", "직설적이고 솔직한 말투",
            "부드럽고 따뜻한 말투", "유머가 섞인 경쾌한 말투", "조용하고 신중한 말투",
            "열정적이고 에너지 넘치는 말투", "차분하고 안정적인 말투", "신비롭고 우아한 말투",
            "거칠지만 진심 어린 말투", "지적이고 논리적인 말투", "감성적이고 시적인 말투"
        ]
        
        # 전역 중복 방지를 위한 집합
        self.used_names = set()
        
        # 이세계 전용 이름들 (더 특별한 조합)
        self.isekai_male_names = [
            # 서양 + 일본 믹스
            "아키라", "렌", "카이", "류", "쇼", "진", "레이", "소라", "하루", "유키",
            "루시퍼", "가브리엘", "미카엘", "라파엘", "우리엘", "아리엘", "카시엘", "라구엘",
            "메를린", "아서", "랜슬롯", "갈라하드", "퍼시발", "가웨인", "트리스탄", "베디비어",
            "시그르드", "라그나르", "토르", "오딘", "프레이", "발더", "로키", "헤임달",
            "아인즈", "모몬가", "터치미", "울베르트", "페로로치노", "부큐브", "타키미카즈치",
            "키리토", "카즈토", "클라인", "아길", "톤키", "나베르", "크라디엘", "다크리프터"
        ]
        
        self.isekai_female_names = [
            # 서양 + 일본 믹스
            "아야", "유이", "레이", "아이", "미오", "리오", "나나", "마이", "에미", "사야",
            "아리아", "루나", "셀레스티아", "오로라", "이사벨라", "빅토리아", "알렉산드라", "아나스타시아",
            "아테나", "아르테미스", "아프로디테", "헤라", "데메테르", "헤스티아", "프레이야", "이둔",
            "알베도", "샬티어", "아우라", "마레", "나베랄", "루푸스레기나", "유리", "엔트마",
            "아스나", "실리카", "리즈벳", "사치", "유이", "시논", "리파", "스구하",
            "렘", "람", "에밀리아", "펠트", "프리실라", "크루쉬", "아나스타시아", "베아트리체"
        ]
        
        # 장르별 이름 매핑 (이세계 장르 추가)
        self.genre_names = {
            "modern": {
                "male": self.modern_male_names,
                "female": self.modern_female_names
            },
            "fantasy": {
                "male": self.fantasy_male_names,
                "female": self.fantasy_female_names
            },
            "isekai": {  # 새로운 이세계 장르!
                "male": self.isekai_male_names,
                "female": self.isekai_female_names
            },
            "historical": {
                "male": self.historical_male_names,
                "female": self.historical_female_names
            },
            "scifi": {
                "male": self.scifi_male_names,
                "female": self.scifi_female_names
            }
        }
    
    def detect_genre(self, title: str, text_sample: str) -> str:
        """제목과 텍스트 샘플로 장르 감지 - 이세계/판타지 키워드 대폭 확장"""
        title_lower = title.lower()
        text_sample_lower = text_sample.lower()
        combined_text = f"{title_lower} {text_sample_lower}"
        
        # 이세계/판타지 키워드 (대폭 확장)
        fantasy_keywords = [
            # 기본 판타지
            "마법", "드래곤", "엘프", "마법사", "기사", "검", "성", "왕국", "마왕", "용사",
            "던전", "길드", "모험", "퀘스트", "레벨", "스킬", "아이템", "몬스터", "보스",
            
            # 이세계 특화
            "이세계", "전생", "환생", "소환", "트럭", "신", "여신", "치트", "스테이터스", "능력",
            "다른 세계", "이계", "전이", "소환술", "마물", "슬라임", "오버로드", "전직",
            
            # 판타지 종족/직업
            "드워프", "오크", "고블린", "데몬", "천사", "악마", "언데드", "리치", "뱀파이어",
            "팔라딘", "로그", "아처", "메이지", "클레릭", "워리어", "버서커", "어쌔신",
            
            # 마법/스킬 관련
            "파이어볼", "힐링", "텔레포트", "인챈트", "서먼", "메테오", "라이트닝", "아이스",
            "배리어", "버프", "디버프", "리저렉션", "디스펠", "실드", "오라", "마나",
            
            # 게임 시스템
            "경험치", "HP", "MP", "공격력", "방어력", "민첩성", "지능", "체력", "운",
            "인벤토리", "장비", "무기", "방어구", "포션", "엘릭서", "스크롤", "보석"
        ]
        
        # 사극/무협 키워드  
        historical_keywords = [
            "조선", "한양", "궁궐", "대감", "나리", "소저", "공자", "무림", "검법", "내공",
            "황제", "황후", "왕자", "공주", "상궁", "내관", "암행어사", "포도청", "의금부",
            "문파", "장문인", "제자", "사부", "무공", "기공", "진기", "검기", "도법"
        ]
        
        # SF/미래 키워드
        scifi_keywords = [
            "우주", "로봇", "AI", "사이보그", "미래", "타임머신", "외계인", "우주선",
            "안드로이드", "홀로그램", "레이저", "플라즈마", "워프", "하이퍼스페이스",
            "사이버", "매트릭스", "VR", "AR", "나노", "바이오", "제네틱", "클론"
        ]
        
        # 이세계 특화 키워드 (더 구체적)
        isekai_keywords = [
            "이세계", "전생", "환생", "소환", "트럭", "치트", "스테이터스", "레벨업",
            "다른 세계", "이계", "전이", "소환술", "오버로드", "전직", "슬라임",
            "용사", "마왕", "길드", "던전", "퀘스트", "아이템", "인벤토리"
        ]
        
        fantasy_score = sum(1 for keyword in fantasy_keywords if keyword in combined_text)
        isekai_score = sum(1 for keyword in isekai_keywords if keyword in combined_text)
        historical_score = sum(1 for keyword in historical_keywords if keyword in combined_text)
        scifi_score = sum(1 for keyword in scifi_keywords if keyword in combined_text)
        
        # 점수가 높은 장르 선택 (이세계 우선)
        if isekai_score >= 2:  # 이세계 키워드가 2개 이상이면 확실히 이세계
            return "isekai"
        elif isekai_score > 0 and isekai_score >= fantasy_score:
            return "isekai"
        elif fantasy_score >= 2:  # 판타지 키워드가 2개 이상이면 확실히 판타지
            return "fantasy"
        elif fantasy_score > 0 and fantasy_score > historical_score and fantasy_score > scifi_score:
            return "fantasy"
        elif historical_score > 0:
            return "historical"
        elif scifi_score > 0:
            return "scifi"
        else:
            return "modern"
    
    def generate_unique_name(self, gender: str = "random", genre: str = "modern") -> str:
        """중복되지 않는 한국 이름 생성 (장르별)"""
        max_attempts = 1000
        
        for attempt in range(max_attempts):
            surname = random.choice(self.surnames)
            
            # 장르와 성별에 따른 이름 선택
            if genre in self.genre_names:
                if gender == "male":
                    given_names = self.genre_names[genre]["male"]
                elif gender == "female":
                    given_names = self.genre_names[genre]["female"]
                else:
                    given_names = self.genre_names[genre]["male"] + self.genre_names[genre]["female"]
            else:
                # 기본값은 현대식
                if gender == "male":
                    given_names = self.modern_male_names
                elif gender == "female":
                    given_names = self.modern_female_names
                else:
                    given_names = self.modern_male_names + self.modern_female_names
            
            given_name = random.choice(given_names)
            full_name = f"{surname}{given_name}"
            
            if full_name not in self.used_names:
                self.used_names.add(full_name)
                return full_name
        
        # 최후의 수단: 숫자 추가
        base_name = f"{random.choice(self.surnames)}{random.choice(self.modern_male_names + self.modern_female_names)}"
        counter = 1
        while f"{base_name}{counter}" in self.used_names:
            counter += 1
        full_name = f"{base_name}{counter}"
        self.used_names.add(full_name)
        return full_name
    
    def generate_character_info(self, name: str, genre: str = "modern") -> Dict:
        """캐릭터 정보 생성 (장르별)"""
        base_info = {
            "name": name,
            "personality": random.choice(self.personalities),
            "speech_pattern": random.choice(self.speech_patterns),
            "background": f"{name}의 과거 이야기",
            "traits": random.sample(self.personalities, 2),
            "genre": genre
        }
        
        # 장르별 추가 정보
        if genre == "fantasy":
            base_info["class"] = random.choice(["전사", "마법사", "궁수", "도적", "성직자", "팔라딘"])
            base_info["magic_affinity"] = random.choice(["화염", "빙결", "번개", "치유", "어둠", "빛"])
        elif genre == "historical":
            base_info["social_class"] = random.choice(["양반", "중인", "평민", "무사", "상인"])
            base_info["martial_arts"] = random.choice(["검법", "창법", "권법", "경공술", "내공"])
        elif genre == "scifi":
            base_info["augmentation"] = random.choice(["사이버네틱 팔", "강화된 눈", "뇌 임플란트", "없음"])
            base_info["tech_level"] = random.choice(["기본", "고급", "최첨단", "실험적"])
        
        return base_info


class GigaChadTextImprover:
    """기가차드급 텍스트 개선기 v2.0"""
    
    def __init__(self):
        # 감정 표현 개선 사전 (확장)
        self.emotion_improvements = {
            "화난다": ["분노로 주먹을 꽉 쥐었다", "화가 치밀어 올랐다", "분노가 폭발했다", "격분했다", "분개했다"],
            "슬프다": ["눈물이 주르륵 흘렀다", "가슴이 먹먹해졌다", "마음이 아팠다", "서글픔에 잠겼다", "애절해했다"],
            "기쁘다": ["환한 미소를 지었다", "기쁨에 겨워 했다", "행복해했다", "즐거워했다", "희색을 감추지 못했다"],
            "놀란다": ["깜짝 놀라 뒤로 물러섰다", "충격을 받았다", "당황했다", "경악했다", "소스라치게 놀랐다"],
            "웃는다": ["활짝 웃었다", "미소를 지었다", "즐겁게 웃었다", "방긋 웃었다", "싱긋 웃었다"],
            "무서워한다": ["공포에 떨었다", "두려움에 몸을 움츠렸다", "무서워 벌벌 떨었다", "공포에 질렸다"],
            "부끄러워한다": ["얼굴이 빨갛게 달아올랐다", "수줍어했다", "부끄러워했다", "민망해했다"]
        }
        
        # 행동 표현 개선 (확장)
        self.action_improvements = {
            "말한다": ["말했다", "이야기했다", "속삭였다", "외쳤다", "중얼거렸다", "소리쳤다", "부르짖었다"],
            "간다": ["향했다", "걸어갔다", "뛰어갔다", "천천히 갔다", "급히 갔다", "성큼성큼 갔다"],
            "본다": ["바라봤다", "응시했다", "힐끗 봤다", "뚫어져라 봤다", "지켜봤다", "관찰했다"],
            "듣는다": ["들었다", "귀 기울였다", "경청했다", "엿들었다", "주의 깊게 들었다"],
            "생각한다": ["생각했다", "고민했다", "숙고했다", "곰곰 생각했다", "심사숙고했다"],
            "움직인다": ["움직였다", "이동했다", "옮겼다", "흔들었다", "요동쳤다"]
        }
        
        # 장르별 표현 개선
        self.genre_expressions = {
            "fantasy": {
                "공격한다": ["마법을 시전했다", "검을 휘둘렀다", "주문을 외웠다", "마력을 방출했다"],
                "방어한다": ["방패를 들었다", "보호막을 쳤다", "마법진을 그렸다", "결계를 펼쳤다"]
            },
            "historical": {
                "인사한다": ["절을 올렸다", "예를 갖췄다", "공손히 인사했다", "머리를 숙였다"],
                "화난다": ["노기가 치밀었다", "분기가 등등했다", "격분했다", "진노했다"]
            },
            "scifi": {
                "통신한다": ["홀로그램으로 연결했다", "뇌파로 소통했다", "디지털 신호를 보냈다"],
                "분석한다": ["데이터를 스캔했다", "시스템을 분석했다", "알고리즘을 실행했다"]
            }
        }
    
    def improve_sentence(self, sentence: str, character_map: Dict[str, str], genre: str = "modern") -> str:
        """문장을 기가차드급으로 개선 (장르별)"""
        # 1단계: 한국어 조사를 고려한 캐릭터 교체
        for old_char, new_char in character_map.items():
            # 방법 1: 조사가 붙은 경우도 처리 (C001은, C001이, C001을, C001의 등)
            korean_particles = ['은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로', '와', '과', '아', '야']
            
            # 조사 없이 단독으로 나오는 경우
            pattern = r'\b' + re.escape(old_char) + r'(?=[^가-힣A-Za-z0-9]|$)'
            sentence = re.sub(pattern, new_char, sentence)
            
            # 조사가 붙은 경우들
            for particle in korean_particles:
                pattern = re.escape(old_char) + particle
                replacement = new_char + particle
                sentence = sentence.replace(pattern, replacement)
        
        # 2단계: 여전히 남은 C 패턴들 확인
        remaining_c_patterns = re.findall(r'C\d{2,3}', sentence)
        if remaining_c_patterns:
            print(f"⚠️  여전히 남은 C 패턴들: {remaining_c_patterns}")
            # 남은 패턴들을 강제로 교체 (혹시 매핑에 있다면)
            for pattern in remaining_c_patterns:
                if pattern in character_map:
                    sentence = sentence.replace(pattern, character_map[pattern])
        
        # 4단계: 감정 표현 개선
        for old_emotion, new_emotions in self.emotion_improvements.items():
            if old_emotion in sentence:
                sentence = sentence.replace(old_emotion, random.choice(new_emotions))
        
        # 5단계: 행동 표현 개선
        for old_action, new_actions in self.action_improvements.items():
            if old_action in sentence:
                sentence = sentence.replace(old_action, random.choice(new_actions))
        
        # 6단계: 장르별 표현 개선
        if genre in self.genre_expressions:
            for old_expr, new_exprs in self.genre_expressions[genre].items():
                if old_expr in sentence:
                    sentence = sentence.replace(old_expr, random.choice(new_exprs))
        
        # 7단계: 단조로운 표현 개선
        sentence = self._enhance_dialogue(sentence)
        
        return sentence
    
    def _enhance_dialogue(self, sentence: str) -> str:
        """대화문 개선"""
        # "은/는 말했다" 패턴 개선
        patterns = [
            (r'(\w+)은 말했다', r'\1가 말했다'),
            (r'(\w+)는 말했다', r'\1가 이야기했다'),
            (r'(\w+)이 말했다', r'\1가 말했다'),
        ]
        
        for pattern, replacement in patterns:
            sentence = re.sub(pattern, replacement, sentence)
        
        # 특별 처리: "가 말했다" 패턴은 동적으로 처리
        def replace_said(match):
            name = match.group(1)
            verbs = ["말했다", "이야기했다", "속삭였다", "외쳤다"]
            return f'{name}가 {random.choice(verbs)}'
        
        sentence = re.sub(r'(\w+)가 말했다', replace_said, sentence)
        
        return sentence


class GigaChadConverter:
    """메인 변환기 클래스 v2.0"""
    
    def __init__(self):
        self.name_generator = GigaChadNameGenerator()
        self.text_improver = GigaChadTextImprover()
    
    def extract_characters(self, text_list: List[str]) -> List[str]:
        """텍스트에서 모든 C숫자 캐릭터 추출 (C001~C999)"""
        characters = set()
        # 더 강력한 패턴으로 모든 C숫자 형태 캐치
        pattern = r'C\d{3}'  # 단어 경계 제거하고 더 광범위하게
        
        # 전체 텍스트를 하나의 긴 문자열로 합쳐서 검색
        full_text = ' '.join(text_list)
        matches = re.findall(pattern, full_text)
        characters.update(matches)
        
        # 각 텍스트에서도 개별적으로 검색
        for text in text_list:
            matches = re.findall(pattern, text)
            characters.update(matches)
        
        print(f"🔍 추출된 모든 캐릭터: {sorted(list(characters))}")
        return sorted(list(characters))
    
    def create_character_mapping(self, characters: List[str], genre: str = "modern") -> Tuple[Dict[str, str], Dict[str, Dict]]:
        """캐릭터 매핑과 정보 생성 (장르별)"""
        character_map = {}
        character_info = {}
        
        for char in characters:
            # 캐릭터 번호에 따라 성별 추정 (홀수=남성, 짝수=여성, 단순한 규칙)
            char_num = int(char[1:])  # C001 -> 1
            gender = "male" if char_num % 2 == 1 else "female"
            
            new_name = self.name_generator.generate_unique_name(gender, genre)
            character_map[char] = new_name
            character_info[new_name] = self.name_generator.generate_character_info(new_name, genre)
        
        return character_map, character_info
    
    def extract_characters_from_novel(self, data: Dict) -> List[str]:
        """VL_novel 형태의 데이터에서 모든 캐릭터 추출"""
        characters = set()
        pattern = r'\bC\d{3}\b'  # 더 강력한 패턴
        
        # characters 필드에서 추출
        if 'characters' in data:
            for char in data['characters']:
                if re.match(pattern, char):
                    characters.add(char)
        
        # storyline에서도 추출
        if 'units' in data:
            for unit in data['units']:
                if 'storyline' in unit:
                    matches = re.findall(pattern, unit['storyline'])
                    characters.update(matches)
                
                if 'characters' in unit:
                    for char in unit['characters']:
                        if re.match(pattern, char):
                            characters.add(char)
                
                if 'story_scripts' in unit:
                    for script in unit['story_scripts']:
                        if 'content' in script:
                            matches = re.findall(pattern, script['content'])
                            characters.update(matches)
                        if 'character' in script and isinstance(script['character'], list):
                            for char in script['character']:
                                if re.match(pattern, char):
                                    characters.add(char)
        
        return sorted(list(characters))
    
    def improve_novel_content(self, data: Dict, character_map: Dict[str, str], genre: str) -> Dict:
        """VL_novel 형태의 content 개선"""
        improved_data = data.copy()
        
        # characters 필드 업데이트
        if 'characters' in improved_data:
            new_characters = []
            for char in improved_data['characters']:
                if char in character_map:
                    new_characters.append(character_map[char])
                else:
                    new_characters.append(char)
            improved_data['characters'] = new_characters
        
        # units의 모든 텍스트 개선
        if 'units' in improved_data:
            for unit in improved_data['units']:
                # storyline도 개선
                if 'storyline' in unit:
                    unit['storyline'] = self.text_improver.improve_sentence(
                        unit['storyline'], character_map, genre
                    )
                
                # characters 필드 업데이트 (unit 레벨)
                if 'characters' in unit:
                    new_unit_characters = []
                    for char in unit['characters']:
                        if char in character_map:
                            new_unit_characters.append(character_map[char])
                        else:
                            new_unit_characters.append(char)
                    unit['characters'] = new_unit_characters
                
                # story_scripts 개선
                if 'story_scripts' in unit:
                    for script in unit['story_scripts']:
                        # content 개선
                        if 'content' in script:
                            script['content'] = self.text_improver.improve_sentence(
                                script['content'], character_map, genre
                            )
                        
                        # character 리스트 업데이트
                        if 'character' in script and isinstance(script['character'], list):
                            new_character_list = []
                            for char in script['character']:
                                if char in character_map:
                                    new_character_list.append(character_map[char])
                                else:
                                    new_character_list.append(char)
                            script['character'] = new_character_list
        
        return improved_data

    def convert_json_file(self, input_path: str, output_path: str) -> bool:
        """JSON 파일 변환"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # VL_novel 타입 확인
            is_novel = data.get('type') == 'novel' or 'units' in data
            
            if is_novel:
                # VL_novel 처리
                characters = self.extract_characters_from_novel(data)
                if not characters:
                    print(f"⚠️  캐릭터가 없는 파일: {input_path}")
                    # 캐릭터가 없어도 파일은 복사
                    new_data = {
                        **data,
                        "id": f"{data.get('id', 'unknown')}_GIGACHAD",
                        "conversion_info": {
                            "original_file": input_path,
                            "converted_characters": 0,
                            "detected_genre": "novel",
                            "gigachad_version": "2.0"
                        }
                    }
                else:
                    # 장르 감지
                    title = data.get('title', '')
                    # novel의 경우 첫 번째 unit의 첫 번째 content로 장르 감지
                    text_sample = ""
                    if 'units' in data and data['units'] and 'story_scripts' in data['units'][0]:
                        scripts = data['units'][0]['story_scripts'][:5]
                        text_sample = ' '.join([s.get('content', '') for s in scripts])
                    
                    genre = self.name_generator.detect_genre(title, text_sample)
                    
                    # 캐릭터 매핑 생성
                    character_map, character_info = self.create_character_mapping(characters, genre)
                    
                    # 내용 개선
                    improved_data = self.improve_novel_content(data, character_map, genre)
                    
                    # 새로운 데이터 구조 생성
                    new_data = {
                        **improved_data,
                        "id": f"{data.get('id', 'unknown')}_GIGACHAD",
                        "genre_detected": genre,
                        "gigachad_characters": character_info,
                        "character_mapping": character_map,
                        "conversion_info": {
                            "original_file": input_path,
                            "converted_characters": len(characters),
                            "detected_genre": genre,
                            "gigachad_version": "2.0",
                            "data_type": "novel"
                        }
                    }
                    
                    print(f"✅ 변환 완료: {input_path} -> {output_path}")
                    print(f"   🎭 장르: {genre}")
                    print(f"   📝 캐릭터 {len(characters)}개 변환: {', '.join(characters)} -> {', '.join(character_map.values()) if character_map else '없음'}")
            
            else:
                # 기존 VL_anime, VL_movie, VL_series 처리
                if 'text' not in data:
                    print(f"❌ 'text' 필드가 없는 파일: {input_path}")
                    return False
                
                # 장르 감지
                title = data.get('title', '')
                text_sample = ' '.join(data['text'][:5])  # 처음 5문장으로 장르 감지
                genre = self.name_generator.detect_genre(title, text_sample)
                
                # 캐릭터 추출 및 매핑 생성
                characters = self.extract_characters(data['text'])
                character_map, character_info = self.create_character_mapping(characters, genre)
                
                # 텍스트 개선
                improved_text = []
                for sentence in data['text']:
                    improved_sentence = self.text_improver.improve_sentence(sentence, character_map, genre)
                    improved_text.append(improved_sentence)
                
                # 새로운 데이터 구조 생성
                new_data = {
                    **data,
                    "id": f"{data.get('id', 'unknown')}_GIGACHAD",
                    "genre_detected": genre,
                    "characters": character_info,
                    "character_mapping": character_map,
                    "text": improved_text,
                    "conversion_info": {
                        "original_file": input_path,
                        "converted_characters": len(characters),
                        "detected_genre": genre,
                        "gigachad_version": "2.0"
                    }
                }
                
                print(f"✅ 변환 완료: {input_path} -> {output_path}")
                print(f"   🎭 장르: {genre}")
                print(f"   📝 캐릭터 {len(characters)}개 변환: {', '.join(characters)} -> {', '.join(character_map.values())}")
            
            # 출력 파일 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)
            
            return True
            
        except Exception as e:
            print(f"❌ 변환 실패: {input_path} - {str(e)}")
            return False
    
    def convert_directory(self, input_dir: str, output_dir: str) -> None:
        """디렉토리 전체 변환"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"❌ 입력 디렉토리가 존재하지 않습니다: {input_dir}")
            return
        
        json_files = list(input_path.rglob("*.json"))
        if not json_files:
            print(f"❌ JSON 파일을 찾을 수 없습니다: {input_dir}")
            return
        
        print(f"🚀 기가차드 v2.0 변환 시작! 총 {len(json_files)}개 파일")
        print(f"📁 입력: {input_dir}")
        print(f"📁 출력: {output_dir}")
        print("="*60)
        
        success_count = 0
        genre_stats = {"modern": 0, "fantasy": 0, "historical": 0, "scifi": 0}
        
        for json_file in json_files:
            # 상대 경로 계산
            relative_path = json_file.relative_to(input_path)
            output_file = output_path / relative_path
            
            # 파일명에 _GIGACHAD 추가
            output_file = output_file.with_name(
                output_file.stem + "_GIGACHAD" + output_file.suffix
            )
            
            if self.convert_json_file(str(json_file), str(output_file)):
                success_count += 1
        
        print("="*60)
        print(f"🎉 변환 완료! 성공: {success_count}/{len(json_files)}")
        if success_count < len(json_files):
            print(f"⚠️  실패: {len(json_files) - success_count}개 파일")


def main():
    parser = argparse.ArgumentParser(description="🔥 GIGACHAD Character Converter v2.0 🔥")
    parser.add_argument("input_dir", help="입력 디렉토리 경로")
    parser.add_argument("output_dir", help="출력 디렉토리 경로")
    parser.add_argument("--file", help="특정 파일만 변환 (선택사항)")
    parser.add_argument("--genre", choices=["modern", "fantasy", "historical", "scifi"], 
                       help="강제 장르 설정 (선택사항)")
    
    args = parser.parse_args()
    
    converter = GigaChadConverter()
    
    if args.file:
        # 단일 파일 변환
        output_file = os.path.join(args.output_dir, 
                                  os.path.basename(args.file).replace('.json', '_GIGACHAD.json'))
        converter.convert_json_file(args.file, output_file)
    else:
        # 디렉토리 전체 변환
        converter.convert_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main() 