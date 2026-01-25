"""
ArXiv Tool para CrewAI
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
import arxiv
import json
import re
from datetime import datetime
import logging

class ArxivSearchInput(BaseModel):
    query: str = Field(description="Search query for arXiv papers")
    max_results: int = Field(default=20, description="Maximum number of papers to fetch")
    categories: List[str] = Field(default=["cs.AI"], description="arXiv categories to search")

class ArxivTool(BaseTool):
    name: str = "ArxivPaperFetcher"
    description: str = "Fetch recent AI papers from arXiv with abstracts, metadata and ar5iv URLs"
    args_schema: Type[BaseModel] = ArxivSearchInput

    def _run(self, query: str, max_results: int = 20, categories: List[str] = ["cs.AI"]) -> str:
        """
        Fetch papers from arXiv.
        """
        try:

            client = self._create_client()
            
            if categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
                full_query = f"({cat_query}) AND ({query})"
            else:
                full_query = query
            
            results = self._arxiv_search(client, max_results, full_query)
            papers = self._papers_processor(results)
            
            papers = self._add_ar5iv_urls(papers)
            
            logging.info(f"ArxivTool: Fetched {len(papers)} papers for query: '{query}'")
            
            return json.dumps({
                "status": "success",
                "papers_count": len(papers),
                "papers": papers,
                "query_used": full_query,
                "categories_searched": categories
            }, indent=2)
            
        except Exception as e:
            error_msg = f"Error fetching papers: {str(e)}"
            logging.error(f"ArxivTool: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})

    def _create_client(self):
        """
        Create arXiv client.
        """

        try:
            client = arxiv.Client()
            return client
        except Exception as e:
            raise Exception(f"Error deploying arXiv client: {e}")
    
    def _arxiv_search(self, client, max_results, query):
        """
        Search papers in arXiv.
        """

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = client.results(search)
        return results
    
    def _papers_processor(self, results):
        """
        Papers processor.
        """

        elements = ['published','title','authors','summary','primary_category',
                   'categories','link','pdf_url']
        
        papers = []
        for i, result in enumerate(results, 1):
            paper = {'id': i}
            
            paper['arxiv_id'] = result.entry_id.split('/')[-1]
            paper['fetched_date'] = datetime.now().isoformat()
            
            for field in elements:
                if hasattr(result, field):
                    value = getattr(result, field)
                    
                    if field == 'published':
                        paper[field] = value.isoformat()
                    elif field == 'authors':
                        paper[field] = [str(author) for author in value]
                    elif field == 'summary':
                        paper[field] = self._clean_abstract(value)
                    else:
                        paper[field] = value
            
            papers.append(paper)
        
        return papers
    
    def _clean_abstract(self, abstract: str) -> str:
        """
        Function to clean the abstract.
        """

        cleaned = re.sub(r'\s+', ' ', abstract.strip())
        cleaned = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]', '', cleaned)

        return cleaned
    
    def _add_ar5iv_urls(self, papers: List[Dict]) -> List[Dict]:
        """
        Add ar5iv URLs so that Gemini can read complete papers
        ar5iv converts PDFs to more readable HTML
        """

        for paper in papers:
            arxiv_id = paper['arxiv_id']
            paper['ar5iv_url'] = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
            paper['arxiv_url'] = f"https://arxiv.org/abs/{arxiv_id}"
        
        return papers
    
    def get_categories_info(self) -> Dict[str, str]:
        """
        Information about arXiv categories.
        """

        return {
            "cs.AI": "Artificial Intelligence",
            "cs.LG": "Machine Learning", 
            "cs.CL": "Computation and Language (NLP)",
            "cs.CV": "Computer Vision and Pattern Recognition",
            "cs.NE": "Neural and Evolutionary Computing",
            "stat.ML": "Machine Learning (Statistics)",
            "cs.RO": "Robotics",
            "cs.IR": "Information Retrieval"
        }