"""
FastAPI 서버와 핸들러 간에 공유되는 타입 정의
"""
from typing import TypedDict
from .handlers.web_search_handler import SearchResult

# --- TypedDicts for Assistant Handler Responses ---

class ImproveSentenceResult(TypedDict):
    vivid_sentence: str
    concise_sentence: str
    character_voice_sentence: str
    model: str
    cost: float
    tokens: int

class SmartSentenceImprovementResult(TypedDict):
    improvement_suggestions: str
    model: str
    cost: float
    tokens: int

class PlotHoleDetectionResult(TypedDict):
    detection_report: str
    model: str
    cost: float
    tokens: int

class CharacterConsistencyResult(TypedDict):
    consistency_report: str
    model: str
    cost: float
    tokens: int

class CliffhangerSuggestion(TypedDict):
    suggestion: str
    expected_reaction: str

class CliffhangerGenerationResult(TypedDict):
    suggestions: list[CliffhangerSuggestion]
    model: str
    cost: float
    tokens: int

class ReaderResponseResult(TypedDict):
    prediction_report: dict[str, str | float]
    model: str
    cost: float
    tokens: int
    
class EpisodeLengthResult(TypedDict):
    optimization_report: dict[str, object]  # replaced Any with object
    model: str
    cost: float
    tokens: int

class BetaReadResult(TypedDict):
    beta_read_report: dict[str, object]  # replaced Any with object
    model: str
    cost: float
    tokens: int
    
class TrendAnalysisResult(TypedDict):
    trend_report: str
    model: str
    cost: float
    tokens: int
    searched_data: list[SearchResult] 