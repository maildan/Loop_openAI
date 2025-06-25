"""
Google Docs 통합을 위한 핸들러
"""

import os
import logging
from typing import Optional, Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleDocsHandler:
    """Google Docs API를 사용하여 문서를 관리하는 핸들러"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self):
        """Google Docs 핸들러 초기화"""
        self.credentials = None
        self.service = None
        self._initialize_credentials()
        
    def _initialize_credentials(self) -> None:
        """Google API 자격 증명 초기화"""
        try:
            self.credentials = Credentials(
                token=os.getenv('GOOGLE_ACCESS_TOKEN'),
                refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                token_uri='https://oauth2.googleapis.com/token',
                scopes=self.SCOPES
            )
            
            # 토큰이 만료되었거나 곧 만료될 예정이면 새로고침
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    logger.info("✅ Google 자격 증명 새로고침 완료")
            
            self.service = build('docs', 'v1', credentials=self.credentials)
            logger.info("✅ Google Docs 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Google 자격 증명 초기화 실패: {e}")
            raise

    async def extract_document_content(self, document_id: str) -> str:
        """문서의 텍스트 내용을 추출"""
        try:
            document = await self.get_document(document_id)
            content = document.get('body', {}).get('content', [])
            
            text_content = []
            for element in content:
                if 'paragraph' in element:
                    for para_element in element['paragraph'].get('elements', []):
                        if 'textRun' in para_element:
                            text_content.append(para_element['textRun'].get('content', ''))
            
            return ''.join(text_content)
            
        except HttpError as e:
            logger.error(f"❌ 문서 내용 추출 실패: {e}")
            raise

    async def analyze_document(self, document_id: str) -> Dict[str, Any]:
        """문서 분석 및 주요 정보 추출"""
        try:
            content = await self.extract_document_content(document_id)
            
            # 문서 분석 결과
            analysis = {
                'word_count': len(content.split()),
                'char_count': len(content),
                'paragraphs': content.count('\n\n') + 1,
                'content': content[:1000],  # 첫 1000자만 반환
                'summary': await self._generate_summary(content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ 문서 분석 실패: {e}")
            raise

    async def _generate_summary(self, content: str) -> str:
        """문서 내용 요약 생성"""
        # 여기에 요약 로직 구현
        # OpenAI나 다른 AI 모델을 사용하여 요약 생성
        return content[:200] + "..."  # 임시로 첫 200자만 반환

    async def create_document(self, title: str, content: str) -> Dict[str, Any]:
        """새로운 Google 문서 생성"""
        try:
            # 빈 문서 생성
            document = self.service.documents().create(body={'title': title}).execute()
            document_id = document.get('documentId')
            
            # 문서에 내용 추가
            requests = [{
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': content
                }
            }]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return {
                'document_id': document_id,
                'title': title,
                'url': f'https://docs.google.com/document/d/{document_id}/edit'
            }
            
        except HttpError as e:
            logger.error(f"❌ Google Docs API 오류: {e}")
            raise

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """문서 내용 가져오기"""
        try:
            document = self.service.documents().get(documentId=document_id).execute()
            return document
        except HttpError as e:
            logger.error(f"❌ 문서 가져오기 실패: {e}")
            raise

    async def update_document(self, document_id: str, content: str) -> Dict[str, Any]:
        """문서 내용 업데이트"""
        try:
            # 기존 내용 삭제
            document = await self.get_document(document_id)
            end_index = len(document.get('body').get('content', []))
            
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]
            
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return {
                'document_id': document_id,
                'updated': True,
                'url': f'https://docs.google.com/document/d/{document_id}/edit'
            }
            
        except HttpError as e:
            logger.error(f"❌ 문서 업데이트 실패: {e}")
            raise 