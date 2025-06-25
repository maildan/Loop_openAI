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

import random
import json
from typing import List, Dict, Tuple
import argparse

class AdvancedFantasyNameGenerator:
    """진짜 판타지/이세계 이름 생성기"""
    
    def __init__(self):
        # 🌟 이세계 애니메이션 여주인공 이름들 (에밀리아, 카구야 스타일)
        self.isekai_female_protagonists = [
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
            "아리아", "루나", "셀레스티아", "오로라", "이사벨라", "빅토리아", "샬롯",
            "로제리아", "에스텔", "카밀라", "레오나", "디아나", "플로라", "실비아",
            
            # 마법소녀 스타일
            "사쿠라", "토모요", "메이링", "유키토", "케르베로스", "유에", "에리올",
            "미도리", "아카네", "시로", "쿠로", "아오", "키이로", "무라사키",
            
            # 하렘 이세계 히로인 이름들
            "아스나", "유키", "실리카", "리즈벳", "사치", "유이", "시논", "리파",
            "스구하", "키리토", "클라인", "아길", "엔드리", "레콘", "류우지"
        ]
        
        # 🗡️ 이세계 남주인공 이름들 (키리토, 림루 스타일)
        self.isekai_male_protagonists = [
            # 주인공급 이름들
            "키리토", "카즈토", "림루", "아인즈", "모몬가", "나츠키", "스바루", "카즈마",
            "아크바이트", "라이트", "아오바", "하루토", "소라", "시로", "테츠야", "유우야",
            
            # 용사/기사 스타일
            "아서", "랜슬롯", "갈라하드", "퍼시발", "가웨인", "트리스탄", "가레스", "베디비어",
            "지크프리드", "라그나르", "토르", "발더", "프레이", "오딘", "로키", "헤임달",
            
            # 마왕/다크로드 스타일
            "루시퍼", "벨제부브", "아스모데우스", "레비아탄", "벨페고르", "맘몬", "사탄",
            "아바돈", "바알", "몰록", "다곤", "베히모스", "리바이어던",
            
            # 현자/마법사 스타일
            "메를린", "간달프", "사루만", "라다가스트", "알랜드릴", "엘론드", "길갈라드",
            "아르케인", "매지카", "미스틱", "오라클", "세이지", "마스터", "그랜드마스터",
            
            # 일본 라노벨 주인공 이름들
            "하치만", "토베", "유키노", "유이", "하야토", "카와사키", "토츠카", "이로하",
            "히키가야", "유키노시타", "유이가하마", "토베", "하야마", "사이카",
            
            # 전생/환생 주인공들
            "루데우스", "에리스", "록시", "실피", "기슬레느", "파울", "제니스", "리리아",
            "알리스", "류지엔", "보레아스", "그레이라트", "라트레이야", "아스라"
        ]
        
        # 🏰 서양 판타지 이름 (LOTR, 해리포터 스타일)
        self.western_fantasy_names = {
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
                "아리엘", "카시엘", "라구엘", "라지엘", "하니엘", "카마엘"
            ],
            "male": [
                # 기사/전사 이름들
                "아라곤", "보로미르", "파라미르", "덴에소르", "이시르", "아나리온",
                "엘렌딜", "길갈라드", "엘론드", "레골라스", "김리", "간달프",
                
                # 마법사/현자 이름들
                "메를린", "덤블도어", "스네이프", "루핀", "시리우스", "제임스", "해리",
                "론", "네빌", "시무스", "딘", "올리버", "퍼시", "프레드", "조지",
                
                # 왕/황제 이름들
                "아서", "알렉산더", "아우구스투스", "막시밀리안", "레오나르드", "세바스찬",
                "아드리안", "발렌틴", "다미안", "루시안", "트리스탄", "퍼시발",
                
                # 대천사/신 이름들
                "가브리엘", "미카엘", "라파엘", "우리엘", "카시엘", "라구엘", "사리엘"
            ]
        }
        
        # 💫 조합용 음절 (진짜 이세계 느낌나는)
        self.isekai_syllables = {
            "prefix": [
                # 일본어 느낌
                "아", "카", "사", "타", "나", "하", "마", "야", "라", "와",
                "키", "시", "치", "니", "히", "미", "리", "유", "쿠", "스",
                "에", "케", "세", "테", "네", "헤", "메", "레", "웨", "츠",
                "오", "코", "소", "토", "노", "호", "모", "요", "로", "루",
                
                # 서양어 느낌
                "알", "벨", "셀", "델", "엘", "펠", "겔", "헬", "이", "젤",
                "아르", "베르", "세르", "데르", "에르", "페르", "게르", "헤르",
                "아리", "베리", "세리", "데리", "에리", "페리", "게리", "헤리",
                "아로", "베로", "세로", "데로", "에로", "페로", "게로", "헤로"
            ],
            "middle": [
                "미", "리", "니", "시", "치", "키", "지", "비", "피", "히",
                "마", "라", "나", "사", "타", "카", "가", "바", "파", "하",
                "메", "레", "네", "세", "테", "케", "게", "베", "페", "헤",
                "모", "로", "노", "소", "토", "코", "고", "보", "포", "호",
                "리아", "미아", "니아", "시아", "티아", "키아", "지아", "비아",
                "렐", "멜", "넬", "셀", "텔", "켈", "겔", "벨", "펠", "헬"
            ],
            "suffix": [
                # 여성형 어미
                "아", "에", "이", "오", "우", "야", "유", "요", "나", "네",
                "리아", "미아", "니아", "시아", "티아", "키아", "비아", "피아",
                "렐", "멜", "넬", "셀", "텔", "켈", "겔", "벨", "펠", "헬",
                "나", "네", "니", "노", "누", "라", "레", "리", "로", "루",
                
                # 남성형 어미  
                "스", "드", "트", "크", "그", "브", "프", "흐", "즈", "츠",
                "로", "루", "레", "리", "라", "토", "투", "테", "티", "타",
                "우스", "투스", "루스", "무스", "누스", "스트", "르트", "르드"
            ]
        }
        
        # 🎭 캐릭터 클래스별 이름 패턴
        self.class_name_patterns = {
            "마법사": {
                "female": ["미스틱", "아르카나", "셀레스티아", "루나리아", "아스트라", "에테리아"],
                "male": ["아르케인", "매지카", "메를린", "간달프", "미스터", "세이지"]
            },
            "기사": {
                "female": ["아르투리아", "잔다르크", "브륀힐드", "발키리", "템플러", "팔라딘"],
                "male": ["아서", "랜슬롯", "시그르드", "롤랑", "바하무트", "드래곤슬레이어"]
            },
            "도적": {
                "female": ["섀도우", "실프", "니야", "로그", "팬텀", "미스트"],
                "male": ["섀도", "스틸스", "팬텀", "레이븐", "실버", "나이트메어"]
            },
            "성직자": {
                "female": ["세라핌", "엔젤", "홀리", "디바인", "세인트", "프리스티스"],
                "male": ["프리스트", "클레릭", "오라클", "비숍", "가디언", "템플러"]
            },
            "용사": {
                "female": ["헤로인", "챔피언", "세이비어", "레스큐어", "가디언", "프로텍터"],
                "male": ["히어로", "챔피언", "세이비어", "구원자", "용사", "드래곤로드"]
            }
        }
        
        # 🌈 원소/속성별 이름
        self.elemental_names = {
            "fire": ["이그니스", "플람마", "블레이즈", "인페르노", "파이로", "볼케이노"],
            "water": ["아쿠아", "마리나", "오케아노스", "히드로", "글라시에스", "나이아드"],
            "earth": ["테라", "가이아", "크리스탈", "석영", "다이아몬드", "에메랄드"],
            "air": ["벤투스", "시엘", "스카이", "에어리얼", "실프", "스톰"],
            "light": ["룩스", "루미나", "솔라", "레디안트", "오로라", "셀레스"],
            "dark": ["테네브라", "셰이드", "노크턴", "이클립스", "님버스", "오브시디안"]
        }
    
    def generate_isekai_name(self, gender: str = "female", style: str = "anime") -> str:
        """이세계 애니메이션 스타일 이름 생성"""
        
        if style == "anime":
            if gender == "female":
                base_names = self.isekai_female_protagonists
            else:
                base_names = self.isekai_male_protagonists
                
            return random.choice(base_names)
        
        elif style == "composed":
            # 조합형 이름 생성 (에밀리아, 베아트리체 스타일)
            prefix = random.choice(self.isekai_syllables["prefix"])
            middle = random.choice(self.isekai_syllables["middle"])
            suffix = random.choice(self.isekai_syllables["suffix"])
            
            # 성별에 따른 어미 조정
            if gender == "female":
                if suffix.endswith("스") or suffix.endswith("드"):
                    suffix = random.choice(["아", "리아", "에", "네", "나"])
            else:
                if suffix.endswith("아") or suffix.endswith("리아"):
                    suffix = random.choice(["스", "드", "로", "루", "토"])
            
            return f"{prefix}{middle}{suffix}"
        
        elif style == "western":
            # 서양 판타지 스타일
            return random.choice(self.western_fantasy_names[gender])
        
        else:
            # 기본값: anime 스타일로 폴백
            if gender == "female":
                return random.choice(self.isekai_female_protagonists)
            else:
                return random.choice(self.isekai_male_protagonists)
    
    def generate_by_class(self, character_class: str, gender: str = "female") -> str:
        """클래스별 특화 이름 생성"""
        if character_class in self.class_name_patterns:
            base_name = random.choice(self.class_name_patterns[character_class][gender])
            
            # 조합으로 변형
            if random.random() < 0.3:  #     30% 확률로 조합형으로 변형
                syllable = random.choice(self.isekai_syllables["middle"])
                return f"{base_name[:2]}{syllable}{base_name[2:]}"
            
            return base_name
        else:
            return self.generate_isekai_name(gender, "anime")
    
    def generate_elemental_name(self, element: str, gender: str = "female") -> str:
        """원소/속성 기반 이름 생성"""
        if element in self.elemental_names:
            base_name = random.choice(self.elemental_names[element])
            
            # 성별에 따른 어미 추가
            if gender == "female":
                if random.random() < 0.5:
                    base_name += random.choice(["리아", "나", "네", "아", "에"])
            else:
                if random.random() < 0.5:
                    base_name += random.choice(["스", "드", "로", "토", "무스"])
            
            return base_name
        else:
            return self.generate_isekai_name(gender, "anime")
    
    def generate_noble_name(self, gender: str = "female") -> Tuple[str, str]:
        """귀족 이름 생성 (이름 + 성)"""
        
        # 귀족 성씨
        noble_surnames = [
            "그레이라트", "라트레이야", "보레아스", "아스라", "드라고니아",
            "펜드래곤", "플란타지넷", "하프스부르크", "로마노프", "메디치",
            "몬테크리스토", "다르타냥", "발루아", "부르봉", "합스부르크",
            "폰 아인즈베른", "토오사카", "엔즈워스", "마토", "에미야"
        ]
        
        first_name = self.generate_isekai_name(gender, "western")
        surname = random.choice(noble_surnames)
        
        return first_name, surname
    
    def generate_multiple_names(self, count: int = 10, gender: str = "female", 
                              style: str = "mixed") -> List[Dict]:
        """여러 이름을 한번에 생성"""
        
        names = []
        styles = ["anime", "composed", "western"] if style == "mixed" else [style]
        
        for i in range(count):
            current_style = random.choice(styles)
            name = self.generate_isekai_name(gender, current_style)
            
            # 추가 정보 생성
            character_info = {
                "name": name,
                "gender": gender,
                "style": current_style,
                "class": random.choice(list(self.class_name_patterns.keys())),
                "element": random.choice(list(self.elemental_names.keys())),
                "personality": random.choice([
                    "용감한", "지혜로운", "신비로운", "우아한", "강인한", "온화한",
                    "냉정한", "열정적인", "순수한", "교활한", "매력적인", "카리스마 있는"
                ])
            }
            
            names.append(character_info)
        
        return names
    
    def batch_generate_by_categories(self, count_per_category: int = 5) -> Dict:
        """카테고리별로 배치 생성"""
        
        result = {
            "isekai_heroines": [],
            "isekai_heroes": [],
            "fantasy_princesses": [],
            "fantasy_knights": [],
            "elemental_mages": [],
            "noble_families": []
        }
        
        # 이세계 히로인들 (에밀리아, 렘 스타일)
        for _ in range(count_per_category):
            name = self.generate_isekai_name("female", "anime")
            result["isekai_heroines"].append({
                "name": name,
                "type": "이세계 히로인",
                "origin": "애니메이션 스타일"
            })
        
        # 이세계 주인공들 (키리토, 림루 스타일)
        for _ in range(count_per_category):
            name = self.generate_isekai_name("male", "anime")
            result["isekai_heroes"].append({
                "name": name,
                "type": "이세계 주인공",
                "origin": "라이트노벨 스타일"
            })
        
        # 판타지 공주들
        for _ in range(count_per_category):
            first_name, surname = self.generate_noble_name("female")
            result["fantasy_princesses"].append({
                "name": f"{first_name} {surname}",
                "type": "판타지 공주",
                "origin": "서양 판타지"
            })
        
        # 판타지 기사들
        for _ in range(count_per_category):
            name = self.generate_by_class("기사", "male")
            result["fantasy_knights"].append({
                "name": name,
                "type": "판타지 기사",
                "origin": "기사 클래스"
            })
        
        # 원소 마법사들
        for _ in range(count_per_category):
            element = random.choice(list(self.elemental_names.keys()))
            name = self.generate_elemental_name(element, 
                                               random.choice(["male", "female"]))
            result["elemental_mages"].append({
                "name": name,
                "type": f"{element} 마법사",
                "origin": "원소 마법"
            })
        
        # 귀족 가문들
        for _ in range(count_per_category):
            male_name, surname = self.generate_noble_name("male")
            female_name, _ = self.generate_noble_name("female")
            result["noble_families"].append({
                "family_name": surname,
                "lord": f"{male_name} {surname}",
                "lady": f"{female_name} {surname}",
                "type": "귀족 가문"
            })
        
        return result


