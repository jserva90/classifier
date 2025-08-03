import os
import tempfile
from loguru import logger

try:
    from unstructured.partition.pdf import partition_pdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

def extract_text_from_pdf(pdf_data_or_path, is_file_path=False):
    if not PDF_SUPPORT:
        raise ImportError("PDF support requires unstructured library. Install with: pip install unstructured[pdf]")
        
    try:
        if is_file_path:
            file_path = pdf_data_or_path
            temp_path = None
        else:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_data_or_path)
                temp_path = temp_file.name
                file_path = temp_path
        
        try:
            logger.info(f"Extracting text from PDF: {file_path}")
            elements = partition_pdf(
                filename=file_path,
                extract_images_in_pdf=False,
                infer_table_structure=False,
                strategy="fast"
            )
            
            raw_text = "\n".join([str(element) for element in elements])
            
            if not raw_text.strip():
                logger.warning("No text could be extracted from the PDF")
                return "No text could be extracted from the PDF file."
            
            logger.info(f"Extracted {len(raw_text)} characters from PDF")
            logger.debug(f"First 200 characters: {raw_text[:200]}")
            
            return raw_text
            
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")