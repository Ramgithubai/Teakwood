#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

try:
    print("Testing imports...")
    
    # Test core imports
    import streamlit as st
    print("✅ Streamlit imported")
    
    import pandas as pd
    print("✅ Pandas imported")
    
    import plotly.express as px
    print("✅ Plotly imported")
    
    import numpy as np
    print("✅ Numpy imported")
    
    # Test optional imports
    try:
        from modules.web_scraping_module import perform_web_scraping
        print("✅ Web scraping module available")
    except ImportError:
        print("ℹ️ Web scraping module not available (expected in minimal deployment)")
    
    try:
        from data_explorer import create_data_explorer
        print("✅ Data explorer module available")
    except ImportError:
        print("ℹ️ Data explorer module not available (using built-in instead)")
    
    print("\n✅ All core imports successful!")
    print("🚀 App should run without import errors")
    
except Exception as e:
    print(f"❌ Import error: {e}")