def main():
    parser = argparse.ArgumentParser(description="🔥 Fantasy & Isekai Name Generator v3.0 🔥")
    parser.add_argument("--count", "-c", type=int, default=10, help="생성할 이름 개수")
    parser.add_argument("--gender", "-g", choices=["male", "female", "mixed"], 
                       default="female", help="성별 선택")
    parser.add_argument("--style", "-s", choices=["anime", "composed", "western", "mixed"],
                       default="mixed", help="이름 스타일")
    parser.add_argument("--class", dest="char_class", help="캐릭터 클래스")
    parser.add_argument("--element", "-e", help="원소/속성")
    parser.add_argument("--batch", "-b", action="store_true", help="카테고리별 배치 생성")
    parser.add_argument("--output", "-o", help="결과를 JSON 파일로 저장")
    
    args = parser.parse_args()
    
    generator = AdvancedFantasyNameGenerator()
    
    if args.batch:
        # 배치 생성
        print("🌟 카테고리별 배치 생성 시작!")
        result = generator.batch_generate_by_categories(args.count)
        
        for category, names in result.items():
            print(f"\n📖 {category.upper()}:")
            for item in names:
                if "family_name" in item:
                    print(f"  🏰 {item['family_name']} 가문")
                    print(f"     👑 영주: {item['lord']}")
                    print(f"     👸 영부인: {item['lady']}")
                else:
                    print(f"  ✨ {item['name']} ({item['type']})")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 {args.output}에 저장되었습니다!")
    
    else:
        # 일반 생성
        print(f"🔥 Fantasy & Isekai Name Generator v3.0 🔥")
        print(f"📝 {args.count}개의 {args.gender} {args.style} 이름 생성!")
        print("="*50)
        
        if args.char_class:
            # 클래스별 생성
            for i in range(args.count):
                gender = args.gender if args.gender != "mixed" else random.choice(["male", "female"])
                name = generator.generate_by_class(args.char_class, gender)
                print(f"{i+1:2d}. ⚔️  {name} ({gender} {args.char_class})")
        
        elif args.element:
            # 원소별 생성
            for i in range(args.count):
                gender = args.gender if args.gender != "mixed" else random.choice(["male", "female"])
                name = generator.generate_elemental_name(args.element, gender)
                print(f"{i+1:2d}. 🔮 {name} ({gender} {args.element} 마법사)")
        
        else:
            # 일반 생성
            for i in range(args.count):
                gender = args.gender if args.gender != "mixed" else random.choice(["male", "female"])
                style = args.style if args.style != "mixed" else random.choice(["anime", "composed", "western"])
                name = generator.generate_isekai_name(gender, style)
                print(f"{i+1:2d}. ✨ {name} ({gender}, {style})")
    
    print("\n🎉 생성 완료!")
    
    # 샘플 추천
    print("\n💡 추천 명령어:")
    print("  python fantasy_names.py --batch -c 3  # 카테고리별 3개씩")
    print("  python fantasy_names.py -c 20 -g female -s anime  # 애니 히로인 20명")
    print("  python fantasy_names.py --class 마법사 -c 10  # 마법사 10명")
    print("  python fantasy_names.py --element fire -c 5  # 화염 마법사 5명")


if __name__ == "__main__":
    main()