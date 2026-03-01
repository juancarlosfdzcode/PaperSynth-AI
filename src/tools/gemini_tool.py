"""
Gemini Tool para CrewAI - Versión corregida sin conflictos Pydantic
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai
import json
import time
import logging
import os

class GeminiAnalysisInput(BaseModel):
    papers: List[Dict] = Field(description="List of papers to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    use_urls: bool = Field(default=True, description="Use ar5iv URLs for full paper access")

class GeminiTool(BaseTool):
    name: str = "GeminiAnalyzer"
    description: str = "Analyze research papers using Gemini Flash API with rate limiting"
    args_schema: Type[BaseModel] = GeminiAnalysisInput
    
    # Define fields that Pydantic allows
    _gemini_model: Optional[Any] = None  # Private attribute to avoid conflicts

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_gemini()
        
    def _setup_gemini(self):
        """Setup Gemini model - usando atributo privado para evitar conflictos"""
        try:
            # Configure Gemini API
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY is required")
                
            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
            
            logging.info("✅ Gemini model configured successfully")
            
        except Exception as e:
            logging.error(f"❌ Error setting up Gemini: {e}")
            self._gemini_model = None
            
    def _run(self, papers: List[Dict], analysis_type: str = "comprehensive", use_urls: bool = True) -> str:
        """
        Analyze papers with Gemini Flash
        """
        if self._gemini_model is None:
            return json.dumps({
                "status": "error", 
                "message": "Gemini model not configured"
            })
            
        try:
            results = []
            
            for i, paper in enumerate(papers, 1):
                logging.info(f"GeminiTool: Analyzing paper {i}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}...")
                
                analysis = self._analyze_single_paper(paper, analysis_type, use_urls)
                if analysis:
                    results.append(analysis)
                
                # Rate limiting - 15 requests per minute max
                if i < len(papers):  # Don't sleep after last paper
                    time.sleep(4.1)  # ~14.5 requests per minute to be safe
            
            return json.dumps({
                "status": "success", 
                "analyzed_count": len(results),
                "total_papers": len(papers),
                "analyses": results
            }, indent=2)
            
        except Exception as e:
            error_msg = f"Error in Gemini analysis: {str(e)}"
            logging.error(f"GeminiTool: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})

    def _analyze_single_paper(self, paper: Dict, analysis_type: str, use_urls: bool) -> Optional[Dict]:
        """
        Analyze a single paper with Gemini
        """
        try:
            # Prepare content for Gemini
            if use_urls and 'ar5iv_url' in paper:
                # Gemini puede leer URLs directamente
                content = f"""
                Analyze this AI research paper:
                URL: {paper['ar5iv_url']}
                
                Title: {paper['title']}
                Authors: {', '.join(paper.get('authors', []))}
                Abstract: {paper['summary']}
                """
            else:
                # Use only abstract
                content = f"""
                Analyze this AI research paper based on its abstract:
                
                Title: {paper['title']}
                Authors: {', '.join(paper.get('authors', []))}
                Abstract: {paper['summary']}
                Category: {paper.get('primary_category', 'Unknown')}
                """
            
            # Add analysis prompt
            content += """
            
            Provide analysis in this exact JSON format:
            {
                "ai_subcategory": "NLP/CV/ML/RL/etc",
                "methodology": "main methodology used",
                "key_contribution": "primary contribution in one sentence",
                "technical_keywords": ["keyword1", "keyword2", "keyword3"],
                "novelty_score": integer 1-10 (1-3=incremental, 4-6=moderate contribution combining known approaches, 7-8=clear advancement over state of the art, 9-10=ONLY for paradigm-shifting work like Transformers or GPT. Be conservative, most papers score 4-6),
                "practical_applications": ["application1", "application2"],
                "limitations": ["limitation1", "limitation2"]
            }
            
            Respond ONLY with the JSON, no additional text.
            """
            
            response = self._gemini_model.generate_content(content)
            
            # Parse JSON response
            try:
                # Clean response text
                response_text = response.text.strip()
                
                # Remove potential markdown formatting
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                analysis_json = json.loads(response_text)
                
                return {
                    "arxiv_id": paper.get('arxiv_id', 'unknown'),
                    "title": paper['title'],
                    "analysis": analysis_json,
                    "processed_with_url": use_urls and 'ar5iv_url' in paper
                }
                
            except json.JSONDecodeError as je:
                logging.warning(f"Could not parse JSON for {paper.get('arxiv_id')}: {je}")
                logging.debug(f"Raw response: {response.text}")
                
                # Return raw response as fallback
                return {
                    "arxiv_id": paper.get('arxiv_id', 'unknown'),
                    "title": paper['title'],
                    "analysis": {
                        "raw_response": response.text,
                        "parse_error": str(je)
                    },
                    "processed_with_url": False
                }
                
        except Exception as e:
            logging.error(f"Error analyzing paper {paper.get('arxiv_id')}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if Gemini connection is working"""
        try:
            if self._gemini_model is None:
                return False
                
            response = self._gemini_model.generate_content("Say hello in one word")
            return True
            
        except Exception as e:
            logging.error(f"Gemini connection test failed: {e}")
            return False