import { NextRequest, NextResponse } from 'next/server'

/**
 * API Proxy Route - Forwards all authenticated requests to backend
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params
  return proxyRequest(request, resolvedParams.path, 'GET')
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params
  return proxyRequest(request, resolvedParams.path, 'POST')
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params
  return proxyRequest(request, resolvedParams.path, 'PUT')
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params
  return proxyRequest(request, resolvedParams.path, 'DELETE')
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params
  return proxyRequest(request, resolvedParams.path, 'PATCH')
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  try {
    // Reconstruct the full path - preserve trailing slash if present in original URL
    const path = pathSegments.join('/')
    const originalPath = request.nextUrl.pathname.replace('/api/proxy/', '')
    const hasTrailingSlash = originalPath.endsWith('/') && originalPath !== '/'
    const pathWithSlash = hasTrailingSlash && !path.endsWith('/') ? `${path}/` : path
    
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/${pathWithSlash}`
    
    // Get search params from the original request
    const searchParams = request.nextUrl.searchParams.toString()
    const fullUrl = searchParams ? `${backendUrl}?${searchParams}` : backendUrl
    
    // Prepare headers
    const headers: Record<string, string> = {}
    
    // Copy Content-Type from original request if present
    const originalContentType = request.headers.get('content-type')
    if (originalContentType) {
      headers['Content-Type'] = originalContentType
    } else if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
      // Default to JSON for mutation requests without explicit content type
      headers['Content-Type'] = 'application/json'
    }
    
    // Get cookies from the incoming request
    const cookies = request.cookies.getAll()
    if (cookies.length > 0) {
      headers['Cookie'] = cookies.map(c => `${c.name}=${c.value}`).join('; ')
    }
    
    // Forward Authorization header if present
    const authorization = request.headers.get('authorization')
    if (authorization) {
      headers['Authorization'] = authorization
    }
    
    // Forward other important headers
    const userAgent = request.headers.get('user-agent')
    if (userAgent) {
      headers['User-Agent'] = userAgent
    }
    
    const accept = request.headers.get('accept')
    if (accept) {
      headers['Accept'] = accept
    }
    
    const acceptLanguage = request.headers.get('accept-language')
    if (acceptLanguage) {
      headers['Accept-Language'] = acceptLanguage
    }
    
    // Debug: Log headers being forwarded
    console.log('🔍 Proxy forwarding headers:', Object.keys(headers))
    console.log('🔍 Proxy forwarding cookies:', cookies.length > 0 ? 'Yes' : 'No')
    
    // Prepare fetch options
    const fetchOptions: RequestInit = {
      method,
      headers,
    }
    
    // Include body for POST, PUT, PATCH requests
    if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
      try {
        const body = await request.text()
        if (body) {
          fetchOptions.body = body
        }
      } catch (e) {
        // No body or invalid body, continue without it
      }
    }
    
    // Make the request to the backend
    console.log('🚀 Proxy making request to:', fullUrl)
    console.log('🚀 Proxy request headers:', headers)
    let response = await fetch(fullUrl, fetchOptions)

    // If backend indicates method not allowed, retry once with a trailing slash
    // This helps when backend routes are defined with trailing slashes only
    if (response.status === 405 && !fullUrl.endsWith('/')) {
      try {
        const retryUrl = `${fullUrl}/`
        response = await fetch(retryUrl, fetchOptions)
      } catch (_) {
        // Ignore retry failure; original response will be handled below
      }
    }

    // Log 500 errors for debugging
    if (response.status === 500) {
      console.error(`Backend 500 error for ${method} ${fullUrl}`)
      const errorText = await response.text()
      console.error(`Backend error response:`, errorText)
    }
    
    // Get response data
    const contentType = response.headers.get('content-type')
    let nextResponse: NextResponse
    
    if (contentType?.includes('application/json')) {
      // Read as text first to avoid consuming the stream
      const text = await response.text()
      try {
        const data = JSON.parse(text)
        nextResponse = NextResponse.json(data, { status: response.status })
      } catch (e) {
        // Invalid JSON, return as text (text variable already has the body)
        nextResponse = new NextResponse(text, { 
          status: response.status,
          headers: { 'Content-Type': 'text/plain' }
        })
      }
    } else {
      // Non-JSON response (text, HTML, etc.)
      const text = await response.text()
      nextResponse = new NextResponse(text, { 
        status: response.status,
        headers: { 'Content-Type': contentType || 'text/plain' }
      })
    }
    
    // Forward all Set-Cookie headers from backend to browser
    const setCookieHeaders = response.headers.getSetCookie?.() || []
    setCookieHeaders.forEach(cookie => {
      nextResponse.headers.append('Set-Cookie', cookie)
    })
    
    // Forward other important headers
    const headersToForward = ['cache-control', 'etag']
    headersToForward.forEach(headerName => {
      const value = response.headers.get(headerName)
      if (value) {
        nextResponse.headers.set(headerName, value)
      }
    })
    
    return nextResponse
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { 
        error: 'Proxy request failed',
        details: error instanceof Error ? error.message : String(error),
        method,
        path: pathSegments.join('/')
      },
      { status: 500 }
    )
  }
}