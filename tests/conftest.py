"""
Configuración de pytest y fixtures compartidas
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Setup test environment
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment"""
    os.environ['GEMINI_API_KEY'] = 'test-api-key'
    os.environ['GOOGLE_API_KEY'] = 'test-api-key'
    
    # Create test directories
    test_dirs = ['test_data', 'test_outputs', 'test_logs']
    for directory in test_dirs:
        Path(directory).mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after tests
    import shutil
    for directory in test_dirs:
        if Path(directory).exists():
            shutil.rmtree(directory)

@pytest.fixture
def sample_papers():
    """Sample papers data from arXiv"""
    return [
        {
            "id": 1,
            "arxiv_id": "2024.01234v1",
            "title": "Advances in Large Language Models for Natural Language Processing",
            "authors": ["John Doe", "Jane Smith", "Bob Johnson"],
            "summary": "This paper presents novel approaches to improving large language models through attention mechanisms and transformer architectures. We demonstrate significant improvements in natural language understanding tasks.",
            "primary_category": "cs.CL",
            "categories": ["cs.CL", "cs.AI", "cs.LG"],
            "published": "2024-01-15T09:00:00Z",
            "link": "https://arxiv.org/abs/2024.01234",
            "pdf_url": "https://arxiv.org/pdf/2024.01234.pdf",
            "ar5iv_url": "https://ar5iv.labs.arxiv.org/html/2024.01234",
            "fetched_date": "2024-01-16T10:00:00Z"
        },
        {
            "id": 2,
            "arxiv_id": "2024.01235v1", 
            "title": "Computer Vision Applications in Autonomous Systems",
            "authors": ["Alice Wang", "Charlie Brown"],
            "summary": "We explore computer vision techniques for autonomous navigation systems, focusing on real-time object detection and scene understanding using convolutional neural networks.",
            "primary_category": "cs.CV",
            "categories": ["cs.CV", "cs.AI"],
            "published": "2024-01-14T14:30:00Z",
            "link": "https://arxiv.org/abs/2024.01235",
            "pdf_url": "https://arxiv.org/pdf/2024.01235.pdf",
            "ar5iv_url": "https://ar5iv.labs.arxiv.org/html/2024.01235",
            "fetched_date": "2024-01-16T10:05:00Z"
        }
    ]

@pytest.fixture
def sample_analysis():
    """Sample analysis data from Gemini"""
    return [
        {
            "arxiv_id": "2024.01234v1",
            "title": "Advances in Large Language Models for Natural Language Processing",
            "analysis": {
                "ai_subcategory": "NLP",
                "methodology": "Transformer architecture with attention mechanisms",
                "key_contribution": "Novel attention mechanism improving language understanding",
                "technical_keywords": ["transformer", "attention", "language model", "NLP"],
                "novelty_score": 8,
                "practical_applications": ["chatbots", "language translation", "text summarization"]
            },
            "processed_successfully": True
        },
        {
            "arxiv_id": "2024.01235v1",
            "title": "Computer Vision Applications in Autonomous Systems", 
            "analysis": {
                "ai_subcategory": "CV",
                "methodology": "Convolutional Neural Networks",
                "key_contribution": "Real-time object detection for autonomous navigation",
                "technical_keywords": ["CNN", "object detection", "autonomous", "computer vision"],
                "novelty_score": 7,
                "practical_applications": ["autonomous vehicles", "robotics", "surveillance"]
            },
            "processed_successfully": True
        }
    ]

@pytest.fixture
def sample_report():
    """Sample complete report"""
    return {
        "metadata": {
            "generation_date": "2024-01-16T12:00:00Z",
            "papersynth_version": "1.0.0",
            "query_used": "large language models OR computer vision"
        },
        "summary": {
            "total_papers_found": 2,
            "papers_analyzed": 2,
            "success_rate": "100.0%"
        },
        "trends": {
            "ai_categories": {"NLP": 1, "CV": 1},
            "top_keywords": {"transformer": 1, "attention": 1, "CNN": 1, "object detection": 1},
            "methodologies": {"Transformer architecture": 1, "Convolutional Neural Networks": 1},
            "avg_novelty_score": 7.5
        },
        "sample_papers": [
            # Sample analysis data would go here
        ]
    }

@pytest.fixture
def mock_arxiv_response():
    """Mock arXiv API response"""
    mock_result = Mock()
    mock_result.entry_id = "http://arxiv.org/abs/2024.01234v1"
    mock_result.title = "Test Paper Title"
    
    # Corregir mock de authors
    mock_author = Mock()
    mock_author.__str__ = Mock(return_value="Test Author")
    mock_result.authors = [mock_author]
    
    mock_result.summary = "Test abstract content"
    mock_result.primary_category = Mock(term="cs.AI")
    mock_result.categories = [Mock(term="cs.AI")]
    mock_result.published = datetime(2024, 1, 15, 9, 0, 0)
    mock_result.links = [Mock(href="https://arxiv.org/abs/2024.01234")]
    mock_result.pdf_url = "https://arxiv.org/pdf/2024.01234.pdf"
    
    return mock_result

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response"""
    mock_response = Mock()
    mock_response.text = json.dumps({
        "ai_subcategory": "NLP",
        "methodology": "Transformer",
        "key_contribution": "Novel attention mechanism",
        "technical_keywords": ["transformer", "attention"],
        "novelty_score": 8,
        "practical_applications": ["chatbots", "translation"]
    })
    return mock_response