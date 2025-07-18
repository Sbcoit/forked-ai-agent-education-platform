import os
import asyncio
import json
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import httpx
from dotenv import load_dotenv
import openai
from typing import List
from PyPDF2 import PdfReader
import time

# Explicitly load the .env file from the backend directory (parent of api)
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(backend_env_path)
print(f"[DEBUG] Loading .env from: {backend_env_path}")

LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if LLAMAPARSE_API_KEY:
    print(f"[DEBUG] LLAMAPARSE_API_KEY loaded: {LLAMAPARSE_API_KEY[:6]}...{LLAMAPARSE_API_KEY[-4:]}")
else:
    print("[DEBUG] LLAMAPARSE_API_KEY loaded: None")
if OPENAI_API_KEY:
    print(f"[DEBUG] OPENAI_API_KEY loaded: {OPENAI_API_KEY[:6]}...{OPENAI_API_KEY[-4:]}")
else:
    print("[DEBUG] OPENAI_API_KEY loaded: None")

router = APIRouter()

LLAMAPARSE_API_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
LLAMAPARSE_JOB_URL = "https://api.cloud.llamaindex.ai/api/parsing/job"

async def extract_text_from_context_files(context_files: List[UploadFile]) -> str:
    context_texts = []
    for file in context_files:
        filename = file.filename.lower()
        contents = await file.read()
        if filename.endswith('.pdf'):
            try:
                import io
                reader = PdfReader(io.BytesIO(contents))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                context_texts.append(f"[Context File: {file.filename}]\n{text.strip()}\n")
            except Exception as e:
                context_texts.append(f"[Context File: {file.filename}]\n[Could not extract PDF text: {e}]\n")
        elif filename.endswith('.txt'):
            try:
                text = contents.decode('utf-8', errors='ignore')
                context_texts.append(f"[Context File: {file.filename}]\n{text.strip()}\n")
            except Exception as e:
                context_texts.append(f"[Context File: {file.filename}]\n[Could not extract TXT text: {e}]\n")
        else:
            context_texts.append(f"[Context File: {file.filename}]\n[Unsupported file type]\n")
    return "\n".join(context_texts)

