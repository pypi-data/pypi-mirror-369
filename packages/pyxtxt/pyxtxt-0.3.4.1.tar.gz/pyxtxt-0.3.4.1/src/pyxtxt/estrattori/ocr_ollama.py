# pyxtxt/extractors/image_ocr_ollama.py
from . import register_extractor
from io import BytesIO
import base64

try:
    import ollama
    from PIL import Image
except ImportError:
    ollama = None
    Image = None

# Global configuration for Ollama model and parameters
OLLAMA_MODEL = "gemma3:4b"  # Default multimodal model
OLLAMA_CONFIG = {
    'language': 'auto',  # Language hint for caption generation
    'caption_length': 'medium',  # short, medium, long
    'style': 'descriptive',  # descriptive, technical, simple, detailed
    'temperature': 0.1,  # Response creativity (0.0-1.0)
    'max_tokens': 1500,  # Maximum response length
    'confidence_threshold': 0.7,  # Minimum confidence for text extraction
    'context': 'general'  # Context hint: general, cookbook, document, diagram, etc.
}

def set_ollama_model(model_name: str):
    """
    Set the Ollama model to use for OCR.
    
    Recommended multimodal models:
    - gemma3:4b (default, balanced speed/quality)
    - gemma3:12b (higher quality, slower)
    - gemma3:27b (best quality, very slow)
    - llava:7b (alternative vision model)
    - llava:13b (higher quality LLAVA)
    """
    global OLLAMA_MODEL
    OLLAMA_MODEL = model_name
    print(f"✅ Ollama OCR model set to: {model_name}")

def get_ollama_model():
    """Get current Ollama model name"""
    return OLLAMA_MODEL

def set_ollama_config(**kwargs):
    """
    Configure Ollama LLM parameters for better caption generation.
    
    Parameters:
    - language: Language hint ('auto', 'italian', 'english', 'spanish', etc.)
    - caption_length: Caption length ('short', 'medium', 'long')
    - style: Caption style ('descriptive', 'technical', 'simple', 'detailed')
    - context: Content context ('general', 'cookbook', 'document', 'handwriting', 'technical')
    - temperature: Response creativity 0.0-1.0 (default: 0.1)
    - max_tokens: Maximum response length (default: 1500)
    - confidence_threshold: Text extraction confidence 0.0-1.0 (default: 0.7)
    
    Examples:
        set_ollama_config(language='italian', style='detailed')
        set_ollama_config(context='document', caption_length='long')
        set_ollama_config(context='handwriting', temperature=0.2)
    """
    global OLLAMA_CONFIG
    for key, value in kwargs.items():
        if key in OLLAMA_CONFIG:
            OLLAMA_CONFIG[key] = value
            print(f"✅ Ollama config updated: {key} = {value}")
        else:
            print(f"⚠️ Unknown config parameter: {key}")

def get_ollama_config():
    """Get current Ollama configuration"""
    return OLLAMA_CONFIG.copy()

def reset_ollama_config():
    """Reset Ollama configuration to defaults"""
    global OLLAMA_CONFIG
    OLLAMA_CONFIG = {
        'language': 'auto',
        'caption_length': 'medium', 
        'style': 'descriptive',
        'temperature': 0.1,
        'max_tokens': 1500,
        'confidence_threshold': 0.7,
        'context': 'general'
    }
    print("✅ Ollama configuration reset to defaults")

