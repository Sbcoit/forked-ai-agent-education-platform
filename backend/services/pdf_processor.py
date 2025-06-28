import PyPDF2
import pdfplumber
import re
from typing import Dict, List, Any, Optional
import asyncio
from io import BytesIO
from services.ai_service import AIService

class PDFProcessor:
    def __init__(self):
        self.ai_service = AIService()
    
    async def analyze_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """Analyze PDF content and extract business scenario information"""
        
        # Extract text from PDF
        text_content = await self._extract_text_from_pdf(pdf_content)
        
        if not text_content or len(text_content) < 100:
            raise ValueError("PDF content is too short or could not be extracted")
        
        # Use AI to analyze the content
        analysis = await self._ai_analyze_content(text_content)
        
        # Extract additional structured information
        structured_info = await self._extract_structured_info(text_content)
        
        # Combine AI analysis with structured extraction
        result = {
            **analysis,
            "key_stakeholders": structured_info.get("stakeholders", []),
            "timeline": structured_info.get("timeline", ""),
            "budget_info": structured_info.get("budget_info", ""),
            "extracted_text_length": len(text_content),
            "analysis_confidence": self._calculate_confidence(text_content, analysis)
        }
        
        return result
    
    async def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF using multiple methods"""
        text = ""
        
        try:
            # Method 1: Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text and len(text) > 100:
                return self._clean_text(text)
            
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        try:
            # Method 2: Fallback to PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return self._clean_text(text)
            
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            raise ValueError("Could not extract text from PDF")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and common PDF artifacts
        text = re.sub(r'\n\d+\n', ' ', text)
        text = re.sub(r'Page \d+', '', text)
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        
        return text.strip()
    
    async def _ai_analyze_content(self, content: str) -> Dict[str, Any]:
        """Use AI to analyze PDF content and extract business information"""
        
        # Truncate content if too long (keep first 4000 chars for analysis)
        analysis_content = content[:4000] if len(content) > 4000 else content
        
        prompt = f"""
        Analyze this business case study and extract key information for creating an educational simulation:

        Content: {analysis_content}

        Extract and return as JSON:
        1. title - Main title or case study name
        2. description - 2-3 sentence summary of the business situation
        3. industry - Primary industry category
        4. challenge - Main business challenge or problem to solve
        5. learning_objectives - What students should learn (3-4 objectives)
        6. suggested_agents - Array of 4 AI agent roles that would be relevant
        
        For suggested_agents, include objects with:
        - role: Agent role name
        - focus: What this agent should focus on
        - expertise: Specific expertise areas
        
        Return valid JSON only.
        """
        
        try:
            response = await self.ai_service.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business case analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            
            # Clean JSON response (remove markdown formatting if present)
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            
            import json
            analysis = json.loads(content)
            
            return analysis
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Return fallback analysis
            return self._generate_fallback_analysis(analysis_content)
    
    async def _extract_structured_info(self, content: str) -> Dict[str, Any]:
        """Extract structured information using pattern matching"""
        
        result = {
            "stakeholders": [],
            "timeline": "",
            "budget_info": ""
        }
        
        # Extract stakeholders
        stakeholder_patterns = [
            r"stakeholders?:?\s*([^\n.]+)",
            r"key players?:?\s*([^\n.]+)",
            r"participants?:?\s*([^\n.]+)",
            r"(CEO|CFO|CTO|CMO|Manager|Director|President)",
            r"(customers?|clients?|users?)",
            r"(investors?|shareholders?)",
            r"(employees?|staff|team)"
        ]
        
        for pattern in stakeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    result["stakeholders"].extend([m.strip() for m in match if m.strip()])
                else:
                    result["stakeholders"].append(match.strip())
        
        # Remove duplicates and clean
        result["stakeholders"] = list(set([s.title() for s in result["stakeholders"] if len(s) > 2]))[:10]
        
        # Extract timeline information
        timeline_patterns = [
            r"(\d+\s*(weeks?|months?|years?|days?))",
            r"(Q[1-4]\s*\d{4})",
            r"(deadline|timeline|schedule):?\s*([^\n.]+)",
            r"by\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}"
        ]
        
        for pattern in timeline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result["timeline"] = ", ".join([str(match) if isinstance(match, str) else " ".join(match) for match in matches[:3]])
                break
        
        # Extract budget information
        budget_patterns = [
            r"\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|M|B|K))?",
            r"budget:?\s*([^\n.]+)",
            r"investment:?\s*([^\n.]+)",
            r"cost:?\s*([^\n.]+)"
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result["budget_info"] = ", ".join(matches[:5])
                break
        
        return result
    
    def _generate_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Generate fallback analysis when AI analysis fails"""
        
        # Try to extract basic information
        title = "PDF Case Study"
        if len(content) > 50:
            # Use first meaningful sentence as title
            sentences = content.split('.')[:3]
            title = sentences[0][:100] + "..." if len(sentences[0]) > 100 else sentences[0]
        
        return {
            "title": title,
            "description": "Business case study requiring strategic decision making and cross-functional collaboration.",
            "industry": "Business",
            "challenge": "Navigate complex business decisions while managing stakeholder interests and resource constraints.",
            "learning_objectives": [
                "Understand cross-functional business operations",
                "Develop strategic thinking and decision-making skills",
                "Learn to balance multiple stakeholder perspectives",
                "Practice business communication and negotiation"
            ],
            "suggested_agents": [
                {
                    "role": "Strategic Advisor",
                    "focus": "High-level strategy and decision making",
                    "expertise": "Strategic planning, market analysis, competitive positioning"
                },
                {
                    "role": "Financial Analyst",
                    "focus": "Financial planning and analysis",
                    "expertise": "Budget management, financial modeling, ROI analysis"
                },
                {
                    "role": "Operations Manager",
                    "focus": "Operational efficiency and execution",
                    "expertise": "Process optimization, resource allocation, project management"
                },
                {
                    "role": "Market Research Specialist",
                    "focus": "Market insights and customer analysis",
                    "expertise": "Market research, customer segmentation, competitive analysis"
                }
            ]
        }
    
    def _calculate_confidence(self, text: str, analysis: Dict[str, Any]) -> int:
        """Calculate confidence score for the analysis based on text quality and completeness"""
        
        base_score = 60
        
        # Text length factor
        if len(text) > 2000:
            base_score += 15
        elif len(text) > 1000:
            base_score += 10
        elif len(text) < 500:
            base_score -= 20
        
        # Analysis completeness
        if analysis.get("title") and len(analysis["title"]) > 10:
            base_score += 5
        if analysis.get("description") and len(analysis["description"]) > 50:
            base_score += 5
        if analysis.get("suggested_agents") and len(analysis["suggested_agents"]) >= 3:
            base_score += 10
        
        # Text quality indicators
        business_keywords = ["strategy", "management", "market", "customer", "revenue", "profit", "investment", "growth"]
        keyword_count = sum(1 for keyword in business_keywords if keyword in text.lower())
        base_score += min(keyword_count * 2, 15)
        
        return max(30, min(95, base_score)) 