async def parse_with_llamaparse(file: UploadFile) -> str:
    """Send a file to LlamaParse and return the parsed markdown content."""
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    
    try:
        # Read file contents once and store them
        contents = await file.read()
        headers = {"Authorization": f"Bearer {LLAMAPARSE_API_KEY}"}
        files = {"file": (file.filename, contents, file.content_type)}
        
        print(f"[DEBUG] Sending {file.filename} to LlamaParse...")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            upload_response = await client.post(LLAMAPARSE_API_URL, headers=headers, files=files)
            upload_response.raise_for_status()
            
            job_data = upload_response.json()
            print(f"[DEBUG] LlamaParse upload response: {job_data}")
            print(f"[DEBUG] Response type: {type(job_data)}")
            print(f"[DEBUG] Response keys: {list(job_data.keys()) if isinstance(job_data, dict) else 'Not a dict'}")
            
            if not job_data:
                print(f"[ERROR] Empty response from LlamaParse")
                raise HTTPException(status_code=500, detail="Empty response from LlamaParse")
            
            if not isinstance(job_data, dict):
                print(f"[ERROR] Invalid response type from LlamaParse: {type(job_data)}")
                raise HTTPException(status_code=500, detail=f"Invalid response type from LlamaParse: {type(job_data)}")
            
            # Check for different possible job ID fields
            job_id = None
            if "id" in job_data:
                job_id = job_data["id"]
            elif "job_id" in job_data:
                job_id = job_data["job_id"]
            elif "jobId" in job_data:
                job_id = job_data["jobId"]
            
            if not job_id:
                print(f"[ERROR] No job ID in LlamaParse response. Got keys: {list(job_data.keys())}")
                raise HTTPException(status_code=500, detail=f"No job ID in LlamaParse response. Got keys: {list(job_data.keys())}")
            
            if not job_id:
                print(f"[ERROR] Empty job ID received from LlamaParse")
                raise HTTPException(status_code=500, detail="Empty job ID received from LlamaParse")
            
            print(f"[DEBUG] Got job ID: {job_id}")
            
            # Poll for completion
            for attempt in range(60):
                print(f"[DEBUG] Polling attempt {attempt + 1}/60 for job {job_id}")
                status_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}", headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                print(f"[DEBUG] Status response: {status_data}")
                
                status = status_data.get("status")
                if status in ["COMPLETED", "SUCCESS"]:
                    print(f"[DEBUG] Job {job_id} completed, retrieving result...")
                    # Try to get markdown result
                    try:
                        markdown_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}/result/markdown", headers=headers)
                        markdown_response.raise_for_status()
                        result = markdown_response.text
                        print(f"[DEBUG] Retrieved markdown result, length: {len(result)}")
                        return result
                    except Exception as e:
                        print(f"[DEBUG] Markdown retrieval failed: {e}")
                        pass
                    
                    # Fallback: try text
                    try:
                        result_response = await client.get(f"{LLAMAPARSE_JOB_URL}/{job_id}/result", headers=headers)
                        result_response.raise_for_status()
                        parsed_content = result_response.json()
                        result = parsed_content.get("text", "")
                        print(f"[DEBUG] Retrieved text result, length: {len(result)}")
                        return result
                    except Exception as e:
                        print(f"[DEBUG] Text retrieval failed: {e}")
                        pass
                    
                    # Final fallback: check if result is in status_data
                    if "parsed_document" in status_data:
                        parsed_doc = status_data["parsed_document"]
                        if isinstance(parsed_doc, dict) and "text" in parsed_doc:
                            result = parsed_doc["text"]
                            print(f"[DEBUG] Retrieved result from status_data, length: {len(result)}")
                            return result
                    
                    print(f"[DEBUG] No result found in any format")
                    return ""
                    
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"[DEBUG] Job {job_id} failed: {error_msg}")
                    raise HTTPException(status_code=500, detail=f"LlamaParse job failed for {file.filename}: {error_msg}")
                elif status in ["PENDING", "PROCESSING"]:
                    print(f"[DEBUG] Job {job_id} still {status}, waiting 3s...")
                    await asyncio.sleep(3)
                else:
                    print(f"[DEBUG] Unknown status '{status}', waiting 3s...")
                    await asyncio.sleep(3)
            
            raise HTTPException(status_code=500, detail=f"LlamaParse job timed out for {file.filename}")
    
    except Exception as e:
        print(f"[ERROR] Exception in parse_with_llamaparse for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse {file.filename}: {str(e)}")

