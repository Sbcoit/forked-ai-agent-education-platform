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
    const setCookieHeader = response.headers.get('set-cookie')
    
    const data = await response.json()
    
    // Create NextResponse with the data
    const nextResponse = NextResponse.json(data, { status: response.status })
    
    // If backend set a cookie, forward it to the browser
    if (setCookieHeader) {
      // Parse the cookie and set it on the NextResponse
      nextResponse.headers.set('set-cookie', setCookieHeader)
    }
    
    return nextResponse
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: 'Failed to login' },
      { status: 500 }
    )
  }
}
