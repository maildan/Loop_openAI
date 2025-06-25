#!/usr/bin/env python3
"""
NIA 한국어 사전 변환기
NIADic.xlsx를 JSON 형태로 변환하고 맞춤법 검사용 최적화된 사전 생성
"""

import json
import os
import re
from typing import Dict, List, Set, Any, Optional

import pandas as pd
from pandas import DataFrame, Series

def load_nia_dictionary(file_path: str) -> Optional[DataFrame]:
    """NIA 사전 Excel 파일 로딩"""
    try:
        print(f"📖 NIA 사전 로딩 중: {file_path}")
        
        # Excel 파일 읽기 (첫 번째 시트)
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"✅ 로딩 완료: {len(df):,}개 행")
        
        # 컬럼명 확인
        print(f"📋 컬럼: {list(df.columns)}")
        return df
        
    except Exception as e:
        print(f"❌ 파일 로딩 실패: {e}")
        return None

def clean_word(word: Any) -> Optional[str]:
    """단어 정리 및 검증"""
    if pd.isna(word):
        return None
    
    # 문자열로 변환
    word_str = str(word).strip()
    
    if not word_str:
        return None
    
    # 한글, 영문, 숫자만 허용 (특수문자 제거)
    cleaned = re.sub(r'[^\w가-힣]', '', word_str)
    
    # 최소 길이 확인
    if len(cleaned) < 2:
        return None
    
    return cleaned

def process_nia_data(df: DataFrame) -> Dict[str, Any]:
    """NIA 데이터 처리 및 분석"""
    print("🔍 데이터 분석 중...")
    
    # 컬럼명 매핑 (실제 컬럼명에 맞게 조정)
    word_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['어휘', '단어', 'word', '표제어', '어근']):
            word_columns.append(col)
    
    print(f"📝 식별된 단어 컬럼: {word_columns}")
    
    # 모든 단어 수집
    all_words: Set[str] = set()
    word_stats: Dict[str, int] = {}
    
    for col in word_columns:
        if col in df.columns:
            print(f"📊 {col} 컬럼 처리 중...")
            
            # 각 컬럼의 고유값 개수
            try:
                unique_count = int(df[col].nunique())
                word_stats[col] = unique_count
            except (TypeError, ValueError):
                word_stats[col] = 0
            print(f"   - 고유값: {unique_count:,}개")
            
            # 단어 정리 및 추가
            series_data = df[col].dropna()
            for word in series_data:
                cleaned = clean_word(word)
                if cleaned:
                    all_words.add(cleaned)
    
    print(f"✅ 총 수집된 단어: {len(all_words):,}개")
    
    return {
        "words": sorted(list(all_words)),
        "statistics": {
            "total_words": len(all_words),
            "column_stats": word_stats,
            "original_rows": len(df)
        }
    }

def create_optimized_spellcheck_dict(words: List[str], max_words: int = 50000) -> Dict[str, Any]:
    """맞춤법 검사용 최적화된 사전 생성"""
    print(f"⚡ 맞춤법 검사용 사전 최적화 중... (최대 {max_words:,}개)")
    
    # 단어 길이와 사용 빈도를 고려한 점수 계산
    word_scores = []
    
    for word in words:
        score = 0
        
        # 길이 점수 (2-10자가 최적)
        if 2 <= len(word) <= 10:
            score += 10
        elif len(word) > 10:
            score -= 2
        
        # 한글 단어 우선
        if re.match(r'^[가-힣]+$', word):
            score += 5
        
        # 일반적인 어미/접사 제외
        common_endings = ['하다', '되다', '이다', '적', '성', '화']
        if not any(word.endswith(ending) for ending in common_endings):
            score += 3
        
        word_scores.append((word, score))
    
    # 점수 순으로 정렬
    word_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 단어 선택
    selected_words = [word for word, score in word_scores[:max_words]]
    
    print(f"✅ 최적화 완료: {len(selected_words):,}개 단어 선택")
    
    return {
        "words": selected_words,
        "total_count": len(selected_words),
        "optimization_info": {
            "original_count": len(words),
            "selected_count": len(selected_words),
            "reduction_ratio": f"{(1 - len(selected_words)/len(words))*100:.1f}%"
        }
    }

def save_dictionaries(data: Dict[str, Any], output_dir: str = "dataset/words"):
    """사전 파일들 저장"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 전체 사전 저장
    full_dict_path = os.path.join(output_dir, "nia_dictionary.json")
    print(f"💾 전체 사전 저장 중: {full_dict_path}")
    
    full_dict = {
        "metadata": {
            "source": "NIA 한국어 사전",
            "created_at": pd.Timestamp.now().isoformat(),
            "total_words": len(data["words"]),
            "statistics": data["statistics"]
        },
        "words": data["words"]
    }
    
    with open(full_dict_path, 'w', encoding='utf-8') as f:
        json.dump(full_dict, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 전체 사전 저장 완료: {os.path.getsize(full_dict_path) / 1024 / 1024:.1f}MB")
    
    # 최적화된 맞춤법 검사용 사전 생성
    optimized_data = create_optimized_spellcheck_dict(data["words"])
    
    spell_dict_path = os.path.join(output_dir, "spellcheck_dictionary.json")
    print(f"💾 맞춤법 사전 저장 중: {spell_dict_path}")
    
    spell_dict = {
        "metadata": {
            "source": "NIA 한국어 사전 (맞춤법 검사 최적화)",
            "created_at": pd.Timestamp.now().isoformat(),
            "optimization_info": optimized_data["optimization_info"]
        },
        "words": optimized_data["words"]
    }
    
    with open(spell_dict_path, 'w', encoding='utf-8') as f:
        json.dump(spell_dict, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 맞춤법 사전 저장 완료: {os.path.getsize(spell_dict_path) / 1024 / 1024:.1f}MB")
    
    return full_dict_path, spell_dict_path

def main():
    """메인 실행 함수"""
    print("🚀 NIA 한국어 사전 변환 시작!")
    
    # 파일 경로
    input_file = "dataset/words/NIADic.xlsx"
    
    if not os.path.exists(input_file):
        print(f"❌ 파일이 존재하지 않습니다: {input_file}")
        return
    
    # 1. 사전 로딩
    df = load_nia_dictionary(input_file)
    if df is None:
        return
    
    # 2. 데이터 처리
    processed_data = process_nia_data(df)
    
    # 3. 사전 파일 저장
    full_path, spell_path = save_dictionaries(processed_data)
    
    print("\n" + "="*50)
    print("🎉 변환 완료!")
    print(f"📚 전체 사전: {full_path}")
    print(f"🔍 맞춤법 사전: {spell_path}")
    print(f"📊 총 단어 수: {processed_data['statistics']['total_words']:,}개")
    print("="*50)

if __name__ == "__main__":
    main() 