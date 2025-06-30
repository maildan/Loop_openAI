"""
Google Docs 통합을 위한 핸들러
"""

import os
import logging
from typing import Any, TypedDict, NoReturn
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


# --- Custom Exceptions for Granular Error Handling ---
class GoogleApiError(IOError):
    """Base exception for Google Docs API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DocumentNotFound(GoogleApiError):
    """Raised when a document is not found (404)."""


class PermissionDenied(GoogleApiError):
    """Raised when permission is denied (403)."""


class ServerError(GoogleApiError):
    """Raised for server-side errors (5xx)."""


class MalformedRequestError(GoogleApiError):
    """Raised for malformed requests (400), e.g., malformed HTML."""


# --- TypedDicts for Google Docs API Objects ---
class TextRun(TypedDict):
    """문서의 텍스트 런을 나타냅니다."""

    content: str


class ParagraphElement(TypedDict):
    """단락 내의 요소를 나타냅니다."""

    textRun: TextRun


class Paragraph(TypedDict):
    """문서의 단락을 나타냅니다."""

    elements: list[ParagraphElement]


class StructuralElement(TypedDict, total=False):
    """문서의 구조적 요소를 나타냅니다."""

    paragraph: Paragraph
    endIndex: int


class Body(TypedDict):
    """문서의 본문을 나타냅니다."""

    content: list[StructuralElement]


class Document(TypedDict):
    """Google 문서를 나타냅니다."""

    documentId: str
    title: str
    body: Body


class CreatedDocument(TypedDict):
    """생성된 문서 정보를 나타냅니다."""

    document_id: str
    title: str
    url: str


class UpdatedDocument(TypedDict):
    """업데이트된 문서 정보를 나타냅니다."""

    document_id: str
    updated: bool
    url: str


class GoogleDocsHandler:
    """Google Docs API를 사용하여 문서를 관리하는 핸들러 (동기 방식)"""

    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    credentials: Credentials | None
    service: Any

    def __init__(self) -> None:
        """Google Docs 핸들러 초기화"""
        self.credentials = self._initialize_credentials()
        self.service = build("docs", "v1", credentials=self.credentials)
        logger.info("✅ Google Docs 서비스 초기화 완료")

    def _handle_http_error(
        self, e: HttpError, operation: str, document_id: str | None = None
    ) -> NoReturn:
        """Handles HttpError and raises a more specific custom exception."""
        status_code = e.resp.status
        doc_id_str = f" for document '{document_id}'" if document_id else ""
        message = (
            f"❌ {operation}{doc_id_str} failed with status {status_code}: {e.reason}"
        )
        logger.error(message)

        if status_code == 400:
            raise MalformedRequestError(message, status_code) from e
        if status_code == 403:
            raise PermissionDenied(message, status_code) from e
        if status_code == 404:
            raise DocumentNotFound(message, status_code) from e
        if status_code >= 500:
            raise ServerError(message, status_code) from e

        raise GoogleApiError(message, status_code) from e

    def _initialize_credentials(self) -> Credentials:
        """Google API 자격 증명 초기화 및 반환"""
        try:
            creds = Credentials(
                token=os.getenv("GOOGLE_ACCESS_TOKEN"),
                refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                token_uri="https://oauth2.googleapis.com/token",
                scopes=self.SCOPES,
            )

            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logger.info("✅ Google 자격 증명 새로고침 완료")
                else:
                    raise ConnectionError("Google API 자격 증명을 얻거나 새로고침할 수 없습니다.")
            return creds

        except Exception as e:
            logger.error(f"❌ Google 자격 증명 초기화 실패: {e}")
            raise

    def extract_document_content(self, document_id: str) -> str:
        """문서의 텍스트 내용을 추출"""
        try:
            document = self.get_document(document_id)
            body = document.get("body")
            if not body:
                return ""

            content_elements = body.get("content", [])
            text_content = []
            for structural_element in content_elements:
                if "paragraph" in structural_element:
                    paragraph = structural_element["paragraph"]
                    for element in paragraph.get("elements", []):
                        if "textRun" in element:
                            text_content.append(element["textRun"]["content"])

            return "".join(text_content)

        except HttpError as e:
            self._handle_http_error(e, "Extract document content", document_id)

    def analyze_document(self, document_id: str) -> dict[str, Any]:
        """문서 분석 및 주요 정보 추출"""
        try:
            content = self.extract_document_content(document_id)

            analysis: dict[str, Any] = {
                "word_count": len(content.split()),
                "char_count": len(content),
                "paragraphs": content.count("\n\n") + 1,
                "content": content[:1000],  # 첫 1000자만 반환
                "summary": self._generate_summary(content),
            }

            return analysis

        except Exception as e:
            logger.error(f"❌ 문서 분석 실패: {e}")
            raise

    def _generate_summary(self, content: str) -> str:
        """문서 내용 요약 생성"""
        return content[:200] + "..."  # 임시로 첫 200자만 반환

    def create_document(self, title: str, content: str) -> CreatedDocument:
        """새로운 Google 문서 생성"""
        try:
            doc_body = {"title": title}
            document = self.service.documents().create(body=doc_body).execute()
            document_id = document["documentId"]

            requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()

            result: CreatedDocument = {
                "document_id": document_id,
                "title": title,
                "url": f"https://docs.google.com/document/d/{document_id}/edit",
            }
            return result

        except HttpError as e:
            self._handle_http_error(e, "Create document", title)

    def get_document(self, document_id: str) -> Document:
        """문서 내용 가져오기"""
        try:
            document: Document = (
                self.service.documents().get(documentId=document_id).execute()
            )
            return document
        except HttpError as e:
            self._handle_http_error(e, "Get document", document_id)

    def update_document(self, document_id: str, content: str) -> UpdatedDocument:
        """문서 내용 업데이트"""
        try:
            document = self.get_document(document_id)
            body = document.get("body")
            end_index = 1
            if body:
                doc_content = body.get("content")
                if doc_content:
                    last_element = doc_content[-1]
                    end_index = last_element.get("endIndex", 1)

            requests: list[dict[str, Any]] = []
            if end_index > 1:
                requests.append(
                    {
                        "deleteContentRange": {
                            "range": {"startIndex": 1, "endIndex": end_index - 1}
                        }
                    }
                )

            requests.append({"insertText": {"location": {"index": 1}, "text": content}})

            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()

            result: UpdatedDocument = {
                "document_id": document_id,
                "updated": True,
                "url": f"https://docs.google.com/document/d/{document_id}/edit",
            }
            return result

        except HttpError as e:
            self._handle_http_error(e, "Update document", document_id)
