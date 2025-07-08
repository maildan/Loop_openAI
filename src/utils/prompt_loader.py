import os
import yaml
from typing import cast

# 올바른 프롬프트 파일의 상대 경로
PROMPTS_FILE_PATH = os.path.join("src", "shared", "prompts", "story_prompts.yml")

def load_prompts_from_file() -> dict[str, dict[str, str]]:
    """
    YAML 파일에서 프롬프트를 로드합니다.
    파일이 없거나 오류 발생 시 대체 프롬프트를 반환합니다.
    """
    try:
        # 프로젝트 루트는 src/utils에서 세 단계 상위 디렉토리로 이동하여 loop_ai 디렉토리입니다.
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, PROMPTS_FILE_PATH)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = cast(dict[str, object], yaml.safe_load(f) or {})
            raw_prompts = data.get('prompts', [])
            prompts_list: list[dict[str, str]] = cast(list[dict[str, str]], raw_prompts) if isinstance(raw_prompts, list) else []
            prompts: dict[str, dict[str, str]] = {}
            for p in prompts_list:
                if 'name' in p:
                    prompts[p['name']] = p

        if not prompts:
            print(f"⚠️ 경고: {PROMPTS_FILE_PATH} 파일이 비어있거나 'prompts' 키를 찾을 수 없습니다. 대체 프롬프트를 사용합니다.")
            raise FileNotFoundError
        return prompts
    except FileNotFoundError:
        print(f"❌ 오류: {PROMPTS_FILE_PATH}을(를) 찾을 수 없어 대체 프롬프트를 사용합니다.")
        return {
            'intent_classifier': {'template': '사용자 메시지: "{user_message}"\n의도:'},
            'general': {'template': '안녕하세요!'},
        }
    except yaml.YAMLError as e:
        print(f"❌ 치명적 오류: {PROMPTS_FILE_PATH} 파싱 오류: {e}")
        raise e

# 모듈 로드 시 프롬프트를 캐싱합니다.
_PROMPTS: dict[str, dict[str, str]] = load_prompts_from_file()

def get_prompt(key: str, **kwargs: object) -> str:
    """
    로드된 프롬프트에서 키에 해당하는 템플릿을 가져와 포맷팅합니다.
    """
    prompt_data = _PROMPTS.get(key)
    if prompt_data is None or 'template' not in prompt_data:
        print(f"⚠️ 경고: 프롬프트 키 '{key}' 또는 해당 템플릿을 찾을 수 없습니다.")
        return ""
    
    return prompt_data['template'].format(**kwargs) 