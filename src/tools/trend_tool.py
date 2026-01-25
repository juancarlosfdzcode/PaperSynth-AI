"""
Trend Detection Tool - Análisis básico de patrones
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
import json
from collections import Counter
import logging

class TrendAnalysisInput(BaseModel):
    analyzed_papers: List[Dict] = Field(description="List of analyzed papers")
    trend_type: str = Field(default="keywords", description="Type of trend analysis")

class TrendTool(BaseTool):
    name: str = "TrendDetector"
    description: str = "Detect patterns and trends in research papers"
    args_schema: Type[BaseModel] = TrendAnalysisInput

    def _run(self, analyzed_papers: List[Dict], trend_type: str = "keywords") -> str:
        """
        Basic trend detection
        """

        try:
            trends = {}
            
            if trend_type == "keywords":
                trends = self._analyze_keyword_trends(analyzed_papers)
            elif trend_type == "methodologies":
                trends = self._analyze_methodology_trends(analyzed_papers)
            elif trend_type == "categories":
                trends = self._analyze_category_trends(analyzed_papers)
            
            return json.dumps({
                "status": "success",
                "trend_type": trend_type,
                "trends": trends,
                "papers_analyzed": len(analyzed_papers)
            }, indent=2)
            
        except Exception as e:
            error_msg = f"Error in trend analysis: {str(e)}"
            logging.error(f"TrendTool: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})
    
    def _analyze_keyword_trends(self, papers: List[Dict]) -> Dict:
        """
        Analyze keyword frequency trends
        """

        all_keywords = []
        for paper in papers:
            if 'analysis' in paper and 'technical_keywords' in paper['analysis']:
                all_keywords.extend(paper['analysis']['technical_keywords'])
        
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)
        
        return {
            "top_keywords": top_keywords,
            "total_unique_keywords": len(keyword_counts),
            "keyword_distribution": dict(keyword_counts)
        }
    
    def _analyze_methodology_trends(self, papers: List[Dict]) -> Dict:
        """
        Analyze methodology trends
        """

        methodologies = []
        for paper in papers:
            if 'analysis' in paper and 'methodology' in paper['analysis']:
                methodologies.append(paper['analysis']['methodology'])
        
        method_counts = Counter(methodologies)
        top_methods = method_counts.most_common(5)
        
        return {
            "top_methodologies": top_methods,
            "methodology_distribution": dict(method_counts)
        }
    
    def _analyze_category_trends(self, papers: List[Dict]) -> Dict:
        """
        Analyze AI subcategory trends
        """

        categories = []
        for paper in papers:
            if 'analysis' in paper and 'ai_subcategory' in paper['analysis']:
                categories.append(paper['analysis']['ai_subcategory'])
        
        category_counts = Counter(categories)
        
        return {
            "category_distribution": dict(category_counts),
            "dominant_category": category_counts.most_common(1)[0] if category_counts else None
        }