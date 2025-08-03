# Legal Clause Classifier

A powerful tool for classifying legal clauses in contracts and legal documents using OpenAI's language models.

## Features

- **Automatic Clause Detection**: Intelligently splits text into individual clauses for precise classification
- **Multiple Classification Categories**: Identifies various clause types including Termination, Confidentiality, Governing Law, and more
- **Confidence Scoring**: Provides calibrated confidence scores with explanations (Very High, High, Moderate, Low, Very Low)
- **Plain English Summaries**: Generates concise explanations of each clause in simple language
- **Document Summary**: Provides an overall summary of the document's contents
- **Multiple Interfaces**: Use as a CLI tool, API server, or import as a Python library
- **Model Selection**: Choose between GPT-4.1 and GPT-4.1-mini for cost/performance tradeoffs
- **Multiple File Formats**: Support for plain text (.txt) and PDF (.pdf) files

## Package Structure

The classifier is organized into a modular package structure:

```
classifier/
├── __init__.py        # Package exports
├── core.py           # Main entry point
├── models.py         # Model definitions and constants
├── text_processing.py # Text cleaning and clause splitting
├── api_models.py # Pydantic models for API requests/responses
├── api_classification.py # OpenAI API-based classification
└── pdf_extraction.py # PDF text extraction utilities
```

## Setup

1. Install uv (if not already installed):
```bash
# Using pip
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using cargo (Rust package manager)
cargo install uv
```

2. Install dependencies:
```bash
uv sync
```

3. Set up your environment:
```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file to add your OpenAI API key
nano .env  # or use any text editor
```

## Usage Options

### Option 1: Command Line Interface (CLI)

```bash
# Basic usage with text input
uv run python main.py --text "this agreement shall stay in effect until one party ends it with 30 days' notice."

# Using a text file as input
uv run python main.py --file documents/test_legal.txt

# Using a PDF file as input
uv run python main.py --file documents/test.pdf

# Output to JSON format
uv run python main.py --file documents/test_legal.txt --json

# Save output to a file
uv run python main.py --file documents/test_legal.txt --output results.txt

# Use GPT-4.1-mini for faster, cheaper classification
uv run python main.py --file documents/test_legal.txt --model gpt-4.1-mini-2025-04-14

# Specify custom clause types to look for
uv run python main.py --file documents/test_legal.txt --clause-types "Payment" "Delivery" "Warranty"
```

### Option 2: API Server

Start the server:

```bash
# Run the API server
uv run python api.py
```

The server will run on http://localhost:5000 by default.

## API Endpoints

The API uses Pydantic models for request and response validation, ensuring type safety and better documentation.

### Health Check

```
GET /health
```

Returns status information about the API, including version and supported models.

**Response Model: `HealthResponse`**

```json
{
  "status": "ok",
  "version": "0.3.0",
  "supported_models": ["gpt-4.1", "gpt-4.1-mini-2025-04-14"],
  "default_clause_types": ["Termination", "Confidentiality", "Governing Law", "Payment Terms", "Liability", "Intellectual Property"],
  "pdf_support": true
}
```

### Classify Legal Text

```
POST /classify
Content-Type: application/json
```

**Request Model: `ClassifyRequest`**

You can provide either text or a PDF document:

```json
{
  "text": "this agreement shall stay in effect until one party ends it with 30 days' notice.",
  "pdf_base64": null,
  "model": "gpt-4.1",
  "clause_types": ["Termination", "Confidentiality"]
}
```

Or with a PDF document:

```json
{
  "text": null,
  "pdf_base64": "JVBERi0xLjcKJcfs...",
  "model": "gpt-4.1",
  "clause_types": ["Termination", "Confidentiality"]
}
```

**Response Model: `ClassifyResponse`**

```json
{
  "results": [
    {
      "clause": "this agreement shall stay in effect until one party ends it with 30 days' notice.",
      "label": "Termination",
      "confidence": 0.95,
      "confidence_level": "Very High",
      "summary": "This clause specifies that the agreement remains valid until terminated by either party with 30 days' notice."
    }
  ],
  "document_summary": "This document contains 1 Termination clause.",
  "metadata": {
    "model": "gpt-4.1",
    "clause_count": 1,
    "clause_types": ["Termination", "Confidentiality", "Governing Law", "Payment Terms", "Liability", "Intellectual Property"]
  },
  "error": null
}
```

In case of an error:

```json
{
  "results": [],
  "document_summary": null,
  "metadata": null,
  "error": "PDF processing error: Invalid PDF format"
}
```

