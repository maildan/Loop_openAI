# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportExplicitAny=false
"""
문체 분석 유틸리티
- soynlp를 이용한 키워드 추출
- 기본 텍스트 통계 계산
"""
import logging
from soynlp.noun import LRNounExtractor_v2  # type: ignore[reportMissingTypeStubs]
from soynlp.tokenizer import LTokenizer  # type: ignore[reportMissingTypeStubs]
from typing import cast

logger = logging.getLogger(__name__)

class StyleAnalyzer:
    """텍스트의 스타일과 구조를 분석하는 클래스"""
    noun_extractor: LRNounExtractor_v2 | None
    tokenizer: LTokenizer | None

    def __init__(self):
        self.noun_extractor = None
        self.tokenizer = None
        # 모델 훈련에 시간이 걸리므로, 실제 사용 시에는 미리 훈련된 모델을 로드하는 것이 좋습니다.
        # 지금은 요청 시마다 임시로 훈련합니다.
        
    def _train_models(self, texts: list[str]):
        """주어진 텍스트로 명사 추출기 및 토크나이저 훈련"""
        if not texts:
            return
            
        # 명사 추출기 훈련
        self.noun_extractor = LRNounExtractor_v2(verbose=False)
        self.noun_extractor.train(texts)  # type: ignore[attr-defined]
        
        # 토크나이저 훈련
        if self.noun_extractor:
            nouns: dict[str, object] = cast(dict[str, object], self.noun_extractor.train_extract(texts))  # type: ignore[attr-defined]
            self.tokenizer = LTokenizer(scores=nouns)  # type: ignore

    def get_basic_stats(self, text: str) -> dict[str, float | int]:
        """텍스트의 기본적인 통계 정보를 반환"""
        if not text:
            return {"sentences": 0, "words": 0, "avg_sentence_length": 0}

        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        num_sentences = len(sentences)
        num_words = len(words)
        avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0

        return {
            "sentences": num_sentences,
            "words": num_words,
            "avg_sentence_length": round(avg_sentence_length, 2),
        }

    def extract_keywords(self, text: str, min_count: int = 2) -> list[str]:
        """
        텍스트에서 핵심 명사(키워드)를 추출.
        간단한 구현을 위해, 매번 텍스트 자체로 모델을 훈련시킵니다.
        """
        if not text:
            return []
        
        try:
            self._train_models([text])
            if not self.noun_extractor:
                return []
            nouns: dict[str, object] = cast(dict[str, object], self.noun_extractor.train_extract([text]))  # type: ignore[attr-defined]
            # min_count 이상 출현한 명사만 키워드로 간주
            keywords = [noun for noun in nouns.keys() if text.count(noun) >= min_count]
            return keywords
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {e}")
            return []

# 테스트용
if __name__ == "__main__":
    analyzer = StyleAnalyzer()
    sample_text = "이것은 문체 분석기를 테스트하기 위한 샘플 텍스트입니다. 이 텍스트는 여러 개의 문장으로 구성되어 있습니다. 각 문장은 분석의 대상이 됩니다. 키워드 추출이 잘 되는지 확인해봅시다. 키워드는 중요한 단어입니다."
    
    stats = analyzer.get_basic_stats(sample_text)
    print("기본 통계:", stats)
    
    keywords = analyzer.extract_keywords(sample_text)
    print("추출된 키워드:", keywords) 