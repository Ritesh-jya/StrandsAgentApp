# StrandsAgentApp

A Python-based Strands-style agent scaffold that fetches customer feedback for a product from Amazon.in and summarizes it via the Gemini API.

## Setup

1. Install Python 3.10+.
2. Create and activate a virtual environment inside `StrandsAgentApp`:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install from `pyproject.toml`:
   ```bash
   pip install .
   ```
4. Copy your Gemini API key into `.env`:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   GEMINI_METHOD=generateContent
   GEMINI_ENDPOINT=https://generativelanguage.googleapis.com/v1beta
   AMAZON_COUNTRY_CODE=in
   ```

   If you already have a full Gemini endpoint URL, you can set `GEMINI_ENDPOINT` to a complete path such as
   `https://gemini.googleapis.com/v1/models/gemini-1.5:generate`.

## Usage

Run the agent from the project root:
```bash
python src/main.py
```

Enter a product name when prompted, and the agent will search Amazon.in, retrieve review excerpts, and summarize customer feedback.

## Files created

- `.env` — Gemini API configuration template
- `pyproject.toml` — Python project metadata and dependencies
- `src/strands_agent_app/config.py` — settings loader
- `src/strands_agent_app/gemini_client.py` — Gemini API adapter
- `src/strands_agent_app/tools/amazon_feedback_tool.py` — Amazon.in review fetcher
- `src/strands_agent_app/agent.py` — agent orchestration logic
- `src/strands_agent_app/pdf_report.py` — PDF report generator
- `src/main.py` — CLI entrypoint

## PDF report output

After the agent prints the summary, choose `y` to save a PDF report. The generated PDF includes:
- product name and ASIN
- live Amazon.in product link
- Gemini summary of customer sentiment
- a table of review ratings and excerpts

## Notes

- The Gemini API endpoint is configured in `.env`.
- Amazon scraping uses simple HTML parsing and may require a real browser user agent.
- This is a generic Strands-style scaffold and may be adapted to a concrete AWS Strands SDK later.
