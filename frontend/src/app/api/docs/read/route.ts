import { NextRequest, NextResponse } from 'next/server'
import { google } from 'googleapis'

export async function POST(request: NextRequest) {
  try {
    const { documentId } = await request.json()

    if (!documentId) {
      return NextResponse.json(
        { error: '문서 ID가 필요합니다.' },
        { status: 400 }
      )
    }

    // OAuth2 클라이언트 설정
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      'http://localhost:3000'
    )

    // 액세스 토큰 설정
    oauth2Client.setCredentials({
      access_token: process.env.GOOGLE_ACCESS_TOKEN,
      refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
    })

    const docs = google.docs({ version: 'v1', auth: oauth2Client })

    // 문서 내용 가져오기
    const response = await docs.documents.get({
      documentId: documentId,
    })

    const document = response.data
    if (!document || !document.body) {
      throw new Error('문서 내용을 가져올 수 없습니다.')
    }

    // 텍스트 추출
    let content = ''
    if (document.body.content) {
      for (const element of document.body.content) {
        if (element.paragraph) {
          for (const elem of element.paragraph.elements || []) {
            if (elem.textRun && elem.textRun.content) {
              content += elem.textRun.content
            }
          }
        }
      }
    }

    return NextResponse.json({
      success: true,
      documentId,
      title: document.title || '제목 없음',
      content: content.trim(),
      url: `https://docs.google.com/document/d/${documentId}/edit`
    })

  } catch (error) {
    console.error('Google Docs 읽기 오류:', error)
    
    return NextResponse.json(
      { 
        error: 'Google Docs 문서를 읽을 수 없습니다.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 