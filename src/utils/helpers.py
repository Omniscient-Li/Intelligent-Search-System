#!/usr/bin/env python3
"""
Helper Functions Module
Provides common utility functions
"""

import re
import json
import pandas as pd
from typing import List, Dict, Any, Optional

def safe_str(value: Any) -> str:
    """Safely convert to string, handling NaN values"""
    if pd.isna(value) or isinstance(value, float):
        return ''
    return str(value)

def extract_json_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract JSON data from text"""
    try:
        # Find JSON array
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            json_str = json_str.replace('\n', ' ').replace('    ', ' ')
            return json.loads(json_str)
        
        # Find single JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            json_str = json_str.replace('\n', ' ').replace('    ', ' ')
            return [json.loads(json_str)]
        
        return []
    except Exception as e:
        print(f"JSON extraction failed: {e}")
        return []

def flatten_products(data: Any) -> List[Dict[str, Any]]:
    """Recursively extract all product objects, including nested product_variants"""
    products = []
    
    if isinstance(data, list):
        for item in data:
            products.extend(flatten_products(item))
    elif isinstance(data, dict):
        # If it's a product object
        if all(k in data for k in ("name", "product_url")):
            products.append(data)
        # If there are product_variants
        if "product_variants" in data and isinstance(data["product_variants"], list):
            products.extend(flatten_products(data["product_variants"]))
        # If there are variants
        if "variants" in data and isinstance(data["variants"], list):
            products.extend(flatten_products(data["variants"]))
    
    return products

def is_fuzzy_query(query: str, products: List[Dict[str, Any]]) -> bool:
    """Check if it's a fuzzy query"""
    query_clean = query.strip().lower()
    
    for product in products:
        name = product.get('name', product.get('Product Name', ''))
        if pd.isna(name) or str(name) == 'nan':
            continue
        name = str(name).strip().lower()
        if query_clean == name:
            return False
    
    return True

def format_price(price: Any) -> str:
    """Format price display"""
    if pd.isna(price) or price is None:
        return "Price not shown"
    
    price_str = str(price).strip()
    if not price_str or price_str == 'nan':
        return "Price not shown"
    
    return price_str

def format_description(description: str, max_length: int = 200) -> str:
    """Format description text"""
    if pd.isna(description) or not description:
        return "No description available"
    
    desc = str(description).strip()
    if len(desc) > max_length:
        return desc[:max_length] + "..."
    
    return desc

def validate_product_data(product: Dict[str, Any]) -> bool:
    """Validate product data completeness"""
    required_fields = ['name', 'product_url']
    
    for field in required_fields:
        if field not in product or pd.isna(product[field]):
            return False
    
    return True

def clean_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """Clean product data, remove NaN values"""
    cleaned = {}
    
    for key, value in product.items():
        if not pd.isna(value) and value is not None:
            cleaned[key] = value
    
    return cleaned

def merge_product_variants(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge product variant information"""
    merged_products = []
    
    for product in products:
        # If there's variant information, expand variants
        if 'variants' in product and isinstance(product['variants'], list):
            for variant in product['variants']:
                merged_product = product.copy()
                merged_product.update(variant)
                merged_products.append(merged_product)
        else:
            merged_products.append(product)
    
    return merged_products

def calculate_similarity_score(distance: float) -> float:
    """Calculate similarity score"""
    return 1 / (1 + distance)

def sort_products_by_relevance(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort products by relevance"""
    def sort_key(product):
        score = product.get('similarity_score', 0)
        # Online products prioritized
        source_bonus = 0.1 if product.get('source') == 'browser-use' else 0
        return score + source_bonus
    
    return sorted(products, key=sort_key, reverse=True)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text"""
    if not text or pd.isna(text):
        return ""
    
    text_str = str(text).strip()
    if len(text_str) <= max_length:
        return text_str
    
    return text_str[:max_length] + "..."

def format_dimensions(dimensions: Any) -> str:
    """Format dimension information"""
    if pd.isna(dimensions) or not dimensions:
        return "Dimension information not provided"
    
    if isinstance(dimensions, dict):
        parts = []
        for key, value in dimensions.items():
            if value and not pd.isna(value):
                parts.append(f"{key}: {value}")
        return ", ".join(parts) if parts else "Dimension information not provided"
    
    return str(dimensions)

def fill_missing_product_fields(product: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required product fields are present, fill missing with default values."""
    required_fields = [
        'name', 'price', 'image_url', 'product_url', 'description', 'sku', 'dimensions',
        'material', 'finish', 'installation', 'weight', 'package_contents',
        'technical_specs', 'certifications', 'warranty', 'source', 'search_query', 'search_time'
    ]
    defaults = {
        'name': 'Unknown Product',
        'price': 'Price not shown',
        'image_url': '',
        'product_url': '',
        'description': 'No description available',
        'sku': '',
        'dimensions': '',
        'material': '',
        'finish': '',
        'installation': '',
        'weight': '',
        'package_contents': '',
        'technical_specs': '',
        'certifications': '',
        'warranty': '',
        'source': '',
        'search_query': '',
        'search_time': ''
    }
    filled = product.copy()
    for field in required_fields:
        if field not in filled or pd.isna(filled[field]) or filled[field] is None:
            filled[field] = defaults[field]
    return filled 