#!/usr/bin/env python3
"""
Loop AI 한국어 맞춤법 검사 모듈
GitHub pragnakalp/spellcheck-using-dictionary-in-python 및 
GeeksforGeeks 가이드를 참고하여 구현

참고:
- https://github.com/pragnakalp/spellcheck-using-dictionary-in-python
- https://www.geeksforgeeks.org/python/spelling-checker-in-python/
"""

import json
import os
import logging
from typing import List, Dict, Tuple, Optional, Set
from fuzzywuzzy import fuzz, process
import re

logger = logging.getLogger(__name__)

class KoreanSpellChecker:
    """
    한국어 맞춤법 검사기
    NIA 한국어 사전을 기반으로 한 Fuzzy String Matching 사용
    """
    
    def __init__(self, dictionary_path: str = "dataset/words/spellcheck_dictionary.json"):
        """
        맞춤법 검사기 초기화
        
        Args:
            dictionary_path: 사전 파일 경로
        """
        self.dictionary_path = dictionary_path
        self.words: Set[str] = set()
        self.word_list: List[str] = []
        self.metadata: Dict = {}
        
        self._load_dictionary()
    
    def _load_dictionary(self) -> None:
        """사전 파일 로딩"""
        try:
            if not os.path.exists(self.dictionary_path):
                logger.error(f"❌ 사전 파일을 찾을 수 없습니다: {self.dictionary_path}")
                # 빈 사전으로 초기화
                self.words = set()
                self.word_list = []
                return
            
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get("metadata", {})
            self.word_list = data.get("words", [])
            self.words = set(self.word_list)
            
            logger.info(f"✅ 맞춤법 사전 로딩 완료: {len(self.words):,}개 단어")
            
        except Exception as e:
            logger.error(f"❌ 사전 로딩 실패: {e}")
            self.words = set()
            self.word_list = []
    
    def is_correct(self, word: str) -> bool:
        """
        단어가 올바른 맞춤법인지 확인
        
        Args:
            word: 검사할 단어
            
        Returns:
            bool: 올바른 맞춤법이면 True
        """
        if not word or not isinstance(word, str):
            return False
        
        # 정확한 매치 확인
        return word.strip() in self.words
    
    def get_suggestions(self, word: str, limit: int = 5, threshold: int = 60) -> List[Tuple[str, int]]:
        """
        틀린 단어에 대한 수정 제안
        
        Args:
            word: 검사할 단어
            limit: 최대 제안 개수
            threshold: 유사도 임계값 (0-100)
            
        Returns:
            List[Tuple[str, int]]: (제안단어, 유사도점수) 리스트
        """
        if not word or not isinstance(word, str):
            return []
        
        word = word.strip()
        
        # 이미 올바른 단어면 빈 리스트 반환
        if self.is_correct(word):
            return []
        
        try:
            # FuzzyWuzzy를 사용한 유사 단어 찾기
            matches = process.extract(
                word, 
                self.word_list, 
                scorer=fuzz.ratio,
                limit=limit * 2  # 더 많이 가져와서 필터링
            )
            
            # 임계값 이상인 것만 필터링
            suggestions = [
                (match[0], match[1]) 
                for match in matches 
                if match[1] >= threshold
            ]
            
            # 상위 limit개만 반환
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"❌ 제안 생성 중 오류: {e}")
            return []
    
    def correct_word(self, word: str, threshold: int = 80) -> str:
        """
        단어 자동 수정
        
        Args:
            word: 수정할 단어
            threshold: 자동 수정 임계값
            
        Returns:
            str: 수정된 단어 (수정 불가능하면 원본 반환)
        """
        if not word or not isinstance(word, str):
            return word
        
        word = word.strip()
        
        # 이미 올바른 단어면 그대로 반환
        if self.is_correct(word):
            return word
        
        suggestions = self.get_suggestions(word, limit=1, threshold=threshold)
        
        if suggestions:
            return suggestions[0][0]  # 가장 유사한 단어 반환
        
        return word  # 수정 불가능하면 원본 반환
    
    def check_text(self, text: str) -> Dict:
        """
        텍스트 전체 맞춤법 검사
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            Dict: 검사 결과
        """
        if not text or not isinstance(text, str):
            return {
                "original": text,
                "corrected": text,
                "errors": [],
                "suggestions": {},
                "stats": {"total_words": 0, "errors": 0, "accuracy": 100.0}
            }
        
        # 한글, 영문, 숫자만 포함된 단어 추출
        words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
        
        errors = []
        suggestions = {}
        corrected_text = text
        
        for word in words:
            if not self.is_correct(word):
                errors.append(word)
                word_suggestions = self.get_suggestions(word, limit=3)
                
                if word_suggestions:
                    suggestions[word] = word_suggestions
                    # 가장 유사한 단어로 자동 수정
                    best_match = word_suggestions[0][0]
                    corrected_text = corrected_text.replace(word, best_match, 1)
        
        # 통계 계산
        total_words = len(words)
        error_count = len(errors)
        accuracy = ((total_words - error_count) / total_words * 100) if total_words > 0 else 100.0
        
        return {
            "original": text,
            "corrected": corrected_text,
            "errors": errors,
            "suggestions": suggestions,
            "stats": {
                "total_words": total_words,
                "errors": error_count,
                "accuracy": round(accuracy, 1)
            }
        }
    
    def get_stats(self) -> Dict:
        """맞춤법 검사기 통계 정보"""
        return {
            "dictionary_size": len(self.words),
            "metadata": self.metadata,
            "status": "active" if self.words else "inactive"
        }