## Example Usage with curl

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "this agreement shall stay in effect until one party ends it with 30 days notice. both sides agree to keep information confidential for two years after the agreement ends."}'

# With a PDF file (base64-encoded)
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"pdf_base64": "'$(base64 -w 0 documents/test.pdf)'", "model": "gpt-4.1"}'
```

## Jupyter Notebook Demo

A Jupyter notebook demo is included to showcase the classifier's capabilities:

```bash
# Install Jupyter
uv pip install notebook

# Run the notebook server
cd /path/to/classifier && uv run jupyter notebook
```

Then open `demo_classifier.ipynb` in your browser to see examples of:
- Basic classification
- Custom clause types
- Model comparison (GPT-4.1 vs GPT-4.1-mini)
- Complex contract analysis
- Visualization of results

## How Confidence Scoring Works

The confidence scoring system combines multiple factors:

1. **Model-Generated Score**: The base confidence score is generated by the language model based on how clearly a clause fits into a category.

2. **Calibration**: Scores are post-processed to ensure they're well-calibrated:
   - **0.9-1.0**: Very High confidence - Clear and unambiguous classification
   - **0.7-0.9**: High confidence - Strong indicators of the category
   - **0.5-0.7**: Moderate confidence - Some indicators but potential ambiguity
   - **0.3-0.5**: Low confidence - Weak indicators or multiple possible categories
   - **0.0-0.3**: Very Low confidence - Unclear or unusual clause

3. **Explanation**: Each confidence score includes a human-readable confidence level to aid interpretation.

## Docker Support

The classifier can be run in a Docker container for easy deployment and consistent environments.

### Using Docker Compose (Recommended)

```bash
# Build the Docker image
docker compose -f docker/docker-compose.yml build

# Start the API server
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f

# Stop the container
docker compose -f docker/docker-compose.yml down

# Run the CLI with a text file
docker compose -f docker/docker-compose.yml run --rm classifier-cli --file documents/test.txt

# Run the CLI with a PDF file
docker compose -f docker/docker-compose.yml run --rm classifier-cli --file documents/test.pdf

# Run the CLI with custom clause types
docker compose -f docker/docker-compose.yml run --rm classifier-cli --file documents/test.txt --clause-types "Payment" "Delivery" "Warranty"

# Run the CLI with a different model
docker compose -f docker/docker-compose.yml run --rm classifier-cli --file documents/test.txt --model gpt-4.1-mini-2025-04-14
```

### Using Docker Directly

```bash
# Build the Docker image
docker build -t legal-clause-classifier -f docker/Dockerfile .

# Run the API container
docker run -p 5000:5000 -v $(pwd)/.env:/app/.env -v $(pwd)/documents:/app/documents -v $(pwd)/output:/app/output legal-clause-classifier

# Run the CLI with a text file
docker run --rm -v $(pwd)/.env:/app/.env -v $(pwd)/documents:/app/documents -v $(pwd)/output:/app/output legal-clause-classifier python main.py --file documents/test.txt

# Run the CLI with a PDF file
docker run --rm -v $(pwd)/.env:/app/.env -v $(pwd)/documents:/app/documents -v $(pwd)/output:/app/output legal-clause-classifier python main.py --file documents/test.pdf
```

### Environment Variables

When running with Docker, you can configure the application using environment variables:

- `HOST`: Host to bind the API server (default: 0.0.0.0)
- `PORT`: Port to run the API server (default: 5000)
- `DEBUG`: Enable debug mode (default: false)
- `OPENAI_API_KEY`: Your OpenAI API key

These can be set in the docker-compose.yml file or passed directly to the docker run command.

### PDF Support in Docker

The Docker container includes all necessary dependencies for PDF processing:
- poppler-utils for PDF rendering
- tesseract-ocr for OCR capabilities
- libmagic1 and file for MIME type detection
- OpenCV dependencies for layout detection

This allows you to process PDF files directly through both the API and CLI interfaces without installing additional system dependencies.

## Future Improvements

With more time, the following enhancements could be made:

- **Multi-label Classification**: Allow clauses to belong to multiple categories with separate confidence scores
- **Custom Model Fine-tuning**: Train a specialized model on legal texts for improved accuracy
- **Clause Highlighting**: Return character offsets to highlight clauses in the original text
- **Batch Processing**: Support for processing multiple documents in batch mode
- **Interactive UI**: Web interface for uploading and analyzing documents
- **Export Options**: Support for exporting results in various formats (PDF, DOCX, etc.)
- **Comparison Feature**: Compare clauses across multiple contracts
- **Additional File Formats**: Support for more document formats (DOCX, RTF, etc.)