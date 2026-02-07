# 🤖 PaperSynth AI


> **Sistema Multi-Agente de Síntesis de Papers de Investigación**  
> Descubre, analiza y sintetiza automáticamente papers de IA usando CrewAI y Google Gemini.


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-green.svg)](https://crewai.com/)
[![Gemini](https://img.shields.io/badge/Gemini-AI%20Analysis-orange.svg)](https://ai.google.dev/)


## 🎯 **Características**

- 📄 **Descubre** papers recientes de arXiv.
- 🔍 **Analiza** contenido con Gemini AI (gratuito).
- 📊 **Detecta** tendencias y patrones.
- 📝 **Genera** reportes.
- 🎨 **Visualiza** insights en un dashboard interactivo.


## ⚡ **Inicio Rápido**
```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/papersynth-ai.git
cd papersynth-ai

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar API key de Gemini (gratuito)
echo "GEMINI_API_KEY=tu_clave_aqui" > .env

# 4. Ejecutar análisis
python main.py

# 5. Ver dashboard
python run_dashboard.py
```

## 🏗️ **Arquitectura**
```
🤖 4 Agentes Especializados:
├── Paper Fetcher     → Obtiene papers de arXiv
├── Content Analyzer  → Análisis con Gemini AI  
├── Trend Detector    → Identifica patrones
└── Synthesis Agent   → Genera reportes finales
```

## 📁 **Estructura**
```
papersynth-ai/
├── main.py              # Pipeline principal
├── run_dashboard.py     # Lanzador de dashboard
├── dashboard/           # Dashboard Streamlit
├── config/              # Configuración YAML
├── src/                 # Código fuente
├── outputs/             # Reportes generados
└── data/               # Cache de datos
```

## 📊 **Salidas**

- **JSON**: Datos estructurados para APIs
- **Markdown**: Reportes ejecutivos legibles
- **Dashboard**: Visualizaciones interactivas
- **Trends**: Gráficos de palabras clave, metodologías, categorías

## ⚙️ **Configuración**

**Obligatorio:**
```bash
GEMINI_API_KEY=tu_clave_gemini  # Gratis en https://makersuite.google.com
```

**Opcional:**
```bash
LOG_LEVEL=INFO
MAX_PAPERS=20
```

## 🧪 **Tests**
```bash
python -m pytest tests/
```

## 🚀 **Deploy**

- **Local**: `python main.py && python run_dashboard.py`
- **Streamlit Cloud**: Deploy directo desde GitHub
- **Docker**: `docker run -e GEMINI_API_KEY=key papersynth-ai`

## 🛠️ **Stack Técnico**

- **Multi-Agent**: CrewAI
- **LLM**: Google Gemini Flash (gratuito)
- **Data**: arXiv API, pandas
- **Viz**: Streamlit, Plotly
- **Config**: YAML, Pydantic

## 💡 **Casos de Uso**

- **Investigadores**: Literatura review automatizada
- **Empresas**: Inteligencia competitiva en IA
- **Estudiantes**: Identificación de temas y trends
- **Inversores**: Due diligence técnico

## 🤝 **Contribuir**

1. Fork → 2. Feature branch → 3. Commit → 4. Push → 5. PR

## 📄 **Licencia**

MIT License

## 📧 **Contacto**

**Juan Carlos** - AI Engineer  
📧 [tu.email@ejemplo.com](mailto:tu.email@ejemplo.com)  
🔗 [LinkedIn](https://linkedin.com/in/tu-perfil) | [GitHub](https://github.com/tuusuario)

---

⭐ **Dale estrella si te resultó útil**