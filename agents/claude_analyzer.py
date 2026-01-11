import anthropic
import json
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv('../.env')

class ClaudeAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
    
    def analyze_abstract(self, paper: Dict) -> Dict:
        """
        Analizar un abstract individual.
        """
        prompt = f"""
        Analiza este abstract de un paper de IA:
        
        Título: {paper['title']}
        Abstract: {paper['summary']}
        Categoría arXiv: {paper['primary_category']}
        
        Proporciona análisis en formato JSON:
        {{
            "ai_subcategory": "NLP/CV/ML/RL/etc",
            "methodology": "metodología principal",
            "key_contribution": "contribución en 1 frase",
            "technical_keywords": ["keyword1", "keyword2", "keyword3"],
            "novelty_score": 1-10,
            "practical_applications": ["aplicación1", "aplicación2"]
        }}
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            return {
                "arxiv_id": paper['arxiv_id'],
                "analysis": response_text,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
            
        except Exception as e:
            print(f"Error analizando {paper['arxiv_id']}: {e}")
            return None
    
    def batch_analyze(self, papers: List[Dict], batch_size=5):
        """
        Analizar papers en lotes.
        """
        results = []
        total_tokens = 0
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            print(f"Procesando lote {i//batch_size + 1}...")
            
            for paper in batch:
                result = self.analyze_abstract(paper)
                if result:
                    results.append(result)
                    total_tokens += result.get('tokens_used', 0)
        
        print(f"Total tokens usados: {total_tokens}")
        return results