def _calculate_confidence_score(content: str, mode: str) -> float:
    """
    Calculate confidence score (0.0-1.0) for OCR/caption quality.
    
    Evaluates response based on:
    - Content length and structure
    - Presence of meaningful text patterns
    - Absence of hallucination indicators
    - Appropriate response format
    """
    if not content or len(content.strip()) < 3:
        return 0.0
    
    content_lower = content.lower()
    score = 0.5  # Base score
    
    # Positive indicators (add to confidence)
    positive_patterns = [
        # Structured text indicators
        (r'\b\d+\b', 0.1, "Contains numbers/measurements"),
        (r'[.!?]', 0.1, "Has sentence punctuation"), 
        (r'\b(the|and|of|in|to|for|with|on|at|by)\b', 0.1, "Common words present"),
        (r'\b[A-Z][a-z]+\b', 0.1, "Proper capitalization"),
        (r'[,;:]', 0.05, "Has proper punctuation"),
        
        # Content-specific indicators
        (r'\b(text|document|page|title|heading)\b', 0.1, "Document references"),
        (r'\b(image|photo|picture|shows|contains)\b', 0.1, "Visual descriptions"),
        (r'\b\d+[%$€£¥]\b|\b[%$€£¥]\d+\b', 0.1, "Currency/percentages"),
        (r'\b\d{1,2}[:/]\d{1,2}\b|\b\d{4}\b', 0.05, "Times/years"),
    ]
    
    # Negative indicators (reduce confidence) 
    negative_patterns = [
        # Historical/Archaeological hallucinations (common with X-rays, scans)
        ("ancient", 0.2, "May be hallucinating historical content"),
        ("egypt", 0.15, "Egyptian hallucination"),
        ("hieroglyph", 0.25, "Hieroglyphic hallucination"),
        ("papyrus", 0.2, "Papyrus hallucination"),
        ("scroll", 0.1, "Ancient scroll hallucination"),
        ("medieval", 0.15, "Medieval hallucination"),
        ("manuscript", 0.1, "Manuscript hallucination"),
        ("archaeological", 0.15, "Archaeological hallucination"),
        ("artifact", 0.12, "Artifact hallucination"),
        ("roman", 0.1, "Roman historical hallucination"),
        ("greek", 0.1, "Greek historical hallucination"),
        ("biblical", 0.15, "Religious historical hallucination"),
        ("stone tablet", 0.2, "Stone tablet hallucination"),
        ("carved", 0.1, "Carving hallucination"),
        
        # Art/Cultural hallucinations (common with medical images, diagrams)
        ("painting", 0.1, "Artistic interpretation hallucination"),
        ("artwork", 0.12, "Artwork hallucination"),  
        ("masterpiece", 0.15, "Art masterpiece hallucination"),
        ("renaissance", 0.15, "Renaissance art hallucination"),
        ("portrait", 0.08, "Portrait hallucination"),
        ("landscape", 0.08, "Landscape hallucination"),
        ("abstract art", 0.12, "Abstract art hallucination"),
        
        # Fantasy/Fictional content (can occur with any unclear image)
        ("mystical", 0.15, "Fantasy content hallucination"),
        ("magical", 0.15, "Magical content hallucination"),
        ("mythological", 0.15, "Mythology hallucination"),
        ("fairy tale", 0.15, "Fairy tale hallucination"),
        ("legend", 0.1, "Legend/folklore hallucination"),
        ("dragon", 0.2, "Dragon hallucination"),
        ("wizard", 0.15, "Fantasy character hallucination"),
        
        # Scientific misinterpretations (X-rays as geological, etc.)
        ("fossil", 0.15, "Fossil hallucination"),
        ("geological", 0.1, "Geological misinterpretation"),
        ("mineral", 0.1, "Mineral hallucination"),
        ("crystal", 0.1, "Crystal hallucination"),
        ("rock formation", 0.12, "Rock formation hallucination"),
        ("sediment", 0.1, "Sediment hallucination"),
        
        # Vague/uncertain language
        ("unclear", 0.1, "Uncertainty indicator"),
        ("difficult to read", 0.1, "Reading difficulty"),
        ("appears to be", 0.05, "Tentative language"),
        ("seems to", 0.05, "Uncertain language"),
        ("might be", 0.1, "Possibility language"),
        ("possibly", 0.1, "Uncertain language"),
        ("probably", 0.08, "Probability language"),
        ("looks like", 0.08, "Appearance-based guess"),
        ("reminds me of", 0.1, "Subjective association"),
        ("similar to", 0.05, "Similarity guess"),
        
        # Quality/visibility issues (legitimate but indicate uncertainty)
        ("blurry", 0.05, "Image quality issue"),
        ("faded", 0.05, "Faded content"),
        ("damaged", 0.05, "Damaged content"),
        ("corrupted", 0.1, "Corrupted content"),
        ("low resolution", 0.08, "Resolution issue"),
        ("hard to make out", 0.1, "Visibility issue"),
        
        # Generic/evasive responses
        ("sorry, i cannot", 0.3, "Refusal response"),
        ("cannot determine", 0.2, "Unable to process"),
        ("unable to identify", 0.15, "Identification failure"),
        ("not clear enough", 0.1, "Clarity issue"),
        ("too dark", 0.08, "Darkness issue"),
        ("too bright", 0.08, "Brightness issue"),
        ("no visible text", 0.0, "No text found - appropriate response"),
        
        # Repetitive/nonsensical content (AI breakdown indicators)
        ("lorem ipsum", 0.2, "Placeholder text hallucination"),
        ("test test test", 0.25, "Repetitive test pattern"),
        ("abc abc abc", 0.2, "Repetitive pattern"),
        ("error error", 0.15, "Error message hallucination"),
    ]
    
    import re
    
    # Apply positive pattern scoring
    for pattern, bonus, description in positive_patterns:
        if re.search(pattern, content_lower):
            score += bonus
    
    # Apply negative pattern scoring  
    for pattern, penalty, description in negative_patterns:
        if pattern in content_lower:
            score -= penalty
            print(f"⚠️ Confidence penalty ({penalty}): {description}")
    
    # Length-based adjustments
    if len(content) > 200:  # Substantial content
        score += 0.1
    elif len(content) < 20:  # Very short responses are suspicious
        score -= 0.2
    
    # Mode-specific adjustments
    if mode == "describe":
        # Check for proper formatting in describe mode
        if "TEXT:" in content and "DESCRIPTION:" in content:
            score += 0.1  # Proper format bonus
        elif len(content) > 50:  # Has substantial descriptive content
            score += 0.05
    
    # Context coherence check - very basic
    words = content_lower.split()
    if len(words) > 5:
        # Check for repetitive patterns (hallucination indicator)
        unique_words = set(words)
        repetition_ratio = len(unique_words) / len(words)
        if repetition_ratio < 0.3:  # Too repetitive
            score -= 0.2
    
    # Clamp to valid range
    return max(0.0, min(1.0, score))

