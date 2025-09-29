import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log('Register API route: Received body:', body)
    
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/register`
    console.log('Register API route: Calling backend at:', backendUrl)
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    console.log('Register API route: Backend response status:', response.status)
    
    const data = await response.json()
    console.log('Register API route: Response data received')
    
    // Create NextResponse with the data
    const nextResponse = NextResponse.json(data, { status: response.status })
    
    // Forward all Set-Cookie headers from backend to browser
    const setCookieHeaders = response.headers.getSetCookie?.() || []
    console.log('Register API route: Set-Cookie headers count:', setCookieHeaders.length)
    setCookieHeaders.forEach(cookie => {
      nextResponse.headers.append('Set-Cookie', cookie)
    })
    
    return nextResponse
  } catch (error) {
    console.error('Registration error - Full details:', error)
    console.error('Error type:', error instanceof Error ? error.constructor.name : typeof error)
    console.error('Error message:', error instanceof Error ? error.message : String(error))
    return NextResponse.json(
      { error: 'Failed to register user', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
