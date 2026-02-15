"""
Tests unitarios para ArXiv Tool
"""

import pytest
import json
from unittest.mock import Mock, patch
import arxiv
from src.tools.arxiv_tool import ArxivTool

class TestArxivTool:
    
    @pytest.fixture
    def arxiv_tool(self):
        """Instancia de ArxivTool para tests"""
        return ArxivTool()
    
    def test_arxiv_tool_creation(self, arxiv_tool):
        """Test que se puede crear una instancia de ArxivTool"""
        assert arxiv_tool is not None
        assert arxiv_tool.name == "ArxivPaperFetcher"
        assert arxiv_tool.description is not None
    
    @patch('src.tools.arxiv_tool.arxiv.Client')
    def test_create_client_success(self, mock_client, arxiv_tool):
        """Test creación exitosa de cliente arXiv"""
        mock_client.return_value = Mock()
        
        client = arxiv_tool._create_client()
        
        assert client is not None
        mock_client.assert_called_once()
    
    @patch('src.tools.arxiv_tool.arxiv.Client')
    def test_create_client_failure(self, mock_client, arxiv_tool):
        """Test fallo en creación de cliente arXiv"""
        mock_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            arxiv_tool._create_client()
        
        assert "Connection failed" in str(exc_info.value)
    
    @patch('src.tools.arxiv_tool.arxiv.Search')
    @patch('src.tools.arxiv_tool.arxiv.Client')
    def test_arxiv_search(self, mock_client, mock_search, arxiv_tool):
        """Test búsqueda en arXiv"""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_search_instance = Mock()
        mock_search.return_value = mock_search_instance
        
        mock_results = [Mock(), Mock()]
        mock_client_instance.results.return_value = mock_results
        
        results = arxiv_tool._arxiv_search(mock_client_instance, 10, "test query")
        
        assert results == mock_results
        mock_search.assert_called_once_with(
            query="test query",
            max_results=10,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
    
    def test_papers_processor(self, arxiv_tool, mock_arxiv_response):
        """Test procesamiento de papers"""
        mock_results = [mock_arxiv_response]
        
        papers = arxiv_tool._papers_processor(mock_results)
        
        assert len(papers) == 1
        paper = papers[0]
        
        # Verificar campos obligatorios
        assert 'id' in paper
        assert 'arxiv_id' in paper
        assert 'title' in paper
        assert 'authors' in paper
        assert 'summary' in paper
        assert 'fetched_date' in paper
        
        # Verificar valores
        assert paper['arxiv_id'] == "2024.01234v1"
        assert paper['title'] == "Test Paper Title"
        assert paper['authors'] == ["Test Author"]
    
    def test_add_ar5iv_urls(self, arxiv_tool):
        """Test adición de URLs ar5iv"""
        papers = [{"arxiv_id": "2024.01234v1"}]
        
        enhanced_papers = arxiv_tool._add_ar5iv_urls(papers)
        
        assert len(enhanced_papers) == 1
        paper = enhanced_papers[0]
        
        assert 'ar5iv_url' in paper
        assert 'arxiv_url' in paper
        assert paper['ar5iv_url'] == "https://ar5iv.labs.arxiv.org/html/2024.01234v1"
        assert paper['arxiv_url'] == "https://arxiv.org/abs/2024.01234v1"
    
    @patch('src.tools.arxiv_tool.ArxivTool._papers_processor')
    @patch('src.tools.arxiv_tool.ArxivTool._arxiv_search')  
    @patch('src.tools.arxiv_tool.ArxivTool._create_client')
    def test_run_success(self, mock_create_client, mock_search, mock_processor, arxiv_tool):
        """Test ejecución exitosa completa"""
        # Setup mocks
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        mock_results = [Mock()]
        mock_search.return_value = mock_results
        
        mock_papers = [{"arxiv_id": "2024.01234v1", "title": "Test"}]
        mock_processor.return_value = mock_papers
        
        # Execute
        result = arxiv_tool._run("test query", max_results=5, categories=["cs.AI"])
        
        # Verify
        result_data = json.loads(result)
        
        assert result_data["status"] == "success"
        assert result_data["papers_count"] == 1
        assert len(result_data["papers"]) == 1
        assert "ar5iv_url" in result_data["papers"][0]  # URLs añadidas
    
    def test_run_failure(self, arxiv_tool):
        """Test fallo en ejecución"""
        with patch('src.tools.arxiv_tool.ArxivTool._create_client') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            result = arxiv_tool._run("test query")
            result_data = json.loads(result)
            
            assert result_data["status"] == "error"
            assert "API Error" in result_data["message"]
    
    def test_clean_abstract(self, arxiv_tool):
        """Test limpieza de abstracts"""
        dirty_abstract = "This is a test\n\nwith multiple   spaces\tand tabs"
        
        clean_abstract = arxiv_tool._clean_abstract(dirty_abstract)
        
        assert clean_abstract == "This is a test with multiple spaces and tabs"
    
    def test_get_categories_info(self, arxiv_tool):
        """Test información de categorías"""
        categories = arxiv_tool.get_categories_info()
        
        assert isinstance(categories, dict)
        assert "cs.AI" in categories
        assert "cs.LG" in categories
        assert categories["cs.AI"] == "Artificial Intelligence"