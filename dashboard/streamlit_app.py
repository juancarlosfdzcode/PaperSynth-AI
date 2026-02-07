"""
PaperSynth AI - Dashboard Streamlit
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="PaperSynth AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_latest_report():
    """Load the most recent report"""
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        return None
    
    # Find latest report
    json_files = list(outputs_dir.glob("papersynth_report_*.json"))
    
    if not json_files:
        return None
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def load_all_reports():
    """Load all available reports"""
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        return []
    
    reports = []
    json_files = list(outputs_dir.glob("papersynth_report_*.json"))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['filename'] = file_path.name
                data['file_date'] = datetime.fromtimestamp(file_path.stat().st_mtime)
                reports.append(data)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
    
    return sorted(reports, key=lambda x: x['file_date'], reverse=True)

def render_header():
    """Render main header"""
    st.markdown('<h1 class="main-header">🤖 PaperSynth AI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")

def render_sidebar():
    """Render sidebar - VERSIÓN SIMPLIFICADA"""
    st.sidebar.title("🛠️ Controls")
    
    # Report selection
    reports = load_all_reports()
    
    if reports:
        report_options = [f"{r['file_date'].strftime('%Y-%m-%d %H:%M')} ({r['summary']['papers_analyzed']} papers)" 
                         for r in reports]
        
        selected_idx = st.sidebar.selectbox(
            "Select Report",
            range(len(report_options)),
            format_func=lambda x: report_options[x]
        )
        
        selected_report = reports[selected_idx]
    else:
        st.sidebar.warning("No reports found. Run the main pipeline first.")
        selected_report = None
    
    # REMOVER los campos query y max_papers
    st.sidebar.markdown("### 🚀 Generate New Report")
    st.sidebar.markdown("*Uses default settings: 'large language models', 15 papers*")
    
    if st.sidebar.button("🔄 Generate New Report"):
        with st.spinner("Running PaperSynth pipeline..."):
            result = subprocess.run([sys.executable, "main.py"], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                st.sidebar.success("✅ New report generated!")
                st.rerun()
            else:
                st.sidebar.error(f"❌ Error: {result.stderr}")
    
    return selected_report

def render_metrics(report):
    """Render key metrics"""
    if not report:
        return
        
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Papers Found",
            value=report['summary']['total_papers_found']
        )
    
    with col2:
        st.metric(
            label="🔍 Papers Analyzed", 
            value=report['summary']['papers_analyzed']
        )
    
    with col3:
        st.metric(
            label="✅ Success Rate",
            value=report['summary']['success_rate']
        )
    
    with col4:
        innovation_score = report['trends'].get('avg_novelty_score', 0)
        st.metric(
            label="💡 Avg Innovation",
            value=f"{innovation_score:.1f}/10"
        )

def render_trends_charts(report):
    """Render trend visualization charts"""
    if not report:
        return
        
    st.subheader("📊 Research Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # AI Categories chart
        categories = report['trends']['ai_categories']
        if categories:
            df_cats = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            
            fig_cats = px.pie(df_cats, values='Count', names='Category', 
                             title="AI Research Categories",
                             color_discrete_sequence=px.colors.qualitative.Set3)
            
            st.plotly_chart(fig_cats, use_container_width=True)
    
    with col2:
        # Keywords bar chart
        keywords = report['trends']['top_keywords']
        if keywords:
            df_keywords = pd.DataFrame(list(keywords.items())[:10], columns=['Keyword', 'Frequency'])
            
            fig_keywords = px.bar(df_keywords, x='Frequency', y='Keyword',
                                orientation='h', title="Top Technical Keywords",
                                color='Frequency', color_continuous_scale='viridis')
            
            fig_keywords.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_keywords, use_container_width=True)

def render_innovation_analysis(report):
    """Render innovation and novelty analysis - NUEVO GRÁFICO"""
    if not report:
        return
        
    st.subheader("💡 Análisis de Innovación")
    
    # Extraer puntuaciones de novedad
    papers = report.get('sample_papers', [])
    novelty_scores = []
    categories = []
    titles = []
    
    for paper in papers:
        analysis = paper.get('analysis', {})
        score = analysis.get('novelty_score')
        category = analysis.get('ai_subcategory', 'Unknown')
        title = paper.get('title', 'Sin título')
        
        if isinstance(score, (int, float)) and 1 <= score <= 10:
            novelty_scores.append(score)
            categories.append(category)
            titles.append(title[:40] + '...' if len(title) > 40 else title)
    
    if novelty_scores:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de puntuaciones de novedad
            fig_hist = px.histogram(
                x=novelty_scores,
                nbins=10,
                title="Distribución de Puntuaciones de Novedad",
                labels={'x': 'Puntuación de Novedad (1-10)', 'y': 'Número de Papers'},
                color_discrete_sequence=['#1f77b4']
            )
            
            fig_hist.update_layout(
                height=350,
                showlegend=False,
                xaxis=dict(range=[0.5, 10.5], tickvals=list(range(1, 11))),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            # Agregar línea promedio
            avg_score = sum(novelty_scores) / len(novelty_scores)
            fig_hist.add_vline(
                x=avg_score, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Promedio: {avg_score:.1f}"
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Scatter plot: Novedad por Categoría
            if len(set(categories)) > 1:  # Solo si hay múltiples categorías
                df_scatter = pd.DataFrame({
                    'Categoría': categories,
                    'Novedad': novelty_scores,
                    'Título': titles
                })
                
                fig_scatter = px.scatter(
                    df_scatter,
                    x='Categoría',
                    y='Novedad',
                    color='Categoría',
                    size=[1]*len(novelty_scores),
                    hover_data={'Título': True},
                    title="Novedad por Categoría de IA"
                )
                
                fig_scatter.update_layout(
                    height=350,
                    yaxis=dict(range=[0, 11]),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                # Si solo hay una categoría, mostrar box plot
                fig_box = px.box(
                    y=novelty_scores,
                    title="Distribución de Novedad",
                    labels={'y': 'Puntuación de Novedad'}
                )
                
                fig_box.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Estadísticas resumidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Promedio", f"{avg_score:.1f}/10")
        with col2:
            st.metric("📈 Máximo", f"{max(novelty_scores)}/10")
        with col3:
            st.metric("📉 Mínimo", f"{min(novelty_scores)}/10")
        with col4:
            high_innovation = sum(1 for score in novelty_scores if score >= 8)
            st.metric("🚀 Alta Innovación", f"{high_innovation} papers")
    
    else:
        st.info("ℹ️ No se encontraron puntuaciones de novedad en los papers analizados.")

def render_insights(report):
    """Render key insights"""
    if not report:
        return
        
    st.subheader("💡 Key Insights")
    
    insights = report.get('insights', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
        <h4>🔥 Dominant Category</h4>
        <p><strong>{insights.get('dominant_category', 'Unknown')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
        <h4>⚡ Innovation Level</h4>
        <p><strong>{insights.get('innovation_level', 'Unknown')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        hot_topics = ', '.join(insights.get('emerging_keywords', [])[:3])
        st.markdown(f"""
        <div class="insight-box">
        <h4>🚀 Hot Topics</h4>
        <p><strong>{hot_topics}</strong></p>
        </div>
        """, unsafe_allow_html=True)

def render_featured_papers(report):
    """Render featured papers table - VERSIÓN MEJORADA"""
    if not report:
        return
        
    st.subheader("📚 Papers Destacados")
    
    papers = report.get('sample_papers', [])
    
    if papers:
        # Create papers dataframe con URLs
        papers_data = []
        for paper in papers:
            analysis = paper.get('analysis', {})
            
            # Construir lista de autores limpia
            authors = paper.get('authors', [])
            if authors:
                if len(authors) > 3:
                    authors_text = f"{authors[0]}, {authors[1]}, {authors[2]} et al. ({len(authors)} autores)"
                else:
                    authors_text = ", ".join(authors)
            else:
                authors_text = "No especificado"
            
            # ArXiv URL
            arxiv_id = paper.get('arxiv_id', '')
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
            
            papers_data.append({
                'Título': paper['title'][:80] + '...' if len(paper['title']) > 80 else paper['title'],
                'Autores': authors_text,
                'ArXiv ID': arxiv_id,
                'ArXiv URL': arxiv_url,
                'Categoría': analysis.get('ai_subcategory', 'No clasificado'),
                'Metodología': analysis.get('methodology', 'No especificado')[:30] + ('...' if len(analysis.get('methodology', '')) > 30 else ''),
                'Novedad': analysis.get('novelty_score', 'N/A')
            })
        
        df_papers = pd.DataFrame(papers_data)
        
        # Configurar columnas con URLs clickeables
        st.dataframe(
            df_papers,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Título": st.column_config.TextColumn(
                    "Título",
                    help="Título completo del paper",
                    width="large"
                ),
                "Autores": st.column_config.TextColumn(
                    "Autores",
                    help="Lista de autores del paper",
                    width="medium"
                ),
                "ArXiv ID": st.column_config.TextColumn(
                    "ArXiv ID",
                    help="Identificador único en arXiv"
                ),
                "ArXiv URL": st.column_config.LinkColumn(
                    "🔗 Ver Paper",
                    help="Abrir paper en arXiv",
                    display_text="Ver en arXiv"
                ),
                "Categoría": st.column_config.TextColumn(
                    "Categoría IA",
                    help="Categoría de IA del paper"
                ),
                "Metodología": st.column_config.TextColumn(
                    "Metodología",
                    help="Metodología principal utilizada"
                ),
                "Novedad": st.column_config.NumberColumn(
                    "Novedad",
                    help="Puntuación de novedad (1-10)",
                    format="%.1f"
                )
            }
        )
        
        # Agregar links directos debajo de la tabla
        st.markdown("### 🔗 Enlaces Directos")
        
        cols = st.columns(min(len(papers), 3))
        for i, paper in enumerate(papers[:3]):
            with cols[i]:
                arxiv_id = paper.get('arxiv_id', '')
                if arxiv_id:
                    st.markdown(f"""
                    **{paper['title'][:40]}...**  
                    [`🔗 Ver en arXiv`](https://arxiv.org/abs/{arxiv_id})
                    """)

def render_raw_data(report):
    """Render raw data section"""
    if not report:
        return
        
    with st.expander("🔧 Raw Data & Metadata"):
        st.subheader("📋 Report Metadata")
        metadata = report.get('metadata', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Generation Date:**", metadata.get('generation_date', 'Unknown'))
            st.write("**Query Used:**", metadata.get('query_used', 'Not specified'))
        
        with col2:
            st.write("**Categories Searched:**", ', '.join(metadata.get('categories_searched', [])))
            st.write("**Version:**", metadata.get('papersynth_version', 'Unknown'))
        
        st.subheader("📊 Full Trends Data")
        st.json(report.get('trends', {}))

def main():
    """Main dashboard function"""
    render_header()
    
    # Sidebar
    selected_report = render_sidebar()
    
    if selected_report:
        # Main content
        render_metrics(selected_report)
        st.markdown("---")
        
        render_trends_charts(selected_report)
        st.markdown("---")
        
        render_innovation_analysis(selected_report)
        st.markdown("---")
        
        render_insights(selected_report)
        st.markdown("---")
        
        render_featured_papers(selected_report)
        st.markdown("---")
        
        render_raw_data(selected_report)
        
    else:
        st.warning("🚀 No reports found. Run the main pipeline to generate your first report!")
        
        if st.button("▶️ Run PaperSynth Pipeline Now"):
            with st.spinner("Generating your first report..."):
                import subprocess
                import sys
                
                try:
                    result = subprocess.run([sys.executable, "main.py"], 
                                          capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        st.success("✅ First report generated! Refresh the page.")
                    else:
                        st.error(f"❌ Error generating report: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    st.error("❌ Report generation timed out")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()