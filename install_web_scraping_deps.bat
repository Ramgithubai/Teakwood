@echo off
echo Installing missing dependencies for Web Scraping functionality...
echo.

echo Installing OpenAI API client...
pip install openai>=1.3.3

echo Installing Tavily Search API client...
pip install tavily-python>=0.3.0

echo.
echo ✅ Dependencies installed successfully!
echo.
echo Next steps:
echo 1. Make sure your .env file has valid API keys:
echo    - OPENAI_API_KEY=sk-your_key_here
echo    - TAVILY_API_KEY=tvly-your_key_here
echo 2. Restart your Streamlit app
echo.
pause
