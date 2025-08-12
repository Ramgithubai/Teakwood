# 🤖 AI-Powered CSV Data Analyzer

An intelligent Streamlit application for analyzing CSV/Excel data with AI-powered insights and automated business research capabilities.

## 🚀 Quick Deploy to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   git remote add origin https://github.com/yourusername/ai-csv-analyzer.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file: `ai_csv_analyzer.py`
   - Use requirements file: `requirements_production.txt`

3. **Configure API Keys (Optional):**
   - In Streamlit Cloud → App Settings → Secrets
   - Add your API keys:
   ```toml
   GROQ_API_KEY = "your_groq_key"
   OPENAI_API_KEY = "sk-your_openai_key"
   ANTHROPIC_API_KEY = "your_anthropic_key"
   TAVILY_API_KEY = "tvly-your_tavily_key"
   ```

## ✨ Features

- **Smart Data Loading:** Auto-detects identifier columns (HS codes, product codes)
- **AI Chat Interface:** Ask questions about your data in natural language
- **Multiple AI Providers:** Claude, Groq, OpenAI, and local analysis
- **Advanced Filtering:** Business intelligence focused data exploration
- **Automated Research:** Business contact finding with web scraping
- **Export Capabilities:** Enhanced datasets with research results

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run ai_csv_analyzer.py
```

## 📁 Configuration Files

- `.streamlit/config.toml` - Streamlit settings
- `.streamlit/secrets.toml.example` - API keys template
- `requirements_production.txt` - Production dependencies
- `Procfile` - Heroku deployment configuration

## 🔐 Environment Variables

The app works without API keys but provides enhanced features when configured:

- `GROQ_API_KEY` - For Groq AI chat
- `OPENAI_API_KEY` - For OpenAI GPT chat  
- `ANTHROPIC_API_KEY` - For Claude AI chat
- `TAVILY_API_KEY` - For web scraping research

## 📊 Usage

1. Upload CSV or Excel files
2. Explore data with intelligent filters
3. Chat with your data using AI
4. Generate visualizations
5. Research business contacts (with API keys)
6. Export enhanced datasets

## 🚀 Deployment Options

- **Streamlit Cloud** (Recommended)
- **Heroku** (using Procfile)
- **Docker** (containerized deployment)
- **AWS/DigitalOcean** (VPS deployment)

See the deployment guide artifact for detailed instructions.

## 📝 License

MIT License - See LICENSE file for details.
