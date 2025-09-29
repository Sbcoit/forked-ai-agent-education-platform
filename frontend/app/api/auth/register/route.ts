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

    // Get the set-cookie header from backend response
    const setCookieHeader = response.headers.get('set-cookie')
    console.log('Register API route: Set-Cookie header:', setCookieHeader ? 'present' : 'missing')
    
    const data = await response.json()
    console.log('Register API route: Response data received')
    
    // Create NextResponse with the data
    const nextResponse = NextResponse.json(data, { status: response.status })
    
    // If backend set a cookie, forward it to the browser
    if (setCookieHeader) {
      // Parse the cookie and set it on the NextResponse
      nextResponse.headers.set('set-cookie', setCookieHeader)
    }
    
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
