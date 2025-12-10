#!/bin/bash
# Launch LP Monitoring Dashboard

echo "🚀 Starting LP Investment Monitoring Dashboard..."
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip install streamlit plotly
fi

# Launch dashboard
echo "📊 Launching dashboard on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run dashboard.py
