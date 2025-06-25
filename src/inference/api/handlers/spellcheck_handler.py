"""
Loop AI 맞춤법 검사 핸들러
서버의 맞춤법 검사 관련 로직을 모듈화
"""

import logging
from typing import Dict, List, Tuple
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.utils.spellcheck import get_spellchecker, check_spelling, suggest_corrections, correct_word

logger = logging.getLogger(__name__)

class SpellCheckHandler:
    """맞춤법 검사 핸들러"""
    
    def __init__(self):
        """맞춤법 검사 핸들러 초기화"""
        self.spellchecker = get_spellchecker()
        logger.info("✅ 맞춤법 검사 핸들러 초기화 완료")
    
    def check_text(self, text: str) -> Dict:
        """
        텍스트 맞춤법 검사
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            Dict: 맞춤법 검사 결과
        """
        try:
            result = check_spelling(text)
            
            # 추가 정보 포함
            result["handler"] = "SpellCheckHandler"
            result["dictionary_size"] = len(self.spellchecker.words)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 맞춤법 검사 중 오류: {e}")
            return {
                "original": text,
                "corrected": text,
                "errors": [],
                "suggestions": {},
                "stats": {"total_words": 0, "errors": 0, "accuracy": 100.0},
                "error": str(e)
            }
    
    def get_word_suggestions(self, word: str, limit: int = 5) -> List[Tuple[str, int]]:
        """
        단어 수정 제안
        
        Args:
            word: 검사할 단어
            limit: 최대 제안 개수
            
        Returns:
            List[Tuple[str, int]]: (제안단어, 유사도점수) 리스트
        """
        try:
            return suggest_corrections(word, limit)
        except Exception as e:
            logger.error(f"❌ 단어 제안 생성 중 오류: {e}")
            return []
    
    def correct_single_word(self, word: str) -> str:
        """
        단어 자동 수정
        
        Args:
            word: 수정할 단어
            
        Returns:
            str: 수정된 단어
        """
        try:
            return correct_word(word)
        except Exception as e:
            logger.error(f"❌ 단어 수정 중 오류: {e}")
            return word
    
    def is_word_correct(self, word: str) -> bool:
        """
        단어가 올바른 맞춤법인지 확인
        
        Args:
            word: 검사할 단어
            
        Returns:
            bool: 올바른 맞춤법이면 True
        """
        try:
            return self.spellchecker.is_correct(word)
        except Exception as e:
            logger.error(f"❌ 단어 검사 중 오류: {e}")
            return True  # 오류 시 올바른 것으로 가정
    
    def get_statistics(self) -> Dict:
        """맞춤법 검사기 통계 정보"""
        try:
            return self.spellchecker.get_stats()
        except Exception as e:
            logger.error(f"❌ 통계 정보 조회 중 오류: {e}")
            return {
                "dictionary_size": 0,
                "metadata": {},
                "status": "error",
                "error": str(e)
            }
    
    def batch_check(self, texts: List[str]) -> List[Dict]:
        """
        여러 텍스트 일괄 맞춤법 검사
        
        Args:
            texts: 검사할 텍스트 리스트
            
        Returns:
            List[Dict]: 각 텍스트의 검사 결과 리스트
        """
        results = []
        
        for text in texts:
            result = self.check_text(text)
            results.append(result)
        
        return results
    
    def create_spellcheck_response(self, text: str, auto_correct: bool = True) -> Dict:
        """
        맞춤법 검사 응답 생성 (API 응답용)
        
        Args:
            text: 검사할 텍스트
            auto_correct: 자동 수정 여부
            
        Returns:
            Dict: API 응답 형태의 결과
        """
        try:
            # 기본 맞춤법 검사
            check_result = self.check_text(text)
            
            # 추가 정보 생성
            response = {
                "success": True,
                "original_text": text,
                "corrected_text": check_result["corrected"] if auto_correct else text,
                "errors_found": len(check_result["errors"]),
                "error_words": check_result["errors"],
                "suggestions": check_result["suggestions"],
                "accuracy": check_result["stats"]["accuracy"],
                "total_words": check_result["stats"]["total_words"],
                "auto_corrected": auto_correct,
                "dictionary_info": {
                    "size": len(self.spellchecker.words),
                    "source": self.spellchecker.metadata.get("source", "NIA 한국어 사전")
                }
            }
            
            # 권장사항 추가
            if check_result["errors"]:
                response["recommendations"] = []
                for error_word in check_result["errors"][:3]:  # 상위 3개만
                    suggestions = self.get_word_suggestions(error_word, 3)
                    if suggestions:
                        response["recommendations"].append({
                            "word": error_word,
                            "suggestions": [{"word": s[0], "confidence": s[1]} for s in suggestions]
                        })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 맞춤법 검사 응답 생성 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
                "corrected_text": text,
                "errors_found": 0
            } 