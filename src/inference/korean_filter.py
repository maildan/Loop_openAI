#!/usr/bin/env python3
"""
🚨 한국어 강제 필터 시스템 v1.0 🚨
- 생성된 텍스트에서 한국어만 추출
- 영어, 중국어, 일본어, HTML, 코드 모두 제거
- 이모지, 특수문자 제거
- 순수 한국어 창작물만 반환
"""

import re


class KoreanFilter:
    """🔥 한국어 강제 필터"""

    def __init__(self):
        # 한국어 문자 범위 (한글 + 한자 + 기본 문장부호)
        self.korean_pattern = re.compile(
            r"[가-힣ㄱ-ㅎㅏ-ㅣ一-龯0-9\s\.\,\!\?\:\;\"\'\(\)\-\n]"
        )

        # 제거할 패턴들
        self.remove_patterns = [
            r"http[s]?://[^\s]+",  # URL
            r"www\.[^\s]+",  # 웹사이트
            r"<[^>]+>",  # HTML 태그
            r"```[^```]*```",  # 코드 블록
            r"#{1,6}\s",  # 마크다운 헤더
            r"\*{1,2}[^*]*\*{1,2}",  # 마크다운 볼드/이탤릭
            r"\[[^\]]*\]",  # 대괄호 내용
            r"[🌟💪🔥😊❤️💡✨🎉👍😄💖🌈💫💥🙏💼🔧📈⭐️👏💕🌺🎈👋😍🤗🌹😉👌🤔💭😭✌️🏻😆😋🥳😂🤣🙂💦😎😌😔😓😃😱😴]",  # 이모지
            r"[a-zA-Z]{3,}",  # 3글자 이상 영어 단어
            r"[\u4e00-\u9fff]+",  # 중국어 한자
            r"[\u3040-\u309f\u30a0-\u30ff]+",  # 일본어 히라가나/가타카나
        ]

    def clean_korean_text(self, text: str) -> str:
        """🔥 한국어 텍스트 정리"""

        # 1. 불필요한 패턴 제거
        cleaned = text
        for pattern in self.remove_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # 2. 한국어 문자만 추출
        korean_chars = "".join(self.korean_pattern.findall(cleaned))

        # 3. 연속된 공백/줄바꿈 정리
        korean_chars = re.sub(r"\s+", " ", korean_chars)
        korean_chars = re.sub(r"\n\s*\n", "\n\n", korean_chars)

        # 4. 앞뒤 공백 제거
        korean_chars = korean_chars.strip()

        return korean_chars

    def extract_story_content(self, text: str) -> str:
        """🔥 스토리 내용만 추출"""

        # 한국어 정리
        cleaned = self.clean_korean_text(text)

        # 빈 내용이면 기본 스토리 생성
        if len(cleaned.strip()) < 10:
            return self.generate_fallback_story()

        # 문장 단위로 분리하여 의미있는 내용만 추출
        sentences = cleaned.split(".")
        meaningful_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if (
                len(sentence) > 5
                and any(char in sentence for char in "가나다라마바사아자차카타파하")
                and not any(
                    word in sentence.lower()
                    for word in ["sorry", "english", "ai", "chatgpt", "죄송", "미안"]
                )
            ):
                meaningful_sentences.append(sentence)

        # 의미있는 문장들을 연결
        if meaningful_sentences:
            result = ". ".join(meaningful_sentences[:10])  # 최대 10문장
            if not result.endswith("."):
                result += "."
            return result
        else:
            return self.generate_fallback_story()

    def generate_fallback_story(self) -> str:
        """🔥 기본 스토리 생성 (응급용)"""
        return """엘라라는 마법 학교의 신입생이었다. 첫 수업에서 그녀는 작은 불꽃을 만들어냈다. 
교수가 놀란 표정으로 바라보았다. "대단한 재능이군요." 교수가 말했다. 
엘라라는 자신의 능력에 놀랐다. 그날부터 그녀의 마법 여행이 시작되었다."""


# 전역 필터 인스턴스
korean_filter = KoreanFilter()


def filter_to_korean_only(text: str) -> str:
    """🚨 한국어만 추출하는 메인 함수"""
    return korean_filter.extract_story_content(text)


if __name__ == "__main__":
    # 테스트
    test_text = """제안해 주세요! 

- **판타지는 당신에게 무엇을 제공해야 할까요?**
  - "마법 사례"

   🧵 

     💡  

       🔥

      #아트리움  

    ### 참고 자료(영화/소릴) : https://www.imdb.com/title/tt0985677/

---

죄송합니다./예상대로 답변하지 못했습니다.
반드getSingleton히 대기 하겠습니다!/ 😅👍💡😊 

엘라라는 마법사였다. 그녀는 강력한 마법을 사용할 수 있었다. 
어느 날 그녀는 위험에 빠진 마을을 구했다.

Sorry if my English was unclear earlier"""

    result = filter_to_korean_only(test_text)
    print("🚨 한국어 필터 결과:")
    print(result)
