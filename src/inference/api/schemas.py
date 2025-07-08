"""공통 Pydantic 모델 정의 모듈
FastAPI 라우터들이 공통으로 사용하는 Request/Response 모델을 한곳에 모아 관리합니다.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# --- Spellcheck ---
class SpellCheckRequest(BaseModel):
    text: str = Field(..., description="맞춤법 검사할 텍스트")
    auto_correct: bool = Field(True, description="자동 보정 사용 여부")
    full_document: str | None = Field(None, description="전체 문서(컨텍스트)")
    use_ai: bool = Field(False, description="AI 문맥 교정 사용 여부")

class SpellCheckResponse(BaseModel):
    original_text: str
    corrected_text: str
    errors_found: int
    error_words: list[str]
    accuracy: float
    total_words: int
    reason: str | None = None
    context_analysis: str | None = None

# --- Web Search ---
class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    publishedDate: str | None = None
    favicon: str | None = None

class WebSearchRequest(BaseModel):
    query: str
    source: str = Field("web", description="검색 소스(web, research 등)")
    num_results: int = Field(5, ge=1, le=10)
    include_summary: bool = True

class WebSearchResponse(BaseModel):
    query: str
    source: str
    num_results: int
    results: list[WebSearchResult]
    summary: str = ""
    timestamp: str
    from_cache: bool = False
    response_time: float

class WebSearchStatsResponse(BaseModel):
    total_searches: int
    cache_hits: int
    cache_misses: int
    avg_response_time: float
    last_search_time: str | None
    cache_enabled: bool

# --- 비용 ---
class CostStatusResponse(BaseModel):
    monthly_cost: float
    monthly_budget: float
    usage_percentage: float
    total_tokens: int
    cache_hits: int

# --- Location ---
class LocationSuggestRequest(BaseModel):
    query: str

class LocationSuggestResponse(BaseModel):
    suggestions: list[str]

# --- Name Generator ---
class NameGenerateRequest(BaseModel):
    style: str = Field("isekai")
    gender: str = Field("female")
    character_class: str | None = None
    element: str | None = None

class MultipleNamesRequest(BaseModel):
    count: int = Field(10, ge=1, le=50)
    gender: str = Field("female")
    style: str = Field("mixed")

class BatchGenerateRequest(BaseModel):
    count_per_category: int = Field(5, ge=1, le=20)

# --- Sentence Improvement ---
class SentenceImprovementRequest(BaseModel):
    original_sentence: str
    genre: str
    character_profile: str
    context: str
    model: str | None = None

class SentenceImprovementResponse(BaseModel):
    suggestions: dict[str, str]
    model: str
    cost: float
    tokens: int

# --- Plot Hole Detection ---
class PlotHoleDetectionRequest(BaseModel):
    full_story_text: str = Field(..., min_length=100)
    model: str | None = Field("gpt-4o")

class PlotHoleDetectionResponse(BaseModel):
    detection_report: str
    model: str
    cost: float
    tokens: int

# --- Character Consistency ---
class CharacterConsistencyRequest(BaseModel):
    character_name: str
    personality: str
    speech_style: str
    core_values: str
    other_settings: str = ""
    story_text_for_analysis: str
    model: str | None = Field("gpt-4o")

class CharacterConsistencyResponse(BaseModel):
    consistency_report: str
    model: str
    cost: float
    tokens: int

# --- Cliffhanger ---
class CliffhangerRequest(BaseModel):
    genre: str
    scene_context: str
    model: str | None = Field("gpt-4o")

class CliffhangerSuggestion(BaseModel):
    suggestion: str
    expected_reaction: str

class CliffhangerResponse(BaseModel):
    suggestions: list[CliffhangerSuggestion]
    model: str
    cost: float
    tokens: int

# --- Reader Response ---
class ReaderResponseRequest(BaseModel):
    platform: str
    scene_context: str
    model: str | None = Field("gpt-4o")

class ReaderResponseResponse(BaseModel):
    prediction_report: dict[str, str | float]  # allow str or float values
    model: str
    cost: float
    tokens: int

# --- Smart Sentence Improvement ---
class SmartSentenceImprovementRequest(BaseModel):
    original_text: str
    model: str | None = None

class SmartSentenceImprovementResponse(BaseModel):
    improvement_suggestions: str
    model: str
    cost: float
    tokens: int

# --- Episode Length Optimization ---
class EpisodeLengthRequest(BaseModel):
    platform: str
    episode_text: str
    model: str | None = Field("gpt-4o")

class EpisodeLengthResponse(BaseModel):
    optimization_report: dict[str, object]  # replaced Any with object
    model: str
    cost: float
    tokens: int

# --- Beta Read ---
class BetaReadRequest(BaseModel):
    manuscript: str
    genre: str
    target_audience: str
    author_concerns: str | None = None
    model: str | None = Field("gpt-4o")

class BetaReadResponse(BaseModel):
    beta_read_report: dict[str, object]  # replaced Any with object
    model: str
    cost: float
    tokens: int

# --- Trend Analysis ---
class TrendAnalysisRequest(BaseModel):
    genre: str
    synopsis: str
    keywords: list[str] = []
    platform: str = Field("카카오페이지")
    model: str | None = Field("gpt-4o")

class TrendAnalysisResponse(BaseModel):
    trend_report: str
    model: str
    cost: float
    tokens: int
    searched_data: list[dict[str, object]]  # replaced Any with object 