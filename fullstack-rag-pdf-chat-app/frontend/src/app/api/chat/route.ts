import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Forward the request to the backend
    const isProd = process.env.NODE_ENV === 'production'
    const origin = request.nextUrl.origin
    const targetUrl = isProd ? `${origin}/backend/chat` : 'http://127.0.0.1:8000/api/chat'

    const backendResponse = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}))
      throw new Error(`Backend responded with status: ${backendResponse.status}, detail: ${errorData.detail || 'Unknown error'}`)
    }

    const reader = backendResponse.body?.getReader()
    if (!reader) throw new Error('No reader available from backend')

    const stream = new ReadableStream({
      async start(controller) {
        const decoder = new TextDecoder()
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break
            controller.enqueue(decoder.decode(value))
          }
        } catch (error) {
          controller.error(error)
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error: unknown) {
    console.error('Error proxying chat request:', error)
    return NextResponse.json({ detail: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
  }
}
