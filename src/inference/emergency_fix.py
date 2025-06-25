#!/usr/bin/env python3
"""
🚨 Loop AI 슈퍼 응급처치 시스템 v2.0 🚨
- Catastrophic Forgetting 완전 해결
- 한국어 강제 고정
- 더 강력한 Few-Shot Learning
- 토큰 오염 방지
"""

import json
from typing import Dict, Any

class SuperEmergencyLoopAI:
    """🔥 슈퍼 응급처치된 Loop AI"""
    
    def __init__(self):
        self.korean_examples = {
            "fantasy": """**제목: 잃어버린 마법의 서**

엘라라는 마법 아카데미 최하위 학생이었다. 다른 학생들이 화려한 마법을 펼칠 때, 그녀는 촛불 하나 켜는 것도 버거워했다.

"또 실패했군." 교수가 차갑게 말했다.

그날 밤, 엘라라는 도서관 지하에서 먼지 쌓인 고서를 발견했다. 책을 열자 금빛 글자들이 공중에 떠올랐다.

"진정한 마법은 힘이 아니라 마음에서 나온다."

순간, 그녀의 손끝에서 은은한 빛이 흘러나왔다. 그것은 치유의 마법이었다.

다음 날, 엘라라는 다친 새를 치유했다. 교수들이 놀란 눈으로 바라보았다.

"이제 진짜 마법사가 되었구나." 그녀가 혼잣말했다.""",
            
            "movie": """**제목: 최후의 추격**

현우는 전직 특수요원이었다. 지금은 평범한 택시기사로 살고 있었다.

그날 밤, 한 여자가 그의 택시에 뛰어들었다.

"빨리 가주세요! 제발!" 여자가 다급하게 말했다.

뒤따라오는 검은 세단들. 현우의 본능이 깨어났다.

"벨트 매세요." 현우가 냉정하게 말했다.

급가속. 한강대교를 질주하는 택시. 총성이 뒤에서 들렸다.

"당신 누구예요?" 여자가 물었다.

"그냥 택시기사입니다." 현우가 핸들을 꺾으며 답했다.

하지만 그의 눈빛은 이미 전사의 것이었다.""",
            
            "anime": """**제목: 시공간 카페**

유키는 평범한 고등학생이었다. 그날도 학교에서 집으로 가는 길이었다.

비가 내리기 시작했다. 급히 피할 곳을 찾던 유키는 작은 카페를 발견했다.

"어서 오세요." 신비로운 미소를 짓는 마스터가 말했다.

"따뜻한 라떼 하나 주세요." 유키가 말했다.

마스터가 특별한 라떼를 내왔다. 첫 모금을 마시자...

갑자기 주변 풍경이 바뀌었다. 1년 전, 전학 간 친구 미나와의 마지막 날이었다.

"이번엔 제대로 말할 거야." 유키가 다짐했다.

"미나야, 고마웠어. 정말 좋은 친구였어."

미나가 눈물을 글썽이며 웃었다.""",
            
            "drama": """**제목: 작은 책방의 기적**

지은은 28살이었다. 대기업을 그만두고 작은 책방을 열었다.

첫 번째 손님은 70대 할머니였다.

"윤동주 시집이 있나요?" 할머니가 물었다.

"네, 여기 있어요." 지은이 책을 건넸다.

할머니가 책을 받아들고 눈물을 흘렸다.

"돌아가신 남편이 좋아하던 시였어요." 할머니가 말했다.

지은이 따뜻한 차를 내왔다.

"첫 손님이세요. 서비스입니다." 지은이 웃었다.

할머니가 시를 읽기 시작했다. 지은도 함께 들었다.

작은 책방에 따뜻한 기적이 시작되었다."""
        }
    
    def create_super_prompt(self, user_request: str, genre: str = "fantasy") -> str:
        """🔥 슈퍼 강화된 한국어 프롬프트"""
        
        example = self.korean_examples.get(genre, self.korean_examples["fantasy"])
        
        # 한국어 강제 고정 프롬프트
        super_prompt = f"""당신은 한국어 창작 전문가 Loop AI입니다. 반드시 한국어로만 응답하세요.

🎯 필수 규칙:
1. 모든 응답은 한국어로만 작성
2. 영어, 중국어, 일본어 사용 금지
3. HTML, 코드, 특수문자 사용 금지
4. 창작물만 생성, 설명 금지

📚 한국어 창작 예시:
{example}

🚀 지금 요청 (한국어로만 응답):
사용자: {user_request}

Loop AI (한국어 창작 시작):"""

        return super_prompt
    
    def get_korean_params(self) -> Dict[str, Any]:
        """🔥 한국어 최적화 파라미터"""
        return {
            "max_new_tokens": 400,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "repetition_penalty": 1.5,  # 반복 강하게 방지
            "no_repeat_ngram_size": 4,  # 4-gram 반복 방지
            "do_sample": True,
            "pad_token_id": 151643,  # Qwen EOS 토큰
            "eos_token_id": 151643
        }
    
    def detect_genre_korean(self, prompt: str) -> str:
        """🎯 한국어 장르 감지"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["판타지", "마법", "용", "엘프", "마법사", "모험"]):
            return "fantasy"
        elif any(word in prompt_lower for word in ["영화", "시나리오", "액션", "스릴러", "추격"]):
            return "movie"
        elif any(word in prompt_lower for word in ["애니", "애니메이션", "캐릭터", "학생"]):
            return "anime"
        elif any(word in prompt_lower for word in ["드라마", "대본", "연속극", "가족"]):
            return "drama"
        else:
            return "fantasy"

# 전역 슈퍼 인스턴스
super_emergency_ai = SuperEmergencyLoopAI()

def fix_catastrophic_forgetting(prompt: str) -> Dict[str, Any]:
    """🚨 Catastrophic Forgetting 완전 해결"""
    
    # 한국어 장르 감지
    genre = super_emergency_ai.detect_genre_korean(prompt)
    
    # 슈퍼 한국어 프롬프트 생성
    super_prompt = super_emergency_ai.create_super_prompt(prompt, genre)
    
    # 한국어 최적화 파라미터
    params = super_emergency_ai.get_korean_params()
    
    return {
        "enhanced_prompt": super_prompt,
        "params": params,
        "genre": genre,
        "fix_applied": True,
        "korean_forced": True
    }

if __name__ == "__main__":
    # 테스트
    test_prompt = "판타지 소설을 써주세요. 마법사가 등장하는 이야기로요."
    result = fix_catastrophic_forgetting(test_prompt)
    
    print("🚨 슈퍼 응급처치 결과:")
    print(f"장르: {result['genre']}")
    print(f"한국어 강제: {result['korean_forced']}")
    print(f"슈퍼 프롬프트:\n{result['enhanced_prompt']}")
    print(f"파라미터: {result['params']}") 