# 전역 인스턴스
_spellchecker_instance: Optional[KoreanSpellChecker] = None

def get_spellchecker() -> KoreanSpellChecker:
    """싱글톤 맞춤법 검사기 인스턴스 반환"""
    global _spellchecker_instance
    
    if _spellchecker_instance is None:
        _spellchecker_instance = KoreanSpellChecker()
    
    return _spellchecker_instance

def check_spelling(text: str) -> Dict:
    """
    편의 함수: 텍스트 맞춤법 검사
    
    Args:
        text: 검사할 텍스트
        
    Returns:
        Dict: 검사 결과
    """
    checker = get_spellchecker()
    return checker.check_text(text)

def suggest_corrections(word: str, limit: int = 5) -> List[Tuple[str, int]]:
    """
    편의 함수: 단어 수정 제안
    
    Args:
        word: 검사할 단어
        limit: 최대 제안 개수
        
    Returns:
        List[Tuple[str, int]]: (제안단어, 유사도점수) 리스트
    """
    checker = get_spellchecker()
    return checker.get_suggestions(word, limit)

def correct_word(word: str) -> str:
    """
    편의 함수: 단어 자동 수정
    
    Args:
        word: 수정할 단어
        
    Returns:
        str: 수정된 단어
    """
    checker = get_spellchecker()
    return checker.correct_word(word)

# 테스트 함수
def test_spellchecker():
    """맞춤법 검사기 테스트"""
    print("🔍 한국어 맞춤법 검사기 테스트")
    print("=" * 50)
    
    checker = get_spellchecker()
    print(f"📚 사전 크기: {len(checker.words):,}개 단어")
    
    # 테스트 케이스
    test_cases = [
        "안녕하세요",  # 정확한 단어
        "안뇽하세요",  # 틀린 단어
        "컴퓨터",      # 정확한 단어
        "컴퓨타",      # 틀린 단어
        "프로그래밍",  # 정확한 단어
        "프로그래밍이 재미있어요",  # 문장
        "컴퓨타 프로그래밍은 정말 재밌어요"  # 오타가 있는 문장
    ]
    
    for test_text in test_cases:
        print(f"\n🔤 테스트: '{test_text}'")
        
        if len(test_text.split()) == 1:  # 단어 테스트
            word = test_text
            is_correct = checker.is_correct(word)
            print(f"   올바른 맞춤법: {is_correct}")
            
            if not is_correct:
                suggestions = checker.get_suggestions(word)
                print(f"   제안: {suggestions}")
                corrected = checker.correct_word(word)
                print(f"   자동 수정: '{corrected}'")
        else:  # 문장 테스트
            result = checker.check_text(test_text)
            print(f"   수정된 문장: '{result['corrected']}'")
            print(f"   오타: {result['errors']}")
            print(f"   정확도: {result['stats']['accuracy']}%")

if __name__ == "__main__":
    test_spellchecker() 