"""
Helper Functions for Intelligent Product System
"""

import re
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib

def normalize_text(text: str) -> str:
    """
    Normalize text for comparison
    
    Args:
        text: Input text
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_json_from_text(text: str) -> Optional[Union[Dict, List]]:
    """
    Extract JSON from text that may contain other content
    
    Args:
        text: Text that may contain JSON
    
    Returns:
        Extracted JSON object or None
    """
    if not text:
        return None
    
    # Try to find JSON array or object
    json_patterns = [
        r'\[.*\]',  # JSON array
        r'\{.*\}',  # JSON object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # If no JSON found, try to parse the entire text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using normalized text
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def deduplicate_products(products: List[Dict], threshold: float = 0.8) -> List[Dict]:
    """
    Remove duplicate products based on name similarity
    
    Args:
        products: List of product dictionaries
        threshold: Similarity threshold for deduplication
    
    Returns:
        Deduplicated product list
    """
    if not products:
        return []
    
    deduplicated = []
    seen_hashes = set()
    
    for product in products:
        name = product.get('name', '')
        if not name:
            continue
        
        # Create hash for quick comparison
        name_hash = hashlib.md5(normalize_text(name).encode()).hexdigest()
        
        # Check if we've seen this exact name
        if name_hash in seen_hashes:
            continue
        
        # Check similarity with existing products
        is_duplicate = False
        for existing_product in deduplicated:
            existing_name = existing_product.get('name', '')
            similarity = calculate_similarity(name, existing_name)
            
            if similarity >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduplicated.append(product)
            seen_hashes.add(name_hash)
    
    return deduplicated

def format_product_list(products: List[Dict], start_index: int = 1) -> str:
    """
    Format product list for display
    
    Args:
        products: List of product dictionaries
        start_index: Starting index for numbering
    
    Returns:
        Formatted string
    """
    if not products:
        return "No products found"
    
    formatted = []
    for i, product in enumerate(products, start_index):
        name = product.get('name', 'Unknown')
        description = product.get('description', '')
        
        formatted.append(f"{i}. {name}")
        if description and description != 'null':
            formatted.append(f"   Description: {description}")
    
    return "\n".join(formatted)

def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary
    
    Args:
        dictionary: Input dictionary
        key: Key to get
        default: Default value if key not found
    
    Returns:
        Value or default
    """
    return dictionary.get(key, default)

def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
    """
    Validate required fields in data
    
    Args:
        data: Data dictionary
        required_fields: List of required field names
    
    Returns:
        List of missing field names
    """
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)
    
    return missing

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Timestamp to format
    
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

async def run_with_timeout(coro, timeout: float) -> Any:
    """
    Run coroutine with timeout
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
    
    Returns:
        Coroutine result
    
    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Operation timed out after {timeout} seconds")

def create_session_id() -> str:
    """
    Create unique session ID
    
    Returns:
        Unique session ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(datetime.now().microsecond).encode()).hexdigest()[:8]
    return f"session_{timestamp}_{random_suffix}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename.strip('_.')

def format_price(price: Union[str, float, int]) -> str:
    """
    Format price for display
    
    Args:
        price: Price value
    
    Returns:
        Formatted price string
    """
    if not price:
        return "Price unknown"
    
    try:
        if isinstance(price, str):
            # Extract numeric value from string
            numeric_price = re.search(r'[\d.,]+', price)
            if numeric_price:
                price = float(numeric_price.group().replace(',', ''))
            else:
                return price
        
        return f"${price:.2f} CAD"
    except (ValueError, TypeError):
        return str(price) 