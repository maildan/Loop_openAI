#!/usr/bin/env python3
"""
Qwen2.5-0.5B Model Download Script
=================================

기가차드 모드로 최신 Qwen2.5-0.5B 모델을 다운로드한다.
Apple Silicon MPS 최적화를 고려한 모델 다운로드 및 검증.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, List
import argparse

try:
    from huggingface_hub import snapshot_download, hf_hub_download
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    import psutil
except ImportError as e:
    print(f"❌ 필수 라이브러리 누락: {e}")
    print("💡 설치 명령어: pip install transformers torch huggingface_hub psutil")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QwenModelDownloader:
    """Qwen2.5 모델 다운로더 - 기가차드 버전"""
    
    def __init__(self, cache_dir: str = "./models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 지원 모델 목록 (성능 순서)
        self.supported_models = {
            "qwen2.5-0.5b": "Qwen/Qwen2.5-0.5B",
            "qwen2.5-0.5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct", 
            "qwen2-0.5b": "Qwen/Qwen2-0.5B",
            "qwen2-0.5b-instruct": "Qwen/Qwen2-0.5B-Instruct"
        }
        
        # Apple Silicon 최적화 설정
        self.device_info = self._detect_device()
        
    def _detect_device(self) -> dict:
        """디바이스 정보 감지"""
        info = {
            "device": "cpu",
            "device_name": "CPU",
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "mps_available": False
        }
        
        if torch.cuda.is_available():
            info["device"] = "cuda"
            info["device_name"] = torch.cuda.get_device_name(0)
            info["memory_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            info["device"] = "mps"
            info["device_name"] = "Apple Silicon MPS"
            info["mps_available"] = True
            
        return info
    
    def download_model(self, model_key: str, force_download: bool = False) -> str:
        """모델 다운로드"""
        if model_key not in self.supported_models:
            raise ValueError(f"지원하지 않는 모델: {model_key}")
            
        model_id = self.supported_models[model_key]
        local_dir = self.cache_dir / model_key
        
        logger.info(f"🚀 모델 다운로드 시작: {model_id}")
        logger.info(f"📁 저장 경로: {local_dir}")
        logger.info(f"💻 디바이스: {self.device_info['device_name']}")
        
        if local_dir.exists() and not force_download:
            logger.info(f"✅ 모델이 이미 존재합니다: {local_dir}")
            return str(local_dir)
        
        try:
            start_time = time.time()
            
            # 병렬 다운로드로 속도 최적화
            snapshot_download(
                repo_id=model_id,
                local_dir=str(local_dir),
                cache_dir=str(self.cache_dir / "hub"),
                resume_download=True,
                max_workers=8,  # 병렬 다운로드
                local_files_only=False
            )
            
            download_time = time.time() - start_time
            logger.info(f"✅ 다운로드 완료! 소요시간: {download_time:.2f}초")
            
            return str(local_dir)
            
        except Exception as e:
            logger.error(f"❌ 다운로드 실패: {e}")
            raise
    
    def verify_model(self, model_path: str) -> bool:
        """모델 검증"""
        logger.info(f"🔍 모델 검증 중: {model_path}")
        
        try:
            # 토크나이저 로드 테스트
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            logger.info(f"✅ 토크나이저 로드 성공 - 어휘 크기: {len(tokenizer)}")
            
            # 모델 로드 테스트 (헤더만)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device_info["device"] == "cuda" else torch.float32,
                device_map=None,  # 메모리 절약을 위해 로드하지 않음
                low_cpu_mem_usage=True
            )
            
            # 기본 정보 출력
            num_params = sum(p.numel() for p in model.parameters())
            logger.info(f"✅ 모델 로드 성공 - 파라미터 수: {num_params:,}")
            
            # 간단한 추론 테스트
            if self.device_info["mps_available"]:
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")
            else:
                device = torch.device("cpu")
                
            model = model.to(device)
            
            # 한국어 테스트
            test_text = "안녕하세요, 저는"
            inputs = tokenizer(test_text, return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=10,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"✅ 추론 테스트 성공: '{result}'")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 모델 검증 실패: {e}")
            return False
    
    def get_model_info(self, model_path: str) -> dict:
        """모델 정보 수집"""
        info = {
            "path": model_path,
            "size_gb": 0,
            "files": [],
            "config": {}
        }
        
        model_dir = Path(model_path)
        if not model_dir.exists():
            return info
            
        # 디렉토리 크기 계산
        total_size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
        info["size_gb"] = total_size / (1024**3)
        
        # 파일 목록
        info["files"] = [f.name for f in model_dir.iterdir() if f.is_file()]
        
        # 설정 파일 읽기
        config_file = model_dir / "config.json"
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                info["config"] = json.load(f)
        
        return info

def main():
    parser = argparse.ArgumentParser(description="Qwen2.5 모델 다운로더")
    parser.add_argument(
        "--model", 
        choices=["qwen2.5-0.5b", "qwen2.5-0.5b-instruct", "qwen2-0.5b", "qwen2-0.5b-instruct"],
        default="qwen2.5-0.5b-instruct",
        help="다운로드할 모델 선택"
    )
    parser.add_argument("--cache-dir", default="./models", help="모델 저장 디렉토리")
    parser.add_argument("--force", action="store_true", help="강제 재다운로드")
    parser.add_argument("--verify", action="store_true", help="다운로드 후 검증")
    
    args = parser.parse_args()
    
    print("🔥 기가차드 모드 - Qwen2.5 모델 다운로더")
    print("=" * 50)
    
    downloader = QwenModelDownloader(cache_dir=args.cache_dir)
    
    try:
        # 모델 다운로드
        model_path = downloader.download_model(args.model, force_download=args.force)
        
        # 모델 정보 출력
        info = downloader.get_model_info(model_path)
        print(f"\n📊 모델 정보:")
        print(f"   경로: {info['path']}")
        print(f"   크기: {info['size_gb']:.2f} GB")
        print(f"   파일 수: {len(info['files'])}")
        
        if info["config"]:
            print(f"   모델 타입: {info['config'].get('model_type', 'unknown')}")
            print(f"   어휘 크기: {info['config'].get('vocab_size', 'unknown')}")
            print(f"   레이어 수: {info['config'].get('num_hidden_layers', 'unknown')}")
        
        # 검증 실행
        if args.verify:
            print(f"\n🔍 모델 검증 중...")
            if downloader.verify_model(model_path):
                print("✅ 모델 검증 완료!")
            else:
                print("❌ 모델 검증 실패!")
                sys.exit(1)
        
        print(f"\n🎉 모든 작업 완료!")
        print(f"📁 모델 경로: {model_path}")
        
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 