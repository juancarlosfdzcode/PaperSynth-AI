"""
Tests unitarios para Gemini Tool
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.tools.gemini_tool import GeminiTool

class TestGeminiTool:
    
    @pytest.fixture
    def gemini_tool(self):
        """Instancia de GeminiTool para tests"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model:
                mock_instance = Mock()
                mock_model.return_value = mock_instance
                tool = GeminiTool()
                tool._gemini_model = mock_instance
                return tool
    
    def test_gemini_tool_creation(self, gemini_tool):
        """Test que se puede crear una instancia de GeminiTool"""
        assert gemini_tool is not None
        assert gemini_tool.name == "GeminiAnalyzer"
        assert gemini_tool.description is not None
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_setup_gemini_success(self, mock_model, mock_configure):
        """Test setup exitoso de Gemini"""
        mock_instance = Mock()
        mock_model.return_value = mock_instance
        
        tool = GeminiTool()
        
        mock_configure.assert_called_once_with(api_key='test-key')
        assert mock_model.called
    
    @patch.dict('os.environ', {}, clear=True)
    def test_setup_gemini_no_api_key(self):
        """Test fallo por falta de API key"""
        with patch('google.generativeai.configure'):
            tool = GeminiTool()

            assert tool._gemini_model is None
    
    def test_test_connection_success(self, gemini_tool):
        """Test conexión exitosa"""
        mock_response = Mock()
        mock_response.text = "Hello"
        gemini_tool._gemini_model.generate_content.return_value = mock_response
        
        result = gemini_tool.test_connection()
        
        assert result is True
        gemini_tool._gemini_model.generate_content.assert_called_once()
    
    def test_test_connection_failure(self, gemini_tool):
        """Test fallo de conexión"""
        gemini_tool._gemini_model.generate_content.side_effect = Exception("API Error")
        
        result = gemini_tool.test_connection()
        
        assert result is False
    
    def test_analyze_single_paper_success(self, gemini_tool, sample_papers, mock_gemini_response):
        """Test análisis exitoso de un paper"""
        gemini_tool._gemini_model.generate_content.return_value = mock_gemini_response
        
        paper = sample_papers[0]
        result = gemini_tool._analyze_single_paper(paper, "comprehensive", False)
        
        assert result is not None
        assert result["arxiv_id"] == paper["arxiv_id"]
        assert result["title"] == paper["title"]
        assert "analysis" in result
        
        analysis = result["analysis"]
        assert analysis["ai_subcategory"] == "NLP"
        assert analysis["methodology"] == "Transformer"
        assert isinstance(analysis["technical_keywords"], list)
        assert isinstance(analysis["novelty_score"], int)
    

    def test_analyze_single_paper_json_error(self, gemini_tool, sample_papers):
        """Test manejo de error JSON"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        gemini_tool._gemini_model.generate_content.return_value = mock_response
        
        paper = sample_papers[0]
        result = gemini_tool._analyze_single_paper(paper, "comprehensive", False)
        
        assert result is not None
        assert "analysis" in result
        assert "parse_error" in result["analysis"]
        assert "raw_response" in result["analysis"]
    
    def test_analyze_single_paper_api_error(self, gemini_tool, sample_papers):
        """Test error de API"""
        gemini_tool._gemini_model.generate_content.side_effect = Exception("Rate limit exceeded")
        
        paper = sample_papers[0]
        result = gemini_tool._analyze_single_paper(paper, "comprehensive", False)
        
        assert result is None
    
    @patch('time.sleep')  # Mock sleep para tests rápidos
    def test_run_success(self, mock_sleep, gemini_tool, sample_papers, mock_gemini_response):
        """Test ejecución completa exitosa"""
        gemini_tool._gemini_model.generate_content.return_value = mock_gemini_response
        
        result = gemini_tool._run(sample_papers, analysis_type="comprehensive", use_urls=False)
        result_data = json.loads(result)
        
        assert result_data["status"] == "success"
        assert result_data["analyzed_count"] == 2
        assert result_data["total_papers"] == 2
        assert len(result_data["analyses"]) == 2
        
        # Verificar rate limiting
        assert mock_sleep.call_count == 1  # Solo duerme entre papers
    
    def test_run_no_model(self):
        """Test ejecución sin modelo configurado"""
        tool = GeminiTool.__new__(GeminiTool)  # Crear sin __init__
        tool._gemini_model = None
        
        result = tool._run([{"test": "paper"}])
        result_data = json.loads(result)
        
        assert result_data["status"] == "error"
        assert "not configured" in result_data["message"]
    
    def test_run_empty_papers(self, gemini_tool):
        """Test con lista vacía de papers"""
        result = gemini_tool._run([])
        result_data = json.loads(result)
        
        assert result_data["status"] == "success"
        assert result_data["analyzed_count"] == 0
        assert result_data["total_papers"] == 0