# 🤖 PaperSynth AI.


> **Sistema Multi-Agente de Síntesis para Papers de Investigación.**  
> El objetivo de este proyecto es construir un pipeline robusto y list para producción que permita descubrir, analizar y sintetizar automáticamente papers de IA usando CrewAI y Google Gemini.


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-green.svg)](https://crewai.com/)
[![Gemini](https://img.shields.io/badge/Gemini-AI%20Analysis-orange.svg)](https://ai.google.dev/)


## 🎯 **Características.**

- 📄 **Descubre** papers recientes de arXiv.
- 🔍 **Analiza** contenido con Gemini AI (gratuito).
- 📊 **Detecta** tendencias y patrones.
- 📝 **Genera** reportes.
- 🎨 **Visualiza** insights en un dashboard interactivo.


## ⚡ **Inicio Rápido.**

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

## 🏗️ **Arquitectura.**
```
🤖 4 Agentes desarrollados:

├── Paper Fetcher     → Obtiene papers de arXiv.
├── Content Analyzer  → Análisis con Gemini AI.
├── Trend Detector    → Identifica patrones.
└── Synthesis Agent   → Genera reportes finales.
```

## 📁 **Estructura del proyecto.**
```
papersynth-ai/
├── main.py              # Pipeline principal.
├── run_dashboard.py     # Script para ejecutar el dashboard.
├── requirements.txt     
├── dashboard/           # Dashboard Streamlit.
├── config/              # Configuración YAML.
├── src/                 # Código fuente.
├── outputs/             # Reportes generados.
├── data/                # Cache de datos.
└── tests/               # Tests unitarios.
```

## 📊 **Salidas.**

- **JSON**: Datos estructurados para APIs.
- **Markdown**: Reportes listos para consulta.
- **Dashboard**: Visualizaciones interactivas.
- **Trends**: Gráficos de palabras clave, metodologías, categorías.

## ⚙️ **Configuración.**

**Obligatorio:**
```bash
GEMINI_API_KEY=tu_clave_gemini  # Gratis en https://makersuite.google.com
```

**Opcional:**
```bash
LOG_LEVEL=INFO
MAX_PAPERS=20
```

## 🧪 **Tests.**
```bash
python -m pytest tests/
```

## 🚀 **Deploy.**

- **Local**: `python main.py && python run_dashboard.py`

## ⚠️ **Nota Importante sobre el Dashboard**

**Para mejor experiencia, usa el pipeline principal:**
```bash
python main.py
```

**Dashboard - Limitaciones:**
- La funcionalidad "🔄 Generar Nuevo Reporte" puede causar **timeouts** debido a límites de Streamlit y rate limiting de Gemini gratuito
- **Flujo recomendado**: Ejecutar `python main.py` primero, luego usar `python run_dashboard.py` para visualizar resultados

## 🧪 **Testing**
```bash
# Ejecutar todos los tests
PYTHONPATH=. pytest tests/ -v
```

**Coverage: 96.5% (28/29 tests passing)** Cubriendo todos los componentes críticos:
- ✅ ArXiv Tool: Integración con API de arXiv.
- ✅ Gemini Tool: Procesamiento LLM y análisis.  
- ✅ Agent Factory: Arquitectura multi-agente.

## 🛠️ **Stack Técnico.**

- **Multi-Agent**: CrewAI.
- **LLM**: Google Gemini Flash (gratuito).
- **Data**: arXiv API, pandas.
- **Viz**: Streamlit, Plotly.
- **Config**: YAML, Pydantic.

## 💡 **Casos de Uso.**

- **Investigadores**: Literatura review automatizada.
- **Empresas**: Inteligencia competitiva en IA.
- **Estudiantes**: Identificación de temas y trends.
- **Inversores**: Due diligence técnico.

## 🤝 Contribuir.

### Fork el proyecto

* Crea una rama (git checkout -b feature/AmazingFeature).
* Commit cambios (git commit -m 'Add AmazingFeature').
* Push a la rama (git push origin feature/AmazingFeature).
* Abre un Pull Request.

## 👤 Autor

* GitHub: https://github.com/juancarlosfdzcode
* LinkedIn: https://www.linkedin.com/in/juan-carlos-fdz/
* Medium: https://medium.com/@juancarlosfdzgarcode

⭐ Si este proyecto te resultó útil, considera darle una estrella en GitHub.