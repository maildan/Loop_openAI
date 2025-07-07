"""
YAML 형식의 프롬프트 파일을 로드하고 관리하는 모듈
"""
import yaml
import os
import json
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound

# --- 상수 정의 ---
# 현재 파일의 디렉토리를 기준으로 경로를 설정합니다.
PROMPT_DIR = os.path.dirname(__file__)
# dataset 디렉토리는 프로젝트 루트에 있다고 가정합니다.
# loader.py -> prompts -> shared -> src -> loop_ai (project_root)
PROJECT_ROOT = os.path.abspath(os.path.join(PROMPT_DIR, '..', '..', '..'))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")

# --- 데이터 로딩 함수 ---

def load_prompts_config() -> Dict[str, Any]:
    """
    PROMPT_DIR에 있는 모든 .yml 파일을 로드하여 하나의 딕셔너리로 병합합니다.
    모든 YAML 파일은 'prompts' 키 아래에 프롬프트 리스트를 포함해야 합니다.
    """
    combined_config: Dict[str, Any] = {"prompts": []}

    for filename in os.listdir(PROMPT_DIR):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            file_path = os.path.join(PROMPT_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
                # 모든 YAML 파일이 'prompts' 키를 가지고 있다고 가정하고 데이터를 로드합니다.
                if isinstance(data, dict) and "prompts" in data:
                    prompt_list = data.get("prompts")
                    if isinstance(prompt_list, list):
                        combined_config["prompts"].extend(prompt_list)
                else:
                    # 예상치 못한 형식의 파일에 대한 경고
                    print(f"Warning: '{filename}' is not in the expected format (missing 'prompts' key) and will be skipped.")

    if not combined_config["prompts"]:
        raise FileNotFoundError(f"프롬프트 파일이 존재하지 않거나 유효한 프롬프트가 없습니다: {PROMPT_DIR}")

    return combined_config

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

    # 'prompts' 리스트에서 prompt_name에 맞는 설정을 찾습니다.
    prompt_config = next((p for p in config.get("prompts", []) if p.get("name") == prompt_name), None)

    if not prompt_config:
        # 시스템 프롬프트 요청에 대한 예외 처리
        if prompt_name == "system_prompt":
            return get_system_prompt()
        raise ValueError(f"'{prompt_name}'에 해당하는 프롬프트를 찾을 수 없습니다.")

    # 레벨에 따른 템플릿 선택
    level = kwargs.get("level", "beginner") # 기본 레벨은 'beginner'
    template_string = prompt_config.get("levels", {}).get(level)
    
    if not template_string:
         # 레벨이 없는 경우, 최상위 템플릿 사용 (하위 호환성)
        template_string = prompt_config.get("template", "")
    
    if not template_string:
        raise ValueError(f"'{prompt_name}' 프롬프트의 '{level}' 레벨에 해당하는 템플릿을 찾을 수 없습니다.")

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
    'system_prompt'라는 이름의 프롬프트를 찾아 반환합니다.
    """
    config = load_prompts_config()
    system_prompt_config = next((p for p in config.get("prompts", []) if p.get("name") == "system_prompt"), None)
    
    if system_prompt_config and "template" in system_prompt_config:
        return system_prompt_config["template"]
    
    # 대체 기본 프롬프트
    return "당신은 전문 작가를 돕는 AI 어시스턴트, Loop AI입니다. 항상 작가의 창작 활동을 최대한 지원해주세요." 