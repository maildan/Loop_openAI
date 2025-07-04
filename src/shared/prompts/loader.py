"""
YAML 형식의 프롬프트 파일을 로드하고 관리하는 모듈
"""
import yaml
import os
import json
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound

# --- 상수 정의 ---
# 현재 파일의 디렉토리를 기준으로 경로를 설정합니다.
PROMPT_DIR = os.path.dirname(__file__)
PROMPTS_FILE = os.path.join(PROMPT_DIR, "story_prompts.yml")
# dataset 디렉토리는 프로젝트 루트에 있다고 가정합니다.
# loader.py -> prompts -> shared -> src -> loop_ai (project_root)
PROJECT_ROOT = os.path.abspath(os.path.join(PROMPT_DIR, '..', '..', '..'))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")

# --- 데이터 로딩 함수 ---

def load_prompts_config() -> Dict[str, Any]:
    """
    story_prompts.yml 파일을 로드하여 딕셔너리로 반환합니다.
    """
    if not os.path.exists(PROMPTS_FILE):
        raise FileNotFoundError(f"프롬프트 파일이 존재하지 않습니다: {PROMPTS_FILE}")

    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_datasets() -> Dict[str, Any]:
    """
    dataset 디렉토리의 모든 JSON 파일을 로드하여 딕셔너리로 반환합니다.
    파일 이름(확장자 제외)이 키가 됩니다.
    """
    datasets = {}
    if not os.path.isdir(DATASET_DIR):
        # 데이터셋 디렉토리가 없는 경우 경고를 출력하고 빈 딕셔너리를 반환할 수 있습니다.
        print(f"Warning: Dataset directory not found at {DATASET_DIR}")
        return datasets

    for filename in os.listdir(DATASET_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(DATASET_DIR, filename)
            dataset_name = os.path.splitext(filename)[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                datasets[dataset_name] = json.load(f)
    return datasets

# --- 프롬프트 생성 함수 ---

def get_prompt(prompt_name: str, **kwargs: Any) -> str:
    """
    지정된 이름의 프롬프트를 로드하고, 데이터셋과 주어진 변수로 포맷팅하여 반환합니다.
    Jinja2 템플릿 엔진을 사용하여 동적 프롬프트를 생성합니다.

    Args:
        prompt_name (str): 가져올 프롬프트의 이름 (e.g., 'character_development')
        **kwargs: 프롬프트 템플릿을 채울 변수들

    Returns:
        str: 완성된 프롬프트 문자열
    """
    config = load_prompts_config()
    datasets = load_datasets()

    prompt_config = config.get("prompt_templates", {}).get(prompt_name)

    if not prompt_config:
        raise ValueError(f"'{prompt_name}'에 해당하는 프롬프트를 찾을 수 없습니다.")

    template_string = prompt_config.get("template", "")

    # Jinja2 템플릿 렌더링
    template = Environment(loader=BaseLoader()).from_string(template_string)
    
    # 템플릿에 전달할 전체 컨텍스트
    # kwargs가 우선순위를 갖도록 하여, 사용자가 직접 입력한 값으로 데이터셋 값을 덮어쓸 수 있게 함
    context = {
        "dataset": datasets,
        **kwargs
    }
    
    return template.render(context)

def get_system_prompt() -> str:
    """
    마스터 시스템 프롬프트만 반환합니다.
    시스템 프롬프트는 동적 데이터가 필요 없다고 가정합니다.
    """
    config = load_prompts_config()
    return config.get("master_system_prompt", "") 