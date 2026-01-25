"""
PaperSynth AI - Siempre genera archivos útiles
"""

import logging
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/papersynth.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories"""
    directories = ["data", "outputs", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def run_papersynth_pipeline():
    """Run complete PaperSynth pipeline and ALWAYS generate files"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("🚀 Starting PaperSynth AI Pipeline...")
        
        # === STEP 1: FETCH PAPERS ===
        logger.info("📄 Step 1: Fetching papers from arXiv...")
        
        from src.tools.arxiv_tool import ArxivTool
        arxiv_tool = ArxivTool()
        
        papers_result = arxiv_tool._run(
            query="large language models OR transformers OR attention mechanism",
            max_results=15,  # Reasonable amount for demo
            categories=["cs.AI", "cs.LG", "cs.CL"]
        )
        
        papers_data = json.loads(papers_result)
        
        if papers_data["status"] != "success":
            logger.error("❌ Paper fetching failed")
            # Create error file anyway
            error_info = {
                "error": "Paper fetching failed",
                "details": papers_data,
                "timestamp": timestamp
            }
            with open(f"outputs/error_report_{timestamp}.json", "w") as f:
                json.dump(error_info, f, indent=2)
            return False
            
        papers = papers_data["papers"]
        logger.info(f"✅ Fetched {len(papers)} papers")
        
        # Save raw papers
        papers_file = f"data/fetched_papers_{timestamp}.json"
        with open(papers_file, "w", encoding="utf-8") as f:
            json.dump(papers_data, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved raw papers to {papers_file}")
        
        # === STEP 2: ANALYZE PAPERS ===
        logger.info("🤖 Step 2: Analyzing papers with Gemini...")
        
        from src.tools.gemini_tool import GeminiTool
        gemini_tool = GeminiTool()
        
        # Analyze in batches to avoid timeout
        batch_size = 5
        all_analyses = []
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            logger.info(f"Analyzing batch {i//batch_size + 1}: papers {i+1}-{min(i+batch_size, len(papers))}")
            
            analysis_result = gemini_tool._run(batch, use_urls=False)
            analysis_data = json.loads(analysis_result)
            
            if analysis_data["status"] == "success":
                all_analyses.extend(analysis_data["analyses"])
            else:
                logger.warning(f"Batch {i//batch_size + 1} failed: {analysis_data.get('message', 'Unknown error')}")
        
        logger.info(f"✅ Analyzed {len(all_analyses)} papers successfully")
        
        # Save analysis results
        analysis_file = f"data/analyzed_papers_{timestamp}.json"
        analysis_summary = {
            "status": "success",
            "total_papers": len(papers),
            "analyzed_count": len(all_analyses),
            "timestamp": timestamp,
            "analyses": all_analyses
        }
        
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_summary, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved analysis to {analysis_file}")
        
        # === STEP 3: GENERATE INSIGHTS ===
        logger.info("📊 Step 3: Generating insights and trends...")
        
        # Extract trends
        from collections import Counter
        
        categories = []
        keywords = []
        methodologies = []
        novelty_scores = []
        
        for analysis in all_analyses:
            if "analysis" in analysis and isinstance(analysis["analysis"], dict):
                data = analysis["analysis"]
                
                if "ai_subcategory" in data:
                    categories.append(data["ai_subcategory"])
                if "technical_keywords" in data and isinstance(data["technical_keywords"], list):
                    keywords.extend(data["technical_keywords"])
                if "methodology" in data:
                    methodologies.append(data["methodology"])
                if "novelty_score" in data and isinstance(data["novelty_score"], (int, float)):
                    novelty_scores.append(data["novelty_score"])
        
        # Calculate trends
        trends = {
            "ai_categories": dict(Counter(categories).most_common()),
            "top_keywords": dict(Counter(keywords).most_common(15)),
            "methodologies": dict(Counter(methodologies).most_common()),
            "avg_novelty_score": sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0,
            "novelty_distribution": dict(Counter([round(score) for score in novelty_scores]).most_common())
        }
        
        # === STEP 4: CREATE COMPREHENSIVE REPORT ===
        logger.info("📝 Step 4: Creating comprehensive report...")
        
        report = {
            "metadata": {
                "generation_date": datetime.now().isoformat(),
                "papersynth_version": "1.0.0",
                "query_used": papers_data.get("query_used", ""),
                "categories_searched": papers_data.get("categories_searched", [])
            },
            "summary": {
                "total_papers_found": len(papers),
                "papers_analyzed": len(all_analyses),
                "success_rate": f"{(len(all_analyses)/len(papers)*100):.1f}%" if papers else "0%"
            },
            "trends": trends,
            "insights": {
                "dominant_category": max(trends["ai_categories"].items(), key=lambda x: x[1])[0] if trends["ai_categories"] else "Unknown",
                "emerging_keywords": list(trends["top_keywords"].keys())[:5],
                "innovation_level": "High" if trends.get("avg_novelty_score", 0) > 7 else "Medium" if trends.get("avg_novelty_score", 0) > 5 else "Low"
            },
            "sample_papers": [
                {
                    "title": paper["title"],
                    "arxiv_id": paper["arxiv_id"],
                    "authors": paper.get("authors", [])[:3],  # First 3 authors
                    "analysis": paper.get("analysis", {})
                }
                for paper in all_analyses[:5]  # Top 5 papers
            ]
        }
        
        # Save JSON report
        json_report_file = f"outputs/papersynth_report_{timestamp}.json"
        with open(json_report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved JSON report to {json_report_file}")
        
        # Create Markdown report
        markdown_content = f"""# PaperSynth AI Research Report
*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## 📊 Executive Summary
- **Papers Found**: {report['summary']['total_papers_found']}
- **Papers Analyzed**: {report['summary']['papers_analyzed']}
- **Success Rate**: {report['summary']['success_rate']}
- **Query**: `{report['metadata']['query_used']}`

## 🔥 Key Trends

### AI Categories
{chr(10).join([f"- **{cat}**: {count} papers" for cat, count in list(report['trends']['ai_categories'].items())[:5]])}

### 🚀 Emerging Keywords
{chr(10).join([f"- {keyword} ({count} mentions)" for keyword, count in list(report['trends']['top_keywords'].items())[:10]])}

### 🛠️ Popular Methodologies
{chr(10).join([f"- {method}: {count} papers" for method, count in list(report['trends']['methodologies'].items())[:5]])}

## 💡 Key Insights
- **Dominant Category**: {report['insights']['dominant_category']}
- **Innovation Level**: {report['insights']['innovation_level']} (avg score: {report['trends'].get('avg_novelty_score', 0):.1f}/10)
- **Hot Topics**: {', '.join(report['insights']['emerging_keywords'])}

## 📚 Featured Papers

{chr(10).join([
    f"### {i+1}. {paper['title']}" + chr(10) + 
    f"- **ArXiv ID**: {paper['arxiv_id']}" + chr(10) + 
    f"- **Authors**: {', '.join(paper['authors'])}" + chr(10) + 
    f"- **Category**: {paper['analysis'].get('ai_subcategory', 'Unknown')}" + chr(10) + 
    f"- **Methodology**: {paper['analysis'].get('methodology', 'Not specified')}" + chr(10)
    for i, paper in enumerate(report['sample_papers'])
])}

---
*Generated by PaperSynth AI - Multi-Agent Research Synthesis System*
"""
        
        markdown_file = f"outputs/papersynth_report_{timestamp}.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"💾 Saved Markdown report to {markdown_file}")
        
        # Create summary file with file locations
        summary = {
            "execution_summary": {
                "timestamp": timestamp,
                "status": "success",
                "papers_processed": len(papers),
                "papers_analyzed": len(all_analyses)
            },
            "generated_files": {
                "raw_papers": papers_file,
                "analysis_data": analysis_file,
                "json_report": json_report_file,
                "markdown_report": markdown_file
            }
        }
        
        summary_file = f"outputs/execution_summary_{timestamp}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        
        logger.info("🎉 PaperSynth Pipeline completed successfully!")
        logger.info("📁 Generated files:")
        logger.info(f"   📄 {json_report_file}")
        logger.info(f"   📄 {markdown_file}")
        logger.info(f"   📄 {summary_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Create error report
        error_report = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
        
        error_file = f"outputs/error_report_{timestamp}.json"
        with open(error_file, "w") as f:
            json.dump(error_report, f, indent=2)
        
        logger.info(f"💾 Error report saved to {error_file}")
        return False

def main():
    """Main function - always run full pipeline"""
    load_dotenv()
    setup_directories()
    
    logger.info("🤖 PaperSynth AI - Research Paper Synthesis")
    logger.info("=" * 50)
    
    # Always run full pipeline
    if run_papersynth_pipeline():
        logger.info("✅ All done! Check the outputs/ directory for your reports.")
    else:
        logger.error("❌ Pipeline failed. Check error reports in outputs/ directory.")

if __name__ == "__main__":
    main()