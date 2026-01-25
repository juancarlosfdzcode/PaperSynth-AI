from arxiv_fetcher import create_client, arxiv_search, papers_processor, save_papers, AI_QUERIES
from claude_analyzer import ClaudeAnalyzer
import os

def main():
    """
    Pipeline principal.
    """
    # 1. Fetch papers
    print("Obteniendo papers de arXiv...")
    client = create_client()
    results = arxiv_search(client, 20, AI_QUERIES['machine_learning'])
    papers = papers_processor(results)
    
    # Guardar datos raw
    raw_filename = save_papers(papers, "raw_papers.json")
    
    # 2. Analizar con Claude
    print("Analizando con Claude...")
    analyzer = ClaudeAnalyzer()
    analyzed = analyzer.batch_analyze(papers, batch_size=3)
    
    # Guardar análisis
    analysis_filename = save_papers(analyzed, "analyzed_papers.json")
    
    print(f"Completado! Papers: {len(papers)}, Analizados: {len(analyzed)}")

if __name__ == '__main__':
    main()