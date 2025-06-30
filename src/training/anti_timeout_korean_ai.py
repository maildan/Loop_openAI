import streamlit as st
import openai
import os
import time
import threading
from datetime import datetime
import uuid
from typing import TypedDict, Literal, Any, cast

# --- Type Definitions ---
JobStatus = Literal["created", "processing", "completed", "error"]

class Job(TypedDict):
    id: str
    prompt: str
    genre: str
    temperature: float
    max_tokens: int
    status: JobStatus
    progress: int
    result: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


# API 키 설정
api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key

# 전역 작업 상태 저장소
if "jobs" not in st.session_state:
    st.session_state.jobs = {}


class AntiTimeoutAI:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = st.session_state.jobs

    def create_job(
        self, prompt: str, genre: str, temperature: float = 0.8, max_tokens: int = 1000
    ) -> str:
        """새 작업 생성"""
        job_id = str(uuid.uuid4())[:8]

        self.jobs[job_id] = {
            "id": job_id,
            "prompt": prompt,
            "genre": genre,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "status": "created",
            "progress": 0,
            "result": None,
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        return job_id

    def update_job(self, job_id: str, **kwargs: Any) -> None:
        """작업 상태 업데이트"""
        if job_id in self.jobs:
            # TypedDict is structurally compatible with dict, but for update, casting is safer
            cast(dict[str, Any], cast(object, self.jobs[job_id])).update(kwargs)
            self.jobs[job_id]["updated_at"] = datetime.now()

    def process_job_background(self, job_id: str) -> None:
        """백그라운드에서 작업 처리"""
        try:
            job = self.jobs[job_id]

            # 시작
            self.update_job(job_id, status="processing", progress=10)
            time.sleep(0.5)

            # 시스템 프롬프트
            system_prompts = {
                "판타지": "한국 판타지 소설 전문가. 창의적이고 몰입감 있는 스토리 창작.",
                "로맨스": "한국 로맨스 소설 전문가. 감정적 몰입도 높은 연애 스토리 창작.",
                "SF": "한국 SF 소설 전문가. 과학적 상상력과 현실의 조화로운 스토리 창작.",
                "미스터리": "한국 미스터리 소설 전문가. 치밀한 추리와 반전이 있는 스토리 창작.",
                "드라마": "한국 드라마 작가. 일상적이면서 감동적인 인간 드라마 창작.",
            }

            system_prompt = system_prompts.get(job["genre"], system_prompts["판타지"])

            self.update_job(job_id, progress=30)

            # OpenAI API 호출 (스트리밍)
            if not openai or not openai.api_key:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": job["prompt"]},
                ],
                max_tokens=job["max_tokens"],
                temperature=job["temperature"],
                stream=True,
            )

            self.update_job(job_id, progress=50)

            # 결과 수집
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # 진행상황 업데이트
                    # Ensure progress doesn't exceed 90 before completion
                    current_progress = 50 + int(len(full_response) / (job["max_tokens"] * 1.2) * 40)
                    self.update_job(job_id, progress=min(90, current_progress))


            # 완료
            self.update_job(
                job_id, status="completed", progress=100, result=full_response
            )

        except Exception as e:
            self.update_job(job_id, status="error", error=str(e))

    def start_job(self, job_id: str) -> threading.Thread:
        """작업 시작 (백그라운드)"""
        thread = threading.Thread(target=self.process_job_background, args=(job_id,))
        thread.daemon = True
        thread.start()
        return thread