if ollama and Image:
    def xtxt_image_ocr_ollama(file_buffer, mode="ocr", model=None):
        """
        Extract text from images using Ollama with multimodal models.
        
        Args:
            file_buffer: Image file buffer
            mode: "ocr" (text only) or "describe" (text + description)  
            model: Override default model (optional)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            # Reset buffer position if it has read method
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Get current configuration
            config = OLLAMA_CONFIG
            
            # Build language hint
            lang_hint = ""
            if config['language'] != 'auto':
                lang_hint = f"Text language: {config['language']}. "
            
            # Different prompts based on mode
            if mode == "ocr":
                prompt = f"""Look carefully at this image and extract ALL text that you can see, including:
- Titles, headings, and main text content  
- Small print, captions, labels, and annotations
- Numbers, measurements, quantities, and symbols
- Menu items, ingredient lists, cooking instructions
- Any text in boxes, speech bubbles, or decorative elements

IMPORTANT: 
- Read carefully and include even small or partially visible text
- Preserve the original formatting and line breaks where possible
- {lang_hint}Process the text from left to right, top to bottom
- If you cannot find any readable text at all, respond with 'NO_TEXT_FOUND'

Extracted text:"""
            
            else:  # mode == "describe"
                # Build style-specific prompts
                style_prompts = {
                    'descriptive': "Provide a clear, descriptive explanation",
                    'technical': "Use technical terminology and precise descriptions", 
                    'simple': "Use simple, easy-to-understand language",
                    'detailed': "Provide comprehensive details about all visual elements"
                }
                
                length_hints = {
                    'short': "Keep descriptions brief (1-2 sentences)",
                    'medium': "Provide moderate detail (2-4 sentences)",
                    'long': "Give comprehensive descriptions (4-8 sentences)"
                }
                
                style_instruction = style_prompts.get(config['style'], style_prompts['descriptive'])
                length_instruction = length_hints.get(config['caption_length'], length_hints['medium'])
                
                # Context-specific hints (only when explicitly set)
                context_hint = ""
                context = config.get('context', 'general').lower()
                if context == 'cookbook' or context == 'recipe':
                    context_hint = """
   - If this appears to be a recipe/cookbook page, include: ingredients, cooking steps, quantities, cooking times
   - Mention any photos of prepared dishes or cooking techniques shown
   - Note any special formatting like ingredient lists, step numbers, or cooking tips"""
                elif context == 'document':
                    context_hint = """
   - Focus on document structure: headers, paragraphs, sections, page numbers
   - Note any official formatting, letterheads, signatures, or stamps"""
                elif context == 'handwriting' or context == 'notes':
                    context_hint = """
   - Pay special attention to handwritten text which may be harder to read
   - Note any sketches, diagrams, or informal formatting typical of personal notes"""
                elif context == 'technical' or context == 'diagram':
                    context_hint = """
   - Focus on technical elements: labels, measurements, specifications, diagrams
   - Include any mathematical formulas, technical symbols, or engineering notations"""

                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written (preserve formatting, line breaks, bullet points)
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context{context_hint}

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [image description following the guidelines above]"""
            
            # Send request to Ollama with configured parameters
            response = ollama.generate(
                model=current_model,
                prompt=prompt,
                images=[img_base64],
                options={
                    'temperature': config['temperature'],
                    'top_p': 0.9,
                    'num_predict': config['max_tokens']
                }
            )
            
            # Extract and clean response
            extracted_content = response.get('response', '').strip()
            
            # Calculate confidence score based on response quality indicators
            confidence_score = _calculate_confidence_score(extracted_content, mode)
            
            # Check confidence threshold
            if confidence_score < config['confidence_threshold']:
                print(f"⚠️ Low confidence ({confidence_score:.2f} < {config['confidence_threshold']}): {extracted_content[:100]}...")
                if mode == "ocr":
                    return ""  # Return empty for OCR if below threshold
                else:
                    # For describe mode, add warning prefix
                    extracted_content = f"[LOW_CONFIDENCE_{confidence_score:.2f}] {extracted_content}"
            else:
                print(f"✅ Good confidence ({confidence_score:.2f}): Processing successful")
            
            # Handle no-text case for OCR mode
            if mode == "ocr" and ('NO_TEXT_FOUND' in extracted_content or len(extracted_content) < 3):
                return ""
            
            return extracted_content
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return ""
    
    def xtxt_image_ocr_ollama_with_confidence(file_buffer, mode="ocr", model=None):
        """
        Version of OCR-Ollama that returns both text and confidence score.
        
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Get current configuration
            config = OLLAMA_CONFIG
            
            # Build prompts (same logic as main function)
            lang_hint = ""
            if config['language'] != 'auto':
                lang_hint = f"Text language: {config['language']}. "
            
            if mode == "ocr":
                prompt = f"""Look carefully at this image and extract ALL text that you can see, including:
- Titles, headings, and main text content  
- Small print, captions, labels, and annotations
- Numbers, measurements, quantities, and symbols
- Menu items, ingredient lists, cooking instructions
- Any text in boxes, speech bubbles, or decorative elements

IMPORTANT: 
- Read carefully and include even small or partially visible text
- Preserve the original formatting and line breaks where possible
- {lang_hint}Process the text from left to right, top to bottom
- If you cannot find any readable text at all, respond with 'NO_TEXT_FOUND'

Extracted text:"""
            else:  # describe mode
                style_prompts = {
                    'descriptive': "Provide a clear, descriptive explanation",
                    'technical': "Use technical terminology and precise descriptions", 
                    'simple': "Use simple, easy-to-understand language",
                    'detailed': "Provide comprehensive details about all visual elements"
                }
                
                length_hints = {
                    'short': "Keep descriptions brief (1-2 sentences)",
                    'medium': "Provide moderate detail (2-4 sentences)",
                    'long': "Give comprehensive descriptions (4-8 sentences)"
                }
                
                style_instruction = style_prompts.get(config['style'], style_prompts['descriptive'])
                length_instruction = length_hints.get(config['caption_length'], length_hints['medium'])
                
                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written (preserve formatting, line breaks, bullet points)
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [image description following the guidelines above]"""
            
            # Send request to Ollama
            response = ollama.generate(
                model=current_model,
                prompt=prompt,
                images=[img_base64],
                options={
                    'temperature': config['temperature'],
                    'top_p': 0.9,
                    'num_predict': config['max_tokens']
                }
            )
            
            # Extract response
            extracted_content = response.get('response', '').strip()
            
            # Calculate confidence without threshold filtering
            confidence_score = _calculate_confidence_score(extracted_content, mode)
            
            # Return both text and confidence
            return extracted_content, confidence_score
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return "", 0.0

    # Wrapper functions for each mode
    def xtxt_image_ocr_only(file_input):
        """Traditional OCR: extract only visible text using Ollama"""
        # Handle both file paths and buffers
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="ocr")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="ocr")
    
    def xtxt_image_describe(file_input):
        """OCR + Description: text + image context using Ollama"""
        # Handle both file paths and buffers  
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="describe")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="describe")

    def xtxt_image_with_confidence(file_input, mode="ocr"):
        """Get both text and confidence score from image OCR"""
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama_with_confidence(f, mode=mode)
        else:
            return xtxt_image_ocr_ollama_with_confidence(file_input, mode=mode)
    
    # Register OCR-only version as default
    # Note: Will override traditional EasyOCR if both modules are loaded
    image_formats = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    for format_type in image_formats:
        register_extractor(format_type, xtxt_image_ocr_only, name="OCR-Ollama")