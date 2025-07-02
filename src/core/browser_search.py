#!/usr/bin/env python3
"""
Browser-use Search Module
Provides online search functionality based on browser automation
"""

import os
import time
import re
import json
from typing import List, Dict, Any

# Import Browser-use integration
try:
    from browser_use import Agent
    from langchain_openai import AzureChatOpenAI
    BROWSER_USE_AVAILABLE = True
except ImportError as e:
    BROWSER_USE_AVAILABLE = False
    print(f"❌ Browser-use not available: {e}")
    print("Please install: pip install browser-use langchain-openai")

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import extract_json_from_text, flatten_products

class BrowserUseSearch:
    """Browser-use Search Class"""
    
    def __init__(self):
        """Initialize Browser-use search"""
        if not BROWSER_USE_AVAILABLE:
            raise ValueError("Browser-use is not available")
        
        # Validate configuration
        config.validate_config()
        
        # Create Azure OpenAI LLM object
        azure_config = config.get_azure_config()
        self.llm = AzureChatOpenAI(
            azure_deployment=azure_config['deployment_name'],
            openai_api_version=azure_config['api_version'],
            azure_endpoint=azure_config['endpoint'],
            api_key=azure_config['api_key'],
            temperature=0.1
        )
    
    async def search_products(self, query: str, max_products: int = 5) -> List[Dict[str, Any]]:
        """
        Search Richelieu products using Browser-use
        
        Args:
            query (str): Search query
            max_products (int): Maximum number of products
            
        Returns:
            list: Product list
        """
        logger.browser_search_start(query)
        
        task = f"""
        Go to {config.richelieu_url}
        
        1. Click the "Sign In" or "Login" button on the homepage.
        2. Enter the following credentials:
           - Username/Email: {config.login_email}
           - Password: {config.login_password}
        3. Submit the login form and wait for the login to complete.
        4. After successful login, search for "{query}" in the Richelieu catalog.
        5. For the top {max_products} most relevant products, click on each product to view detailed information.
        6. For each product, extract the following detailed information:
           - Product name (exact title)
           - Price (with currency)
           - Product image URL
           - Direct product page URL
           - Detailed product description
           - SKU/Product code
           - Dimensions (length, width, height, thickness, etc.)
           - Material information
           - Finish/Color options
           - Installation requirements
           - Weight (if available)
           - Package contents
           - Technical specifications
           - Certifications or standards (if any)
           - Warranty information (if available)
        7. Return the result as a JSON array with this enhanced structure:
        [
          {{
            "name": "Product Name",
            "price": "Price with currency or null",
            "image_url": "Image URL or null",
            "product_url": "Product page URL",
            "description": "Detailed product description",
            "sku": "Product SKU or null",
            "dimensions": "Dimensions information (L x W x H, etc.)",
            "material": "Material information",
            "finish": "Finish/Color options",
            "installation": "Installation requirements",
            "weight": "Weight information or null",
            "package_contents": "What's included in the package",
            "technical_specs": "Technical specifications",
            "certifications": "Certifications or standards",
            "warranty": "Warranty information or null"
          }}
        ]
        If no products found, return empty array [].
        
        IMPORTANT: Extract as much detailed information as possible from the product pages. This information will be used to provide comprehensive recommendations to customers.
        """
        
        try:
            start_time = time.time()
            agent = Agent(task=task, llm=self.llm)
            result = await agent.run()
            end_time = time.time()
            
            duration = end_time - start_time
            logger.browser_search_complete(query, 0, duration)  # Temporarily set to 0, will update later
            
            # Parse results
            products = self._extract_json_from_result(result)
            
            # Add metadata
            for product in products:
                product['source'] = 'browser-use'
                product['search_query'] = query
                product['search_time'] = duration
            
            # Update product count in logs
            logger.browser_search_complete(query, len(products), duration)
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Browser-use search failed: {e}")
            return []
    
    def _extract_json_from_result(self, result_content: Any) -> List[Dict[str, Any]]:
        """Extract JSON data from Browser-use results, supporting multiple return formats and nested structures"""
        try:
            # 1. Direct list
            if isinstance(result_content, list):
                return flatten_products(result_content)
            
            # 2. String and file path, try to read
            if isinstance(result_content, str):
                if result_content.strip().endswith('.md') and os.path.exists(result_content.strip()):
                    with open(result_content.strip(), 'r', encoding='utf-8') as f:
                        return flatten_products(json.load(f))
                # Direct JSON search
                return extract_json_from_text(result_content)
            
            # 3. AgentHistoryList object
            if hasattr(result_content, 'all_results') and result_content.all_results:
                last_result = result_content.all_results[-1]
                if hasattr(last_result, 'extracted_content'):
                    content = last_result.extracted_content
                    return extract_json_from_text(content)
                if hasattr(last_result, 'text'):
                    content = last_result.text
                    return extract_json_from_text(content)
            
            logger.warning("⚠️ No JSON format product data found")
            return []
            
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Browser-use search is available"""
        return BROWSER_USE_AVAILABLE 