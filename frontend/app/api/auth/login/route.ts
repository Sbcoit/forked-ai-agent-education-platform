import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    // Get the set-cookie header from backend response
    // Get all Set-Cookie headers using getSetCookie() with fallback
    const setCookieHeaders = 
      (response.headers as unknown as { getSetCookie?: () => string[] }).getSetCookie?.() ??
      (response.headers.get('set-cookie') ? [response.headers.get('set-cookie') as string] : [])
    
    const data = await response.json()
    
    // Forward all Set-Cookie headers from backend to browser
    const nextResponse = NextResponse.json(data, { status: response.status })
    
    // If backend set a cookie, forward it to the browser
    // Forward all cookies to the client
    for (const cookie of setCookieHeaders) {
      nextResponse.headers.append('set-cookie', cookie)
    }
    
    return nextResponse
      { error: 'Failed to login' },
      { status: 500 }
    )
  }
}
