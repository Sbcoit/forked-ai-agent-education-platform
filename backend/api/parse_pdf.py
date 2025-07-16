import os
import asyncio
import json
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
from dotenv import load_dotenv

load_dotenv()
print("[DEBUG] .env loaded in parse_pdf.py")
LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"[DEBUG] LLAMAPARSE_API_KEY loaded: {LLAMAPARSE_API_KEY[:6]}...{LLAMAPARSE_API_KEY[-4:] if LLAMAPARSE_API_KEY else None}")
print(f"[DEBUG] GEMINI_API_KEY loaded: {str(GEMINI_API_KEY)[:6]}...{str(GEMINI_API_KEY)[-4:] if GEMINI_API_KEY else None}")

router = APIRouter()

LLAMAPARSE_API_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
LLAMAPARSE_JOB_URL = "https://api.cloud.llamaindex.ai/api/parsing/job"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

@router.post("/api/parse-pdf/")
async def parse_pdf(file: UploadFile = File(...)):
    print("[DEBUG] /api/parse-pdf/ endpoint hit")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        contents = await file.read()
        headers = {"Authorization": f"Bearer {LLAMAPARSE_API_KEY}"}
        files = {"file": (file.filename, contents, file.content_type)}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Just upload and return job ID
            upload_response = await client.post(LLAMAPARSE_API_URL, headers=headers, files=files)
            upload_response.raise_for_status()
            job_data = upload_response.json()
            
            return {
                "job_id": job_data["id"],
                "status": job_data["status"],
                "message": "File uploaded successfully. Use job_id to check status."
            }
            
    except Exception as e:
        print("[ERROR]", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

@router.get("/api/parse-pdf/status/{job_id}")
async def get_parse_status(job_id: str):
    """Check the status of a LlamaParse job"""
    print(f"[DEBUG] Checking status for job: {job_id}")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    
    try:
        headers = {
            "Authorization": f"Bearer {LLAMAPARSE_API_KEY}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}", headers=headers)
        response.raise_for_status()
        job_data = response.json()
        print(f"[DEBUG] Job {job_id} current status: {job_data.get('status')}")
        return job_data
    except Exception as e:
        print(f"[ERROR] Failed to check job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check job status: {str(e)}")

@router.post("/api/parse-pdf/poll/{job_id}")
async def poll_parse_result(job_id: str, max_attempts: int = 60, delay_seconds: int = 3):
    """Poll for the parsed result until it's ready or max attempts reached"""
    print(f"[DEBUG] Polling for job: {job_id}")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    
    headers = {
        "Authorization": f"Bearer {LLAMAPARSE_API_KEY}",
    }
    
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}", headers=headers)
            response.raise_for_status()
            job_data = response.json()
            
            status = job_data.get("status")
            print(f"[DEBUG] Job {job_id} status: {status} (attempt {attempt + 1}/{max_attempts})")
            
            if status == "COMPLETED":
                # Get the parsed content
                parsed_content = job_data.get("parsed_document", {})
                print(f"[DEBUG] Job completed! Parsed content keys: {list(parsed_content.keys()) if parsed_content else 'None'}")
                return {
                    "status": "completed",
                    "job_id": job_id,
                    "parsed_content": parsed_content,
                    "attempts": attempt + 1
                }
            elif status == "FAILED":
                error_msg = job_data.get("error", "Unknown error")
                print(f"[DEBUG] Job failed: {error_msg}")
                return {
                    "status": "failed",
                    "job_id": job_id,
                    "error": error_msg,
                    "attempts": attempt + 1
                }
            elif status == "PENDING":
                print(f"[DEBUG] Job still pending, waiting {delay_seconds}s...")
                # Wait before next attempt
                await asyncio.sleep(delay_seconds)
                continue
            else:
                print(f"[DEBUG] Unknown status '{status}', waiting {delay_seconds}s...")
                # Unknown status
                await asyncio.sleep(delay_seconds)
                continue
                
        except Exception as e:
            print(f"[ERROR] Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise HTTPException(status_code=500, detail=f"Failed to poll job status: {str(e)}")
            await asyncio.sleep(delay_seconds)
    
    # Max attempts reached
    return {
        "status": "timeout",
        "job_id": job_id,
        "error": f"Job did not complete within {max_attempts * delay_seconds} seconds",
        "attempts": max_attempts
    }

@router.get("/api/parse-pdf/result/{job_id}")
async def get_parse_result(job_id: str):
    """Get the parsed result for a completed job"""
    print(f"[DEBUG] Getting result for job: {job_id}")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    
    try:
        headers = {"Authorization": f"Bearer {LLAMAPARSE_API_KEY}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First check if job is completed
            status_response = await client.get(
                f"{LLAMAPARSE_JOB_URL}/{job_id}",
                headers=headers
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            print(f"[DEBUG] Job status: {status_data}")
            
            if status_data.get("status") in ["COMPLETED", "SUCCESS"]:
                # Now get the actual parsed content using the result endpoint
                try:
                    result_response = await client.get(
                        f"{LLAMAPARSE_JOB_URL}/{job_id}/result",
                        headers=headers
                    )
                    result_response.raise_for_status()
                    parsed_content = result_response.json()
                    print(f"[DEBUG] Parsed content from result endpoint: {parsed_content}")
                    
                    # Extract text content for AI processing
                    text_content = ""
                    if isinstance(parsed_content, dict):
                        text_content = parsed_content.get("text", "") or parsed_content.get("content", "") or str(parsed_content)
                    elif isinstance(parsed_content, str):
                        text_content = parsed_content
                    else:
                        text_content = str(parsed_content)
                    
                    # Process with AI if we have content
                    ai_result = None
                    if text_content.strip():
                        ai_result = await process_with_ai(extract_markdown(parsed_content))
                    
                    return {
                        "status": "completed",
                        "job_id": job_id,
                        "parsed_content": parsed_content,
                        "ai_result": ai_result,
                        "full_response": status_data
                    }
                except Exception as result_error:
                    print(f"[ERROR] Failed to get result content: {str(result_error)}")
                    # Fallback: try markdown endpoint
                    try:
                        markdown_response = await client.get(
                            f"{LLAMAPARSE_JOB_URL}/{job_id}/result/markdown",
                            headers=headers
                        )
                        markdown_response.raise_for_status()
                        markdown_content = markdown_response.text
                        print(f"[DEBUG] Markdown content: {markdown_content[:200]}...")
                        
                        # Process markdown content with AI
                        ai_result = None
                        if markdown_content.strip():
                            ai_result = await process_with_ai(extract_markdown(markdown_content))
                        
                        return {
                            "status": "completed",
                            "job_id": job_id,
                            "parsed_content": {"text": markdown_content},
                            "ai_result": ai_result,
                            "full_response": status_data
                        }
                    except Exception as markdown_error:
                        print(f"[ERROR] Failed to get markdown content: {str(markdown_error)}")
                        # Fallback: re-run extraction from scratch using the markdown content we already have
                        try:
                            # Use the markdown content that was already extracted, not the status data
                            markdown_content = extract_markdown(status_data)
                            preprocessed = preprocess_case_study_content(markdown_content)
                            # Fallback description
                            content_lines = preprocessed['cleaned_content'].split('\n')
                            description_lines = []
                            for line in content_lines:
                                line = line.strip()
                                if not line:
                                    continue
                                normalized_line = ''.join(line.split())
                                if any(skip_pattern.replace(' ', '') in normalized_line.upper() for skip_pattern in [
                                    'HARVARD BUSINESS SCHOOL', 'REV:', 'PAGE', '©', 'COPYRIGHT', 'ALL RIGHTS RESERVED',
                                    'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', '9-', 'R E V :', 'PROFESSORS', 'PREPARED THIS CASE',
                                    'CERTAIN DETAILS', 'HBS CASES', 'DEVELOPED SOLELY', 'AUTHORIZED FOR USE', 'TEAMWORK', 'COLLABORATION',
                                    'INTERNATIONAL BUSINESS SCHOOL', 'HULT', 'MGT-', 'FMIB', 'THIS DOCUMENT', 'USE ONLY BY'
                                ]):
                                    continue
                                if line.startswith('#'):
                                    continue
                                if preprocessed["title"] and line.strip() == preprocessed["title"].strip():
                                    continue
                                if '|' in line:
                                    continue
                                if re.match(r'^[\s\-\_]+$', line):
                                    continue
                                if any(phrase in line.upper() for phrase in [
                                    'PROFESSORS', 'PREPARED THIS CASE', 'CERTAIN DETAILS', 'HBS CASES', 'DEVELOPED SOLELY',
                                    'AUTHORIZED FOR USE', 'TEAMWORK', 'COLLABORATION', 'INTERNATIONAL BUSINESS SCHOOL', 
                                    'HULT', 'MGT-', 'FMIB', 'THIS DOCUMENT', 'USE ONLY BY', 'JIMENEZ GUILLEN', 'LUIS AARON'
                                ]):
                                    continue
                                if re.match(r'^[\d\s\-\.]+$', line):
                                    continue
                                if len(line) < 10 or line.isupper():
                                    continue
                                if '&#x' in line or '&#' in line:
                                    continue
                                if len(line) > 30 and len(line) < 400:
                                    description_lines.append(line)
                                    if len(description_lines) >= 2:
                                        break
                            fallback_description = ' '.join(description_lines)
                            print(f'[DEBUG] Fallback description before length check: "{fallback_description}"')
                            if len(fallback_description) > 600:
                                fallback_description = fallback_description[:600] + "..."
                            if not fallback_description.strip():
                                fallback_description = "No background description could be extracted from the case study. Please review the document manually."
                                print('[DEBUG] Fallback: No description found, using generic fallback description.')
                            # Fallback learning outcomes
                            def extract_learning_outcomes_from_content(content: str):
                                import re
                                lines = content.split('\n')
                                outcomes = []
                                print('[DEBUG] Fallback: extracting learning outcomes from content...')
                                header_patterns = [
                                    r'learning outcomes', r'objectives', r'learning objectives', r'what you will learn', r'key takeaways', r'case objectives'
                                ]
                                header_idx = None
                                for i, line in enumerate(lines):
                                    for pat in header_patterns:
                                        if re.search(pat, line, re.IGNORECASE):
                                            header_idx = i
                                            print(f'[DEBUG] Found learning outcomes header: "{line}" at line {i}')
                                            break
                                    if header_idx is not None:
                                        break
                                bullet_regex = r'^(\d+\.|[\-\*•–]|[a-zA-Z]\))\s+'
                                if header_idx is not None:
                                    for line in lines[header_idx+1:]:
                                        l = line.strip()
                                        if re.match(bullet_regex, l):
                                            l = re.sub(bullet_regex, '', l)
                                            if l:
                                                outcomes.append(l)
                                        elif l == '' or l.lower().startswith('note'):
                                            continue
                                        else:
                                            if len(outcomes) >= 3:
                                                break
                                    print(f'[DEBUG] Extracted outcomes after header: {outcomes}')
                                    if 3 <= len(outcomes) <= 7:
                                        return [f"{i+1}. {o}" for i, o in enumerate(outcomes)]
                                outcomes = []
                                for i, line in enumerate(lines):
                                    l = line.strip()
                                    if re.match(bullet_regex, l):
                                        l = re.sub(bullet_regex, '', l)
                                        if l:
                                            outcomes.append(l)
                                    elif outcomes:
                                        if len(outcomes) >= 3:
                                            break
                                print(f'[DEBUG] Extracted outcomes from first list: {outcomes}')
                                if 3 <= len(outcomes) <= 7:
                                    return [f"{i+1}. {o}" for i, o in enumerate(outcomes)]
                                print('[DEBUG] No suitable learning outcomes found, using generic fallback.')
                                return [
                                    "1. Analyze the business situation presented in the case study",
                                    "2. Identify key stakeholders and their interests",
                                    "3. Develop strategic recommendations based on the analysis",
                                    "4. Evaluate the impact of decisions on organizational performance",
                                    "5. Apply business concepts and frameworks to real-world scenarios"
                                ]
                            fallback_learning_outcomes = extract_learning_outcomes_from_content(preprocessed['cleaned_content'])
                            fallback_title = preprocessed["title"] if preprocessed["title"].strip() else "Business Case Study"
                            if not fallback_title.strip():
                                fallback_title = "Business Case Study"
                                print('[DEBUG] Fallback: No title found, using generic fallback title.')
                            print(f'[DEBUG] Fallback title: "{fallback_title}"')
                            print(f'[DEBUG] Fallback description: "{fallback_description}"')
                            return {
                                "status": "completed",
                                "job_id": job_id,
                                "parsed_content": status_data,
                                "ai_result": {
                                    "title": fallback_title,
                                    "description": fallback_description,
                                    "learning_outcomes": fallback_learning_outcomes
                                },
                                "full_response": status_data
                            }
                        except Exception as fallback_error:
                            print(f"[ERROR] Fallback extraction failed: {str(fallback_error)}")
                            return {
                                "status": "completed",
                                "job_id": job_id,
                                "parsed_content": status_data,
                                "ai_result": {
                                    "title": "Business Case Study",
                                    "description": "No background description could be extracted from the case study. Please review the document manually.",
                                    "learning_outcomes": [
                                        "1. Analyze the business situation presented in the case study",
                                        "2. Identify key stakeholders and their interests",
                                        "3. Develop strategic recommendations based on the analysis",
                                        "4. Evaluate the impact of decisions on organizational performance",
                                        "5. Apply business concepts and frameworks to real-world scenarios"
                                    ]
                                },
                                "full_response": status_data
                            }
            else:
                current_status = status_data.get("status", "unknown")
                print(f"[DEBUG] Job {job_id} not completed. Current status: {current_status}")
                return {
                    "status": current_status,
                    "job_id": job_id,
                    "error": f"Job is not completed. Current status: {current_status}"
                }
            
    except Exception as e:
        print(f"[ERROR] Failed to get result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")

def preprocess_case_study_content(raw_content: str) -> dict:
    """Pre-process the parsed content to extract clean case study information"""
    print("[DEBUG] Pre-processing case study content")
    
    # If content is a dict with markdown, extract the markdown
    if isinstance(raw_content, dict) and "markdown" in raw_content:
        content = raw_content["markdown"]
    elif isinstance(raw_content, str):
        content = raw_content
    else:
        content = str(raw_content)
    
    print(f"[DEBUG] Raw content type: {type(raw_content)}")
    print(f"[DEBUG] Raw content preview: {content[:500]}...")
    
    # Clean up formatting artifacts (remove extra spaces, normalize)
    content = content.replace('  ', ' ')  # Remove double spaces
    content = content.replace(' \n', '\n')  # Remove trailing spaces
    content = content.replace('\n ', '\n')  # Remove leading spaces
    
    # Split into lines and process
    lines = content.split('\n')
    cleaned_lines = []
    title = None
    
    # First pass: extract title from markdown headers
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip metadata lines - expanded list
        if any(skip_pattern in line.upper() for skip_pattern in [
            'HARVARD BUSINESS SCHOOL', 'REV:', 'PAGE', '©', 'COPYRIGHT', 'ALL RIGHTS RESERVED',
            'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', '9-', 'R E V :', 'AUTHORIZED FOR USE',
            'TEAMWORK', 'COLLABORATION', 'INTERNATIONAL BUSINESS SCHOOL', 'HULT', 'MGT-', 'FMIB'
        ]):
            continue
            
        # Look for markdown headers (e.g., "# Title")
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            print(f"[DEBUG] Found title in markdown header: {title}")
            break
    
    # If no title found in headers, look for the first meaningful line
    if not title:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip metadata and formatting artifacts
            if any(skip_pattern in line.upper() for skip_pattern in [
                'HARVARD BUSINESS SCHOOL', 'REV:', 'PAGE', '©', 'COPYRIGHT', 'ALL RIGHTS RESERVED',
                'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', '9-', 'R E V :'
            ]):
                continue
                
            # Skip lines that are just numbers, dates, or formatting
            if re.match(r'^[\d\s\-\.]+$', line):  # Just numbers, spaces, dashes, dots
                continue
                
            # Skip very short lines or all-uppercase lines
            if len(line) < 5 or line.isupper():
                continue
                
            # This looks like a title
            title = line
            print(f"[DEBUG] Found title in content: {title}")
            break
    
    # Fallback title
    if not title:
        title = "Business Case Study"

    # Clean content (remove metadata and formatting artifacts)
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Normalize line for better metadata matching (remove ALL spaces for comparison)
        normalized_line = ''.join(line.split())
        
        # Skip metadata lines - expanded list
        if any(skip_pattern.replace(' ', '') in normalized_line.upper() for skip_pattern in [
            'HARVARD BUSINESS SCHOOL', 'REV:', 'PAGE', '©', 'COPYRIGHT', 'ALL RIGHTS RESERVED',
            'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', '9-', 'R E V :', 'PROFESSORS', 'PREPARED THIS CASE',
            'CERTAIN DETAILS', 'HBS CASES', 'DEVELOPED SOLELY', 'AUTHORIZED FOR USE', 'TEAMWORK', 'COLLABORATION',
            'INTERNATIONAL BUSINESS SCHOOL', 'HULT', 'MGT-', 'FMIB', 'THIS DOCUMENT', 'USE ONLY BY'
        ]):
            continue
            
        # Skip lines that contain case study metadata - expanded list
        if any(phrase in line.upper() for phrase in [
            'PROFESSORS', 'PREPARED THIS CASE', 'CERTAIN DETAILS', 'HBS CASES', 'DEVELOPED SOLELY',
            'AUTHORIZED FOR USE', 'TEAMWORK', 'COLLABORATION', 'INTERNATIONAL BUSINESS SCHOOL', 
            'HULT', 'MGT-', 'FMIB', 'THIS DOCUMENT', 'USE ONLY BY', 'JIMENEZ GUILLEN', 'LUIS AARON'
        ]):
            continue
            
        # Skip lines that contain HTML entities or special characters
        if '&#x' in line or '&#' in line:
            continue
            
        # Skip lines that are just formatting artifacts
        if re.match(r'^[\d\s\-\.]+$', line):
            continue
            
        # Skip markdown headers (lines starting with #)
        if line.startswith('#'):
            continue
            
        # Skip lines that are just the title repeated
        if title and line.strip() == title.strip():
            continue
            
        # Skip table formatting (lines with | characters)
        if '|' in line:
            continue
            
        # Skip lines that are just formatting or metadata
        if re.match(r'^[\s\-\_]+$', line):  # Just dashes, underscores, spaces
            continue
            
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    print(f"[DEBUG] Extracted title: {title}")
    print(f"[DEBUG] Cleaned content length: {len(cleaned_content)}")
    print(f"[DEBUG] Cleaned content preview: {cleaned_content[:300]}...")
    
    return {
        "title": title,
        "cleaned_content": cleaned_content
    }

async def process_with_ai(parsed_content: str) -> dict:
    """Process the parsed PDF content with Gemini AI to extract business case study information"""
    print("[DEBUG] Processing content with Gemini AI")
    try:
        # Pre-process the content
        preprocessed = preprocess_case_study_content(parsed_content)
        title = preprocessed["title"]
        cleaned_content = preprocessed["cleaned_content"]
        # Prepare the prompt for business case study analysis
        prompt = f"""
You are an expert business case study analyst specializing in business education. Analyze the following business case study content and extract key information for college business students.

BUSINESS CASE STUDY CONTENT:
{cleaned_content}

Please provide a JSON response with the following structure:
{{
  "title": "(The actual name of the business case study, not a generic phrase)",
  "description": "A comprehensive, non-empty background description (2-3 paragraphs) that includes: 1) The business context and situation, 2) Key players and stakeholders involved, 3) The specific role/position the student will assume in this case study (e.g., 'As a consultant to...', 'As the manager of...', 'As a strategic advisor to...'), 4) The main challenges or decisions to be made.",
  "learning_outcomes": [
    "1. [Specific, actionable learning outcome that students can demonstrate]",
    "2. [Specific, actionable learning outcome that students can demonstrate]",
    "3. [Specific, actionable learning outcome that students can demonstrate]",
    "4. [Specific, actionable learning outcome that students can demonstrate]",
    "5. [Specific, actionable learning outcome that students can demonstrate]"
  ]
}}

Guidelines:
- Title: Use the actual case study name (from the content), not a generic phrase. If not found, summarize the main topic in 10 words or less.
- Description: Write 2-3 paragraphs that clearly establish the business context, introduce key players, and specify the student's role in the case study. This field must NOT be empty.
- Learning Outcomes: Create 5 specific, measurable learning objectives that business students should achieve. Each outcome should be different and specific to the case study content.
- If any field is missing or unclear, infer or summarize based on the content. Do NOT leave any field empty.
- Return ONLY the JSON response, no additional text or explanations.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            print(f"[DEBUG] Gemini API response status: {response.status_code}")
            print(f"[DEBUG] Gemini API response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"[DEBUG] Gemini API response: {result}")
            # Extract the generated text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[DEBUG] Generated text: {generated_text}")
                # Parse the JSON response
                try:
                    ai_result = json.loads(generated_text)
                    print(f"[DEBUG] Parsed AI result: {ai_result}")
                    # Validate and fill missing fields
                    final_result = {}
                    final_result["title"] = ai_result.get("title") or title
                    final_result["description"] = ai_result.get("description") or (cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content)
                    final_result["learning_outcomes"] = ai_result.get("learning_outcomes") or [
                        "1. Analyze the business situation presented in the case study",
                        "2. Identify key stakeholders and their interests",
                        "3. Develop strategic recommendations based on the analysis",
                        "4. Evaluate the impact of decisions on organizational performance",
                        "5. Apply business concepts and frameworks to real-world scenarios"
                    ]
                    print(f"[DEBUG] Final AI result sent to frontend: {final_result}")
                    return final_result
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse JSON from AI response: {e}")
                    print(f"[ERROR] Raw AI response: {generated_text}")
                    # Fallback: return structured content
                    return {
                        "title": title,
                        "description": cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content,
                        "learning_outcomes": [
                            "1. Analyze the business situation presented in the case study",
                            "2. Identify key stakeholders and their interests",
                            "3. Develop strategic recommendations based on the analysis",
                            "4. Evaluate the impact of decisions on organizational performance",
                            "5. Apply business concepts and frameworks to real-world scenarios"
                        ]
                    }
            else:
                raise Exception("No content generated by Gemini API")
                
    except Exception as e:
        print(f"[ERROR] AI processing failed: {str(e)}")
        # Fallback: return basic structured content
        preprocessed = preprocess_case_study_content(parsed_content)
        
        # --- Fallback: try to extract learning outcomes from content ---
        def extract_learning_outcomes_from_content(content: str):
            import re
            lines = content.split('\n')
            outcomes = []
            print('[DEBUG] Fallback: extracting learning outcomes from content...')
            # 1. Look for a section header
            header_patterns = [
                r'learning outcomes', r'objectives', r'learning objectives', r'what you will learn', r'key takeaways', r'case objectives'
            ]
            header_idx = None
            for i, line in enumerate(lines):
                for pat in header_patterns:
                    if re.search(pat, line, re.IGNORECASE):
                        header_idx = i
                        print(f'[DEBUG] Found learning outcomes header: "{line}" at line {i}')
                        break
                if header_idx is not None:
                    break
            # 2. If found, extract next 3-7 bullet/numbered items
            bullet_regex = r'^(\d+\.|[\-\*•–]|[a-zA-Z]\))\s+'
            if header_idx is not None:
                for line in lines[header_idx+1:]:
                    l = line.strip()
                    if re.match(bullet_regex, l):
                        # Remove leading number/bullet
                        l = re.sub(bullet_regex, '', l)
                        if l:
                            outcomes.append(l)
                    elif l == '' or l.lower().startswith('note'):
                        continue
                    else:
                        # Stop if we hit a non-list line after at least 3 outcomes
                        if len(outcomes) >= 3:
                            break
                print(f'[DEBUG] Extracted outcomes after header: {outcomes}')
                if 3 <= len(outcomes) <= 7:
                    return [f"{i+1}. {o}" for i, o in enumerate(outcomes)]
            # 3. If not found, look for first numbered/bulleted list in content
            outcomes = []
            for i, line in enumerate(lines):
                l = line.strip()
                if re.match(bullet_regex, l):
                    l = re.sub(bullet_regex, '', l)
                    if l:
                        outcomes.append(l)
                elif outcomes:
                    # Stop at first break in list
                    if len(outcomes) >= 3:
                        break
            print(f'[DEBUG] Extracted outcomes from first list: {outcomes}')
            if 3 <= len(outcomes) <= 7:
                return [f"{i+1}. {o}" for i, o in enumerate(outcomes)]
            # 4. Fallback to generic
            print('[DEBUG] No suitable learning outcomes found, using generic fallback.')
            return [
                "1. Analyze the business situation presented in the case study",
                "2. Identify key stakeholders and their interests",
                "3. Develop strategic recommendations based on the analysis",
                "4. Evaluate the impact of decisions on organizational performance",
                "5. Apply business concepts and frameworks to real-world scenarios"
            ]

        # --- existing fallback description logic ---
        fallback_description = ' '.join(description_lines)
        print(f'[DEBUG] Fallback description before length check: "{fallback_description}"')
        if len(fallback_description) > 600:
            fallback_description = fallback_description[:600] + "..."
        if not fallback_description.strip():
            fallback_description = "No background description could be extracted from the case study. Please review the document manually."
            print('[DEBUG] Fallback: No description found, using generic fallback description.')
        fallback_learning_outcomes = extract_learning_outcomes_from_content(preprocessed['cleaned_content'])
        fallback_title = preprocessed["title"] if preprocessed["title"].strip() else "Business Case Study"
        if not fallback_title.strip():
            fallback_title = "Business Case Study"
            print('[DEBUG] Fallback: No title found, using generic fallback title.')
        print(f'[DEBUG] Fallback title: "{fallback_title}"')
        print(f'[DEBUG] Fallback description: "{fallback_description}"')
        return {
            "title": fallback_title,
            "description": fallback_description,
            "learning_outcomes": fallback_learning_outcomes
        } 

def extract_markdown(parsed_content):
    """Extract markdown text from LlamaParse result, whether dict or JSON string."""
    if isinstance(parsed_content, dict):
        if 'markdown' in parsed_content:
            return parsed_content['markdown']
        if 'text' in parsed_content:
            return parsed_content['text']
    if isinstance(parsed_content, str):
        # Try to parse as JSON
        try:
            import json
            obj = json.loads(parsed_content)
            if isinstance(obj, dict) and 'markdown' in obj:
                return obj['markdown']
            if isinstance(obj, dict) and 'text' in obj:
                return obj['text']
        except Exception:
            pass
        return parsed_content
    return str(parsed_content) 