def main() -> None:
    _ = st.set_page_config(
        page_title="⚡ 안티 타임아웃 한국어 AI", page_icon="🔥", layout="wide"
    )

    _ = st.title("⚡ 안티 타임아웃 한국어 창작 AI")
    _ = st.markdown("**타임아웃 걱정 없는 기가차드식 AI** 🚀")

    ai = AntiTimeoutAI()

    # 사이드바
    with st.sidebar:
        _ = st.header("⚙️ 설정")

        genre = st.selectbox("장르", ["판타지", "로맨스", "SF", "미스터리", "드라마"])
        if not isinstance(genre, str):
            genre = "판타지" # Default value for type safety

        temperature = st.slider("창의성", 0.1, 1.0, 0.8, 0.1)
        max_tokens = st.slider("길이", 500, 2000, 1000, 100)

        _ = st.markdown("---")
        _ = st.subheader("📊 작업 현황")

        # 활성 작업 수
        active_jobs = [j for j in ai.jobs.values() if j["status"] == "processing"]
        completed_jobs = [j for j in ai.jobs.values() if j["status"] == "completed"]

        _ = st.metric("진행 중", len(active_jobs))
        _ = st.metric("완료됨", len(completed_jobs))

    # 메인 영역
    col1, col2 = st.columns([1, 1])

    with col1:
        _ = st.subheader("📝 창작 요청")

        prompt = st.text_area(
            "창작할 내용을 입력하세요",
            height=150,
            placeholder="예: 미래 서울에서 AI와 인간이 공존하는 사회를 배경으로 한 SF 로맨스...",
        )

        if st.button("🚀 창작 시작", type="primary"):
            if prompt and api_key:
                job_id = ai.create_job(prompt, genre, float(temperature), int(max_tokens))
                _ = ai.start_job(job_id)
                _ = st.success(f"작업 시작! ID: {job_id}")
                st.rerun()
            elif not api_key:
                _ = st.error("API 키가 필요합니다!")
            else:
                _ = st.warning("프롬프트를 입력하세요!")

        # 작업 목록
        if ai.jobs:
            _ = st.subheader("📋 작업 목록")
            # Sort jobs by creation time, most recent first
            sorted_jobs = sorted(
                ai.jobs.values(), key=lambda j: j["created_at"], reverse=True
            )
            for job in sorted_jobs:
                with st.expander(f"작업 {job['id']} - {job['status']}"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        _ = st.write(f"**장르**: {job['genre']}")
                        _ = st.write(f"**프롬프트**: {job['prompt'][:100]}...")
                        _ = st.write(
                            f"**생성시간**: {job['created_at'].strftime('%H:%M:%S')}"
                        )

                    with col_b:
                        if job["status"] == "processing":
                            _ = st.progress(job["progress"] / 100)
                            _ = st.write(f"{job['progress']}%")
                        elif job["status"] == "completed":
                            _ = st.success("완료!")
                        elif job["status"] == "error":
                            _ = st.error("오류")

    with col2:
        _ = st.subheader("📖 결과")

        # 자동 새로고침 (진행 중인 작업이 있을 때)
        if active_jobs:
            time.sleep(2)
            st.rerun()

        # 최신 완료된 작업 표시
        if completed_jobs:
            latest_job = max(completed_jobs, key=lambda j: j["updated_at"])

            _ = st.markdown(f"### 작업 {latest_job['id']} 결과")
            if latest_job["result"]:
                _ = st.write(latest_job["result"])

                # 메타 정보
                _ = st.markdown("---")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    _ = st.write(f"**장르**: {latest_job['genre']}")
                    _ = st.write(
                        f"**완료시간**: {latest_job['updated_at'].strftime('%H:%M:%S')}"
                    )
                with col_info2:
                    word_count = len(latest_job["result"].replace(" ", ""))
                    _ = st.write(f"**글자수**: {word_count:,}자")

                    # 다운로드
                    _ = st.download_button(
                        "💾 다운로드",
                        latest_job["result"],
                        f"{latest_job['genre']}_{latest_job['id']}.txt",
                        "text/plain",
                    )
            else:
                _ = st.warning("결과가 아직 준비되지 않았습니다.")

        else:
            _ = st.info("완료된 작업이 없습니다. 창작을 시작해보세요!")


if __name__ == "__main__":
    main()
