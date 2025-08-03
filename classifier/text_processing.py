import re
from loguru import logger

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("Downloading NLTK punkt tokenizer")
        nltk.download('punkt', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    logger.warning("NLTK not available, falling back to simple regex-based sentence splitting")
    NLTK_AVAILABLE = False
    sent_tokenize = None

def clean_text(text: str) -> str:
    if text.startswith("Legal Document Text:"):
        text = text[len("Legal Document Text:"):].strip()
    
    text = ''.join(char for char in text if char.isalnum() or char.isspace() or char in ".,;:()[]{}'-")
    
    text = text.replace('"', "'")
    
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    for para in paragraphs:
        cleaned = re.sub(r' {2,}', ' ', para).strip()
        if cleaned:
            cleaned_paragraphs.append(cleaned)
    
    return '\n\n'.join(cleaned_paragraphs)

def split_into_clauses(text: str) -> list:
    text = clean_text(text)
    
    if not NLTK_AVAILABLE:
        logger.debug("Using regex-based sentence splitting")
        sentences = re.split(r'(?<=[.!?])\s+', text)
    else:
        logger.debug("Using NLTK for sentence splitting")
        sentences = nltk.sent_tokenize(text)
    
    clauses = []
    for sentence in sentences:
        sub_clauses = re.split(r';\s*', sentence)
        clauses.extend([clause.strip() for clause in sub_clauses if clause.strip()])
    
    return clauses