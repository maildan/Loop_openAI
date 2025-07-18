"""
YAML 형식의 프롬프트 파일을 로드하고 관리하는 모듈
"""
import yaml
import os
import json
from jinja2 import Environment, BaseLoader
from typing import TypedDict, cast

class PromptConfig(TypedDict, total=False):
    name: str
    template: str
    levels: dict[str, str]
    persona: str

# --- 상수 정의 ---
# 현재 파일의 디렉토리를 기준으로 경로를 설정합니다.
PROMPT_DIR = os.path.dirname(__file__)
# dataset 디렉토리는 프로젝트 루트에 있다고 가정합니다.
# loader.py -> prompts -> shared -> src -> loop_ai (project_root)
PROJECT_ROOT = os.path.abspath(os.path.join(PROMPT_DIR, '..', '..', '..'))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")

# --- 데이터 로딩 함수 ---

def load_prompts_config() -> dict[str, list[PromptConfig]]:
    """
    PROMPT_DIR에 있는 모든 .yml 파일을 로드하여 하나의 딕셔너리로 병합합니다.
    모든 YAML 파일은 'prompts' 키 아래에 프롬프트 리스트를 포함해야 합니다.
    """
    combined_config: dict[str, list[PromptConfig]] = {"prompts": []}

    for filename in os.listdir(PROMPT_DIR):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            file_path = os.path.join(PROMPT_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = cast(dict[str, object], yaml.safe_load(f) or {})
                # 'prompts' 키가 있을 때만 처리합니다.
                if "prompts" in data:
                    prompts_obj: object = data["prompts"]
                    if isinstance(prompts_obj, list):
                        combined_config["prompts"].extend(cast(list[PromptConfig], prompts_obj))
                else:
                    # 예상치 못한 형식의 파일에 대한 경고
                    print(f"Warning: '{filename}' is not in the expected format (missing 'prompts' key) and will be skipped.")

    if not combined_config["prompts"]:
        raise FileNotFoundError(f"프롬프트 파일이 존재하지 않거나 유효한 프롬프트가 없습니다: {PROMPT_DIR}")

    return combined_config

def load_datasets() -> dict[str, object]:
    """
    dataset 디렉토리의 모든 JSON 파일을 로드하여 딕셔너리로 반환합니다.
    파일 이름(확장자 제외)이 키가 됩니다.
    """
    datasets: dict[str, object] = {}
    if not os.path.isdir(DATASET_DIR):
        # Dataset directory not found; skipping without warning
        return datasets

    for filename in os.listdir(DATASET_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(DATASET_DIR, filename)
            dataset_name = os.path.splitext(filename)[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                datasets[dataset_name] = json.load(f)
    return datasets

# --- 프롬프트 생성 함수 ---

def get_prompt(prompt_name: str, **kwargs: object) -> str:
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

    prompt_configs = config["prompts"]
    prompt_config = next((p for p in prompt_configs if "name" in p and p["name"] == prompt_name), None)

    if not prompt_config:
        if prompt_name == "system_prompt":
            return get_system_prompt()
        raise ValueError(f"'{prompt_name}'에 해당하는 프롬프트를 찾을 수 없습니다.")

    # level 결정
    if "level" in kwargs and isinstance(kwargs["level"], str):
        level: str = kwargs["level"]
    else:
        level = "beginner"
    # levels에서 우선 조회
    if "levels" in prompt_config:
        levels_dict = prompt_config["levels"]
        template_string = levels_dict.get(level, "")
    else:
        template_string = ""
    # template로 fallback
    if not template_string and "template" in prompt_config:
        template_string = prompt_config["template"]

    if not template_string:
        raise ValueError(f"'{prompt_name}' 프롬프트의 '{level}' 레벨에 해당하는 템플릿을 찾을 수 없습니다.")

    context: dict[str, object] = {"dataset": datasets}
    for key, value in kwargs.items():
        context[key] = value
    return Environment(loader=BaseLoader()).from_string(template_string).render(context)

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