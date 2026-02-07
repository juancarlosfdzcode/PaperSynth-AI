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
    """Render sidebar with controls"""
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
    
    # Run new analysis
    st.sidebar.markdown("### 🚀 Generate New Report")
    
    col1, col2 = st.sidebar.columns(2)
    
    query = st.sidebar.text_input("Research Query", value="large language models")
    max_papers = st.sidebar.slider("Max Papers", 5, 50, 15)
    
    if st.sidebar.button("🔄 Generate New Report"):
        with st.spinner("Running PaperSynth pipeline..."):
            # Run main pipeline
            import subprocess
            import sys
            
            try:
                result = subprocess.run([sys.executable, "main.py"], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    st.sidebar.success("✅ New report generated!")
                    st.rerun()
                else:
                    st.sidebar.error(f"❌ Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                st.sidebar.error("❌ Pipeline timed out")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
    
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

def render_methodologies(report):
    """Render methodology analysis"""
    if not report:
        return
        
    methodologies = report['trends'].get('methodologies', {})
    
    if methodologies:
        st.subheader("🛠️ Popular Methodologies")
        
        # Create methodology chart
        df_methods = pd.DataFrame(list(methodologies.items())[:8], columns=['Methodology', 'Papers'])
        
        fig_methods = px.bar(df_methods, x='Methodology', y='Papers',
                           title="Most Used Research Methodologies",
                           color='Papers', color_continuous_scale='blues')
        
        fig_methods.update_xaxis(tickangle=45)
        st.plotly_chart(fig_methods, use_container_width=True)

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
    """Render featured papers table"""
    if not report:
        return
        
    st.subheader("📚 Featured Papers")
    
    papers = report.get('sample_papers', [])
    
    if papers:
        # Create papers dataframe
        papers_data = []
        for paper in papers:
            analysis = paper.get('analysis', {})
            papers_data.append({
                'Title': paper['title'][:80] + '...' if len(paper['title']) > 80 else paper['title'],
                'ArXiv ID': paper['arxiv_id'],
                'Authors': ', '.join(paper.get('authors', [])[:2]) + ('...' if len(paper.get('authors', [])) > 2 else ''),
                'Category': analysis.get('ai_subcategory', 'Unknown'),
                'Methodology': analysis.get('methodology', 'Not specified'),
                'Novelty': analysis.get('novelty_score', 'N/A')
            })
        
        df_papers = pd.DataFrame(papers_data)
        
        st.dataframe(
            df_papers,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ArXiv ID": st.column_config.LinkColumn(
                    "ArXiv ID",
                    help="Click to view paper on arXiv",
                    display_text="https://arxiv.org/abs/(.*)"
                )
            }
        )

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
        
        render_methodologies(selected_report)
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