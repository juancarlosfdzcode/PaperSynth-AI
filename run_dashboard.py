"""
Quick launcher for PaperSynth Dashboard
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Ensure streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Installing streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
    
    # Run dashboard
    dashboard_path = Path("dashboard/streamlit_app.py")
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return
    
    print("🚀 Starting PaperSynth Dashboard...")
    print("📊 Dashboard will open at: http://localhost:8501")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        str(dashboard_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    main()