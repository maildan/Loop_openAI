import { NextRequest, NextResponse } from 'next/server'
import { google } from 'googleapis'

export async function POST(request: NextRequest) {
  try {
    const { title, content } = await request.json()

    if (!title || !content) {
      return NextResponse.json(
        { error: '제목과 내용이 필요합니다.' },
        { status: 400 }
      )
    }

    // OAuth2 클라이언트 설정
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      'http://localhost:3000' // 리다이렉트 URI (사용하지 않음)
    )

    // 액세스 토큰 설정
    oauth2Client.setCredentials({
      access_token: process.env.GOOGLE_ACCESS_TOKEN,
      refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
    })

    const docs = google.docs({ version: 'v1', auth: oauth2Client })
    const drive = google.drive({ version: 'v3', auth: oauth2Client })

    // 1. 새 문서 생성
    const createResponse = await docs.documents.create({
      requestBody: {
        title: title,
      },
    })

    const documentId = createResponse.data.documentId
    if (!documentId) {
      throw new Error('문서 ID를 가져올 수 없습니다.')
    }

    // 2. 문서에 내용 추가
    await docs.documents.batchUpdate({
      documentId: documentId,
      requestBody: {
        requests: [
          {
            insertText: {
              location: {
                index: 1,
              },
              text: content,
            },
          },
        ],
      },
    })

    // 3. 문서를 공개로 설정
    await drive.permissions.create({
      fileId: documentId,
      requestBody: {
        role: 'reader',
        type: 'anyone',
      },
    })

    const documentUrl = `https://docs.google.com/document/d/${documentId}/edit`

    return NextResponse.json({
      success: true,
      documentId,
      url: documentUrl,
      title,
    })

  } catch (error) {
    console.error('Google Docs 생성 오류:', error)
    
    return NextResponse.json(
      { 
        error: 'Google Docs 문서 생성에 실패했습니다.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 