@router.post("/api/parse-pdf/")
async def parse_pdf(file: UploadFile = File(...), context_files: List[UploadFile] = File(default=[])):
    print("[DEBUG] /api/parse-pdf/ endpoint hit")
    if not LLAMAPARSE_API_KEY:
        raise HTTPException(status_code=500, detail="LlamaParse API key not configured.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Parse main PDF with LlamaParse
        print("[DEBUG] Processing main PDF file...")
        main_markdown = await parse_with_llamaparse(file)
        print(f"[DEBUG] Main PDF processed successfully, content length: {len(main_markdown)}")
        
        # Parse all context files with LlamaParse (with delays between each)
        context_markdowns = []
        for i, ctx_file in enumerate(context_files):
            print(f"[DEBUG] Processing context file {i+1}/{len(context_files)}: {ctx_file.filename}")
            
            # Add delay between files to avoid overwhelming the API
            if i > 0:  # Don't delay before the first file
                print(f"[DEBUG] Waiting 5 seconds before processing next file...")
                await asyncio.sleep(5)
            
            try:
                ctx_markdown = await parse_with_llamaparse(ctx_file)
                context_markdowns.append(f"[Context File: {ctx_file.filename}]\n{ctx_markdown.strip()}\n")
                print(f"[DEBUG] Successfully processed context file: {ctx_file.filename}")
            except Exception as e:
                print(f"[ERROR] Failed to process context file {ctx_file.filename}: {e}")
                context_markdowns.append(f"[Context File: {ctx_file.filename}]\n[Could not extract context: {e}]\n")
        
        context_text = "\n".join(context_markdowns)
        print(f"[DEBUG] All files processed. Main content length: {len(main_markdown)}, Context content length: {len(context_text)}")
        
        # Pass both to process_with_ai
        print("[DEBUG] Calling process_with_ai...")
        ai_result = await process_with_ai(main_markdown, context_text)
        print("[DEBUG] AI processing completed successfully")
        return {"status": "completed", "ai_result": ai_result}
        
    except Exception as e:
        print(f"[ERROR] Exception in parse_pdf endpoint: {str(e)}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
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
                        # Get context files from the request
                        context_files = Request.state.context_files if hasattr(Request.state, 'context_files') else []
                        context_text = await extract_text_from_context_files(context_files)
                        ai_result = await process_with_ai(extract_markdown(parsed_content), context_text)
                    
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
                        context_files = Request.state.context_files if hasattr(Request.state, 'context_files') else []
                        context_text = await extract_text_from_context_files(context_files)
                        ai_result = None
                        if markdown_content.strip():
                            ai_result = await process_with_ai(extract_markdown(markdown_content), context_text)
                        
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
        # Check if it's a JSON string with markdown
        try:
            import json
            parsed_json = json.loads(raw_content)
            if isinstance(parsed_json, dict) and "markdown" in parsed_json:
                content = parsed_json["markdown"]
            else:
                content = raw_content
        except (json.JSONDecodeError, TypeError):
            content = raw_content
    else:
        content = str(raw_content)
    
    print(f"[DEBUG] Raw content type: {type(raw_content)}")
    print(f"[DEBUG] Raw content length: {len(content)}")
    print(f"[DEBUG] Raw content preview: {content[:500]}...")
    
    # Clean up formatting artifacts (remove extra spaces, normalize)
    content = content.replace('  ', ' ')  # Remove double spaces
    content = content.replace(' \n', '\n')  # Remove trailing spaces
    content = content.replace('\n ', '\n')  # Remove leading spaces
    
    # Split into lines and process
    lines = content.split('\n')
    print(f"[DEBUG] Number of lines in content: {len(lines)}")
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

    # Clean content (be very permissive - only remove obvious metadata)
    print(f"[DEBUG] Starting content cleaning. Total lines: {len(lines)}")
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Skip only the most obvious metadata lines
        if any(skip_pattern in line.upper() for skip_pattern in [
            'COPYRIGHT ENCODED', 'DOCUMENT ID:', 'FILE:', 'CREATED:', 'MODIFIED:', 
            'AUTHORIZED FOR USE ONLY', 'THIS DOCUMENT IS FOR USE ONLY BY'
        ]):
            print(f"[DEBUG] Skipping metadata line {i}: {line[:50]}...")
            continue
            
        # Skip lines that are just formatting artifacts (very short or just symbols)
        if len(line) < 2 or re.match(r'^[\s\-\_\.]+$', line):
            print(f"[DEBUG] Skipping formatting line {i}: {line[:50]}...")
            continue
            
        # Keep everything else - let the AI decide what's important
        cleaned_lines.append(line)
        if len(cleaned_lines) <= 5:  # Show first few kept lines
            print(f"[DEBUG] Keeping line {i}: {line[:50]}...")
    
    print(f"[DEBUG] Content cleaning complete. Kept {len(cleaned_lines)} lines out of {len(lines)}")
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    print(f"[DEBUG] Extracted title: {title}")
    print(f"[DEBUG] Cleaned content length: {len(cleaned_content)}")
    print(f"[DEBUG] Cleaned content preview: {cleaned_content[:300]}...")
    
    return {
        "title": title,
        "cleaned_content": cleaned_content
    }

async def process_with_ai(parsed_content: str, context_text: str = "") -> dict:
    """Process the parsed PDF content with OpenAI to extract business case study information (using openai>=1.0.0)"""
    print("[DEBUG] Processing content with OpenAI LLM (new API)")
    try:
        preprocessed = preprocess_case_study_content(parsed_content)
        title = preprocessed["title"]
        cleaned_content = preprocessed["cleaned_content"]
        # Prepend context files' content as most important
        if context_text.strip():
            combined_content = f"""
IMPORTANT CONTEXT FILES (most authoritative, follow these first):
{context_text}

CASE STUDY CONTENT (main PDF):
{cleaned_content}
"""
        else:
            combined_content = cleaned_content
        prompt = f"""
You are a highly structured JSON-only generator trained to analyze business case studies for college business education.

Your task is to analyze the following business case study content and return a JSON object with exactly the following fields:

{{
  "title": "<The exact title of the business case study>",
  "description": "<A minimum 300-word, 3-paragraph detailed background including: 1) business context and situation, 2) main challenges or decisions, 3) the specific role or position the student will assume in the case, and 4) explicit reference to the key figures and their roles/correlations as part of the narrative>",
  "student_role": "<The specific role or position the student will assume in this case study (e.g., 'CEO', 'Marketing Manager', 'Consultant', etc.)>",
  "key_figures": [
    {{
      "name": "<Full name of figure, or descriptive title if unnamed (e.g., 'The Board of Directors', 'Competitor CEO', 'Industry Analyst')>",
      "role": "<Their role or inferred role. If unknown, use 'Unknown'>",
      "correlation": "<A brief explanation of this figure's relationship to the narrative of the case study>",
      "background": "<A 2-3 sentence background/bio of this person/entity based on the case study content>",
      "primary_goals": [
        "<Goal 1>",
        "<Goal 2>",
        "<Goal 3>"
      ],
      "personality_traits": {{
        "analytical": <0-10 rating>,
        "creative": <0-10 rating>,
        "assertive": <0-10 rating>,
        "collaborative": <0-10 rating>,
        "detail_oriented": <0-10 rating>
      }}
    }}
  ],
  "learning_outcomes": [
    "1. <Outcome 1>",
    "2. <Outcome 2>",
    "3. <Outcome 3>",
    "4. <Outcome 4>",
    "5. <Outcome 5>"
  ]
}}

Important generation rules:
- Output ONLY a valid JSON object. Do not include any extra commentary, markdown, or formatting.
- The "description" must be at least 300 words, written in textbook-quality paragraphs, and must explicitly reference the key figures and their roles/correlations as part of the narrative. Do not summarize.
- The "student_role" field should clearly identify the position the student will assume in the case study.
- The "key_figures" array must list **EVERY SINGLE important figure, entity, group, or organization** mentioned in the case study that is essential to understanding and progressing the narrative. This includes:
  * ALL named individuals (e.g., "John Smith", "Mary Johnson", "The CEO", "The Manager")
  * ALL unnamed but important figures (e.g., "The CEO", "The Marketing Director", "The Founder", "The Manager")
  * ALL entities and groups (e.g., "The Board of Directors", "Competitors", "Customers", "Suppliers", "Distributors")
  * ALL organizations mentioned (e.g., "The Company", "Competitors", "Regulatory Bodies", "Government Agencies")
  * ALL stakeholders (e.g., "Shareholders", "Employees", "Partners", "Vendors")
  * ANY person or entity that influences the narrative or decision-making process
- You MUST be extremely thorough and comprehensive. If you're unsure whether someone is important, INCLUDE them. It's better to have too many key figures than to miss important ones.
- Look for EVERY mention of people, companies, groups, or entities in the text and evaluate their importance to the case study narrative.
- For personality_traits, you MUST assign specific numerical values from 0-10 based on the case study content. Do NOT use 0 for all traits. Consider:
  * analytical: How data-driven and logical is this person/entity?
  * creative: How innovative and out-of-the-box thinking do they show?
  * assertive: How direct and forceful are they in their approach?
  * collaborative: How much do they work with others vs. independently?
  * detail_oriented: How focused are they on specifics vs. big picture?
- If you cannot determine a specific trait, use 5 as a neutral default, NOT 0.
- All five "learning_outcomes" must be unique, specific, measurable, and each MUST be numbered (e.g., '1. ...', '2. ...', etc.). If the outcomes are not numbered, your answer will be rejected.
- If any additional files or context are provided, treat them as the most important and authoritative sources. Prioritize information from these files when generating the description, key figures, and learning outcomes.

CRITICAL: Before finalizing your response, double-check that you have identified EVERY person, organization, group, or entity mentioned in the case study content. Your key_figures array should be comprehensive and include ALL stakeholders, decision-makers, influencers, and important entities mentioned in the text.

CASE STUDY CONTENT (context files first, then main PDF):
{combined_content}
"""
        print("[DEBUG] Combined content length:", len(combined_content))
        print("[DEBUG] Combined content preview:", combined_content[:500])
        print("[DEBUG] Prompt sent to OpenAI:\n", prompt[:1000], "..." if len(prompt) > 1000 else "")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.2,
            )
        )
        generated_text = response.choices[0].message.content
        print("[DEBUG] Raw OpenAI response:\n", generated_text)
        # Try to extract JSON from the response using regex
        match = re.search(r'({[\s\S]*})', generated_text)
        if match:
            json_str = match.group(1)
            try:
                ai_result = json.loads(json_str)
                final_result = {
                    "title": ai_result.get("title") or title,
                    "description": ai_result.get("description") or (cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content),
                    "key_figures": ai_result.get("key_figures") if "key_figures" in ai_result else [],
                    "learning_outcomes": ai_result.get("learning_outcomes") or [
                        "1. Analyze the business situation presented in the case study",
                        "2. Identify key stakeholders and their interests",
                        "3. Develop strategic recommendations based on the analysis",
                        "4. Evaluate the impact of decisions on organizational performance",
                        "5. Apply business concepts and frameworks to real-world scenarios"
                    ]
                }
                print("[DEBUG] Final AI result sent to frontend:", final_result)
                return final_result
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON from AI response: {e}")
                print(f"[ERROR] Raw AI response: {json_str}")
        else:
            print("[ERROR] No JSON object found in OpenAI response.")
        # Fallback: return structured content
        return {
            "title": title,
            "description": cleaned_content[:1500] + "..." if len(cleaned_content) > 1500 else cleaned_content,
            "key_figures": [],
            "learning_outcomes": [
                "1. Analyze the business situation presented in the case study",
                "2. Identify key stakeholders and their interests",
                "3. Develop strategic recommendations based on the analysis",
                "4. Evaluate the impact of decisions on organizational performance",
                "5. Apply business concepts and frameworks to real-world scenarios"
            ]
        }
    except Exception as e:
        print(f"[ERROR] AI processing failed: {str(e)}")
        # Fallback: return basic structured content
        preprocessed = preprocess_case_study_content(parsed_content)
        fallback_title = preprocessed["title"] if preprocessed["title"].strip() else "Business Case Study"
        fallback_description = preprocessed["cleaned_content"][:600] + "..." if len(preprocessed["cleaned_content"]) > 600 else preprocessed["cleaned_content"]
        fallback_learning_outcomes = [
            "1. Analyze the business situation presented in the case study",
            "2. Identify key stakeholders and their interests",
            "3. Develop strategic recommendations based on the analysis",
            "4. Evaluate the impact of decisions on organizational performance",
            "5. Apply business concepts and frameworks to real-world scenarios"
        ]
        return {
            "title": fallback_title,
            "description": fallback_description,
            "key_figures": [],
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