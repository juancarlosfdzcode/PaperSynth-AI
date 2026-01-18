
"""
Content Analyzer Agent - PaperSynthAI
Analiza papers académicos usando Google Gemini Flash.
"""

## Importación de librerías.

import os
import json
import time
import logging
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv
from google import generativeai as genai

## Carga de variables de entorno.

load_dotenv('../.env')

## Configuración del logging.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Configuración de Gemini.

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

## Creación de la lógica del agente.

@dataclass
class PaperData:
    """
    Estructura de la información en los papers.
    """

    title: str
    authors: List[str]
    published: str
    summary: str
    categories: List[str]
    primary_category: str
    html_url: str

class ContentAnalyzerAgent:
    """
    Agente para analizar la información de los papers usando Gemini Flash.
    """

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        self.rate_limit_delay = 4
    
    def analyze_paper(self, paper: PaperData) -> Dict[str, Any]:
        """
        Analiza un paper.
        """

        prompt = f"""

        Analiza este paper académico de forma estructurada:

        TÍTULO: {paper.title}
        AUTORES: {paper.authors}
        CATEGORÍA PRINCIPAL: {paper.primary_category}
        CATEGORIAS: {', '.join(paper.categories)}
        ENLACE AL PAPER EN HTML: {paper.html_url}
        ABSTRACT: {paper.summary}

        Proporciona un análisis en formato JSON con esta estructura exacta:

        {{
            
            "main_techniques": ["técnica1", "técnica2", "técnica3"],
            "key_contributions": ["contribución1", "contribución2", "contribución3"],
            "relevance_score": 8,
            "theme_category": "categoria_tematica",
            "innovation_level": "alto/medio/bajo",
            "practical_applications": ["aplicación1", "aplicación2"],
            "research_area": "area_de_investigacion",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]

        }}

        Response SOLO con el JSON válido, sin texto adicional.

        Algunos papers pueden no tener contenido en HTML. Esos exclúyelos del análisis.

        """

        try:
            time.sleep(self.rate_limit_delay)
            response = self.model.generate_content(prompt)
            
            analysis = json.loads(response.text.strip())
            analysis['paper_url'] = paper.html_url
            analysis['analyzed_at'] = datetime.now().isoformat()
            
            logger.info(f"Paper correctamente analizado: {paper.title[:50]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando paper '{paper.title[:50]}...': {e}")
            return {
                "error": str(e),
                "paper_url": paper.url,
                "analyzed_at": datetime.now().isoformat()
            }
    
    def analyze_batch(self, papers: List[PaperData]) -> List[Dict[str, Any]]:
        """
        Analizar múltiples papers.
        """

        logger.info(f"Comenzando a analizar batch de {len(papers)} papers...")
        
        analyses = []
        for i, paper in enumerate(papers, 1):
            logger.info(f"Analizando paper {i}/{len(papers)}: {paper.title[:50]}...")
            analysis = self.analyze_paper(paper)
            analyses.append(analysis)
            
        successful = len([a for a in analyses if 'error' not in a])
        logger.info(f"Batch analysis completado: {successful}/{len(papers)} correctamente.")
        
        return analyses
    
    def save_analysis(self, analysis: Dict[str, Any], filename: str = None) -> str:
        """
        Guardar resultados en un fichero JSON.s
        """

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"paper_analysis_{timestamp}.json"
        
        filepath = path = f'papers_AnalyzeFiles/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Analysis saved to: {filepath}")
        return filepath

def test_analyzer():
    """
    Función para testear con un solo paper.
    """
    
    sample_paper = PaperData(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        published="2017-06-12",
        summary="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        categories=["cs.CL", "cs.AI"],
        html_url="https://arxiv.org/abs/1706.03762",
        primary_category="	Computation and Language"
    )
    
    analyzer = ContentAnalyzerAgent()
    
    logger.info("Testing Content Analyzer Agent")
    logger.info("=" * 50)
    logger.info(f"Paper: {sample_paper.title}")
    
    result = analyzer.analyze_paper(sample_paper)
    
    if 'error' in result:
        logger.error(f"❌ Fallo en el análisis: {result['error']}")
    else:
        logger.info("Analysis correcto!")
        logger.info("Resultados:")
        logger.info("-" * 30)
        for key, value in result.items():
            if key not in ['paper_url', 'analyzed_at']:
                logger.info(f"{key}: {value}")
        
        output_file = analyzer.save_analysis(result)
        logger.info(f"\nResultados almacenados en: {output_file}")

if __name__ == "__main__":
    test_analyzer()
