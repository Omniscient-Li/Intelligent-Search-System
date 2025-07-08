#!/usr/bin/env python3
"""
AI Recommendation System Module
Provides intelligent product recommendations with expert advisor style
"""

import time
from typing import List, Dict, Any

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import is_fuzzy_query, format_price, format_description, safe_str

class RecommendationSystem:
    """AI Recommendation System Class"""
    
    def __init__(self):
        """Initialize recommendation system"""
        # Validate configuration
        config.validate_config()
        
        # Create Azure OpenAI LLM object
        azure_config = config.get_azure_config()
        from langchain_openai import AzureChatOpenAI
        self.llm = AzureChatOpenAI(
            azure_deployment=azure_config['deployment_name'],
            openai_api_version=azure_config['api_version'],
            azure_endpoint=azure_config['endpoint'],
            api_key=azure_config['api_key'],
            temperature=0.7
        )
    
    def generate_recommendation(self, query: str, products: List[Dict[str, Any]]) -> str:
        """
        Generate AI recommendation with expert advisor style
        
        Args:
            query (str): Search query
            products (list): Product list
            
        Returns:
            str: AI recommendation
        """
        if not products:
            return self._generate_no_results_recommendation(query)
        
        logger.recommendation_start(query)
        start_time = time.time()
        
        try:
            # Prepare product information
            product_info = self._format_products_for_ai(products)
            
            # Create expert advisor prompt
            prompt = self._create_expert_prompt(query, product_info)
            
            # Generate recommendation
            response = self.llm.invoke(prompt)
            recommendation = response.content
            
            duration = time.time() - start_time
            logger.recommendation_complete(query, duration)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation failed: {e}")
            return self._generate_fallback_recommendation(query, products)
    
    def _create_expert_prompt(self, query: str, product_info: str) -> str:
        """Create expert advisor style prompt"""
        return f"""
You are a friendly and knowledgeable expert advisor specializing in Richelieu hardware products. 
Your role is to help customers find the perfect products for their needs with a warm, professional approach.

Customer Query: "{query}"

Available Products:
{product_info}

Please provide a comprehensive recommendation that includes:

1. **Warm Greeting**: Start with a friendly welcome and acknowledge their search
2. **Query Understanding**: Show you understand what they're looking for
3. **Product Analysis**: For each recommended product, provide:
   - Clear product name and key features
   - Detailed specifications (dimensions, materials, finish options)
   - Installation requirements and considerations
   - Usage advice and best practices
   - Price information (if available)
   - **Image Preview**: If image URL is available, provide a markdown image tag: ![Product Image](image_url)
   - **Purchase Link**: If product URL is available, provide a markdown link: [View & Buy](product_url)
4. **Expert Tips**: Share professional insights about:
   - Material selection considerations
   - Installation best practices
   - Maintenance and care advice
   - Compatibility with different styles
5. **Personalized Recommendations**: Consider their specific needs and suggest the best options
6. **Friendly Conclusion**: End with encouragement and offer to help with more questions

Please write in a warm, expert tone that makes customers feel confident in their choices. 
Use bullet points and clear sections for easy reading.
Focus on being helpful and informative while maintaining a friendly, approachable style.
"""
    
    def _format_products_for_ai(self, products: List[Dict[str, Any]]) -> str:
        """Format products for AI analysis"""
        formatted_products = []
        
        for i, product in enumerate(products[:3], 1):  # Limit to top 3 products
            name = safe_str(product.get('name', product.get('Product Name', 'Unknown Product')))
            price = format_price(product.get('price', product.get('Price', '')))
            description = format_description(product.get('description', product.get('Description', '')))
            sku = safe_str(product.get('sku', product.get('SKU', '')))
            dimensions = safe_str(product.get('dimensions', ''))
            material = safe_str(product.get('material', ''))
            finish = safe_str(product.get('finish', ''))
            installation = safe_str(product.get('installation', ''))
            weight = safe_str(product.get('weight', ''))
            package_contents = safe_str(product.get('package_contents', ''))
            technical_specs = safe_str(product.get('technical_specs', ''))
            certifications = safe_str(product.get('certifications', ''))
            warranty = safe_str(product.get('warranty', ''))
            product_url = safe_str(product.get('product_url', product.get('Product URL', '')))
            image_url = safe_str(product.get('image_url', product.get('Image URL', '')))
            
            formatted_product = f"""
Product {i}: {name}
- Price: {price}
- SKU: {sku}
- Description: {description}
- Dimensions: {dimensions}
- Material: {material}
- Finish: {finish}
- Installation: {installation}
- Weight: {weight}
- Package Contents: {package_contents}
- Technical Specifications: {technical_specs}
- Certifications: {certifications}
- Warranty: {warranty}
- Product URL: {product_url}
- Image Preview: {image_url if image_url else 'No image available'}
"""
            formatted_products.append(formatted_product)
        
        return "\n".join(formatted_products)
    
    def _generate_no_results_recommendation(self, query: str) -> str:
        """Generate recommendation when no products found"""
        return f"""
Hello! 👋

I understand you're looking for "{query}" in our Richelieu product catalog. 
Unfortunately, I couldn't find any exact matches for your search at the moment.

Here are some suggestions to help you find what you're looking for:

🔍 **Try Different Keywords**:
- Use more general terms (e.g., "handle" instead of "brass handle")
- Try alternative spellings or synonyms
- Use product categories (e.g., "cabinet hardware", "door hardware")

📋 **Browse Categories**:
- Cabinet Hardware
- Door Hardware  
- Drawer Hardware
- Hinges and Accessories

💡 **Need Help?**
If you're having trouble finding the right product, feel free to:
- Describe your project in more detail
- Ask about specific materials or finishes
- Request recommendations for similar products

I'm here to help you find the perfect hardware for your project! 
Please try a different search term or let me know more about what you're looking for.
"""
    
    def _generate_fallback_recommendation(self, query: str, products: List[Dict[str, Any]]) -> str:
        """Generate fallback recommendation when AI fails"""
        if not products:
            return self._generate_no_results_recommendation(query)
        
        recommendation = f"""
Hello! 👋

I found some products that might match your search for "{query}":

"""
        
        for i, product in enumerate(products[:3], 1):
            name = safe_str(product.get('name', product.get('Product Name', 'Unknown Product')))
            price = format_price(product.get('price', product.get('Price', '')))
            description = format_description(product.get('description', product.get('Description', '')))
            
            recommendation += f"""
**Product {i}: {name}**
- Price: {price}
- Description: {description}
"""
        
        recommendation += """
These products might be what you're looking for. 
For more detailed information and expert advice, please try searching again or contact our support team.

I'm here to help you find the perfect hardware for your project! 🛠️
"""
        
        return recommendation
    
    def print_results(self, products: List[Dict[str, Any]]):
        """Print search results in a formatted way"""
        if not products:
            print("\n❌ No products found")
            return
        
        print(f"\n📋 Found {len(products)} products:")
        print("=" * 80)
        
        for i, product in enumerate(products, 1):
            name = safe_str(product.get('name', product.get('Product Name', 'Unknown Product')))
            price = format_price(product.get('price', product.get('Price', '')))
            sku = safe_str(product.get('sku', product.get('SKU', '')))
            source = safe_str(product.get('source', 'unknown'))
            
            print(f"\n{i}. {name}")
            print(f"   💰 Price: {price}")
            print(f"   🏷️  SKU: {sku}")
            print(f"   📍 Source: {source}")
            
            # Print additional details if available
            dimensions = safe_str(product.get('dimensions', ''))
            if dimensions:
                print(f"   📏 Dimensions: {dimensions}")
            
            material = safe_str(product.get('material', ''))
            if material:
                print(f"   🏗️  Material: {material}")
            
            finish = safe_str(product.get('finish', ''))
            if finish:
                print(f"   🎨 Finish: {finish}")
        
        print("\n" + "=" * 80) 