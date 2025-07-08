#!/usr/bin/env python3
"""
Module specifically for Stage Two: Retrieving detailed product information
"""

# Set environment variables to resolve compatibility issues
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import time
import json
import asyncio
import re
from dotenv import load_dotenv
from openai import AzureOpenAI

# Import Browser-use integration
try:
    from browser_use import Agent
    from langchain_openai import AzureChatOpenAI
    BROWSER_USE_AVAILABLE = True
    print("✅ Browser-use integration available")
except ImportError as e:
    BROWSER_USE_AVAILABLE = False
    print(f"❌ Browser-use not available: {e}")
    print("Please install: pip install browser-use langchain-openai")

# --- Configuration ---
load_dotenv()

# Check for necessary Azure environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT", 
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "AZURE_OPENAI_API_VERSION"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables for Azure: {', '.join(missing_vars)}")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def extract_json_from_browser_result(result_content):
    """More robust extraction of JSON data from browser use agent results, supporting multiple formats and error tolerance"""
    try:
        # 1. Directly parse JSON object or array
        if isinstance(result_content, (dict, list)):
            return result_content
        if not isinstance(result_content, str):
            result_content = str(result_content)
        # 2. Find JSON array
        json_array_match = re.search(r'\[.*\]', result_content, re.DOTALL)
        if json_array_match:
            json_str = json_array_match.group()
            json_str = json_str.replace('\n', ' ').replace('    ', ' ')
            try:
                return json.loads(json_str)
            except Exception:
                pass
        # 3. Find JSON object
        json_obj_match = re.search(r'\{.*\}', result_content, re.DOTALL)
        if json_obj_match:
            json_str = json_obj_match.group()
            # Remove markdown wrapper
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            json_str = json_str.strip().replace('\n', ' ').replace('    ', ' ')
            try:
                return json.loads(json_str)
            except Exception:
                pass
        # 4. Count braces line by line, piece together complete JSON
        lines = result_content.split('\n')
        current_json = ""
        brace_count = 0
        for line in lines:
            current_json += line + '\n'
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and current_json.strip():
                try:
                    clean_json = current_json.strip()
                    if clean_json.startswith('```json'):
                        clean_json = clean_json[7:]
                    if clean_json.endswith('```'):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()
                    if clean_json and (clean_json.startswith('{') or clean_json.startswith('[')):
                        return json.loads(clean_json)
                except Exception:
                    pass
                current_json = ""
        # 5. If it's a .md file path, read content and recurse
        if result_content.strip().endswith('.md') and os.path.exists(result_content.strip()):
            with open(result_content.strip(), 'r', encoding='utf-8') as f:
                content = f.read()
                return extract_json_from_browser_result(content)
        return None
    except Exception:
        return None

async def get_product_details_by_name(product_name):
    """
    Stage Two: Search and scrape detailed product information by product name
    
    Args:
        product_name (str): Product name
        
    Returns:
        dict: Detailed product information
    """
    if not BROWSER_USE_AVAILABLE:
        return {"error": "Browser-use is not available"}
    
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.1
    )
    
    instruction = f"""
    Go to https://www.richelieu.com/ca/en/
    
    1. Click the "Sign In" or "Login" button on the homepage.
    2. Enter the following credentials:
       - Username/Email: li000436@gmail.com
       - Password: $101010Mm
    3. Submit the login form and wait for the login to complete.
    4. After successful login, search for "{product_name}" in the Richelieu catalog.
    5. Find the exact product that matches "{product_name}" and click on it to view the product detail page.
    6. On the product detail page, extract the following information:
       - Product name (exact title)
       - Product description
       - Material (if available)
       - Dimensions (if available)
       - Price (if available)
       - SKU/Model number (if available)
       - Color options (if available)
       - Installation instructions (if available)
       - Warranty information (if available)
       - Product images (if available, describe the images)
       - Related products (if available)
       - Customer reviews (if available, summarize)
       - Technical specifications (if available)
       - Package contents (if available)
       - Certifications (if available)
       - Brand information (if available)
       - Country of origin (if available)
       - Weight (if available)
       - Finish/Coating (if available)
       - Style category (if available)
    
    7. Return the extracted information as a JSON object with this structure:
    {{
        "name": "Exact product name",
        "description": "Product description",
        "material": "Material information or null",
        "dimensions": "Dimensions information or null",
        "price": "Price information or null",
        "sku": "SKU/Model number or null",
        "colors": "Available colors or null",
        "installation": "Installation instructions or null",
        "warranty": "Warranty information or null",
        "images": "Image descriptions or null",
        "related_products": "Related products or null",
        "reviews": "Customer review summary or null",
        "specifications": "Technical specifications or null",
        "package_contents": "Package contents or null",
        "certifications": "Certifications or null",
        "brand": "Brand information or null",
        "origin": "Country of origin or null",
        "weight": "Weight information or null",
        "finish": "Finish/Coating information or null",
        "style": "Style category or null"
    }}
    
    IMPORTANT NOTES:
    - Make sure to extract information from the actual product detail page
    - If any information is not available, use null for that field
    - Be accurate and detailed in the extraction
    - Include all available information from the product page
    - If the product is not found, return an error message
    - This is for detailed product information retrieval, not for recommendations
    """
    
    try:
        start_time = time.time()
        agent = Agent(task=instruction, llm=llm)
        result = await agent.run()
        end_time = time.time()
        
        # Parse results
        result_content = None
        if hasattr(result, 'output') and isinstance(result.output, str):
            result_content = result.output
        elif hasattr(result, 'final_result') and callable(result.final_result):
            result_content = result.final_result()
        elif hasattr(result, 'action_results') and callable(result.action_results):
            for action_result in result.action_results():
                if hasattr(action_result, 'attachments') and action_result.attachments:
                    for attachment in action_result.attachments:
                        if isinstance(attachment, str) and attachment.endswith('.md'):
                            result_content = attachment
                            break
        if not result_content:
            result_content = str(result)
        
        # If it's a .md file path, read content and recursively extract JSON
        if isinstance(result_content, str) and result_content.strip().endswith('.md') and os.path.exists(result_content.strip()):
            with open(result_content.strip(), 'r', encoding='utf-8') as f:
                content = f.read()
                data = extract_json_from_browser_result(content)
        else:
            data = extract_json_from_browser_result(result_content)
        
        # Process returned results
        if isinstance(data, dict):
            # Add metadata
            data['source'] = 'browser-use'
            data['product_name'] = product_name
            data['search_time'] = end_time - start_time
            return data
        elif isinstance(data, list) and data:
            # If it's an array, take the first element
            product_data = data[0]
            product_data['source'] = 'browser-use'
            product_data['product_name'] = product_name
            product_data['search_time'] = end_time - start_time
            return product_data
        else:
            return {
                "error": "Failed to extract product details",
                "raw_result": str(result_content),
                "product_name": product_name
            }
            
    except Exception as e:
        return {
            "error": f"Exception occurred: {str(e)}",
            "product_name": product_name
        }

async def get_product_details(product_url):
    """
    Stage Two: Use browser use agent to scrape detailed information for a single product (via URL)
    
    Args:
        product_url (str): Product detail page URL
        
    Returns:
        dict: Detailed product information
    """
    if not BROWSER_USE_AVAILABLE:
        return {"error": "Browser-use is not available"}
    
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.1
    )
    
    instruction = f"""
    Go to https://www.richelieu.com/ca/en/
    
    1. Click the "Sign In" or "Login" button on the homepage.
    2. Enter the following credentials:
       - Username/Email: li000436@gmail.com
       - Password: $101010Mm
    3. Submit the login form and wait for the login to complete.
    4. After successful login, navigate to the product page: {product_url}
    5. On the product detail page, extract the following information:
       - Product name (exact title)
       - Product description
       - Material (if available)
       - Dimensions (if available)
       - Price (if available)
       - SKU/Model number (if available)
       - Color options (if available)
       - Installation instructions (if available)
       - Warranty information (if available)
       - Product images (if available, describe the images)
       - Related products (if available)
       - Customer reviews (if available, summarize)
       - Technical specifications (if available)
       - Package contents (if available)
       - Certifications (if available)
       - Brand information (if available)
       - Country of origin (if available)
       - Weight (if available)
       - Finish/Coating (if available)
       - Style category (if available)
    
    6. Return the extracted information as a JSON object with this structure:
    {{
        "name": "Exact product name",
        "description": "Product description",
        "material": "Material information or null",
        "dimensions": "Dimensions information or null",
        "price": "Price information or null",
        "sku": "SKU/Model number or null",
        "colors": "Available colors or null",
        "installation": "Installation instructions or null",
        "warranty": "Warranty information or null",
        "images": "Image descriptions or null",
        "related_products": "Related products or null",
        "reviews": "Customer review summary or null",
        "specifications": "Technical specifications or null",
        "package_contents": "Package contents or null",
        "certifications": "Certifications or null",
        "brand": "Brand information or null",
        "origin": "Country of origin or null",
        "weight": "Weight information or null",
        "finish": "Finish/Coating information or null",
        "style": "Style category or null"
    }}
    
    IMPORTANT NOTES:
    - Make sure to extract information from the actual product detail page
    - If any information is not available, use null for that field
    - Be accurate and detailed in the extraction
    - Include all available information from the product page
    - If the product page is not accessible, return an error message
    - This is for detailed product information retrieval, not for recommendations
    """
    
    try:
        start_time = time.time()
        agent = Agent(task=instruction, llm=llm)
        result = await agent.run()
        end_time = time.time()
        
        # Parse results
        result_content = None
        if hasattr(result, 'output') and isinstance(result.output, str):
            result_content = result.output
        elif hasattr(result, 'final_result') and callable(result.final_result):
            result_content = result.final_result()
        elif hasattr(result, 'action_results') and callable(result.action_results):
            for action_result in result.action_results():
                if hasattr(action_result, 'attachments') and action_result.attachments:
                    for attachment in action_result.attachments:
                        if isinstance(attachment, str) and attachment.endswith('.md'):
                            result_content = attachment
                            break
        if not result_content:
            result_content = str(result)
        
        # If it's a .md file path, read content and recursively extract JSON
        if isinstance(result_content, str) and result_content.strip().endswith('.md') and os.path.exists(result_content.strip()):
            with open(result_content.strip(), 'r', encoding='utf-8') as f:
                content = f.read()
                data = extract_json_from_browser_result(content)
        else:
            data = extract_json_from_browser_result(result_content)
        
        # Process returned results
        if isinstance(data, dict):
            # Add metadata
            data['source'] = 'browser-use'
            data['product_url'] = product_url
            data['search_time'] = end_time - start_time
            return data
        elif isinstance(data, list) and data:
            # If it's an array, take the first element
            product_data = data[0]
            product_data['source'] = 'browser-use'
            product_data['product_url'] = product_url
            product_data['search_time'] = end_time - start_time
            return product_data
        else:
            return {
                "error": "Failed to extract product details",
                "raw_result": str(result_content),
                "product_url": product_url
            }
            
    except Exception as e:
        return {
            "error": f"Exception occurred: {str(e)}",
            "product_url": product_url
        }

async def test_stage_two():
    """
    Stage Two test function: Directly test detailed product information retrieval
    """
    print("🧪 Stage Two Test: Product Detail Information Retrieval")
    print("=" * 50)
    
    while True:
        product_url = input("\nPlease enter product URL to get detailed information (or enter 'exit' to quit): ").strip()
        if product_url.lower() == 'exit':
            break
        if not product_url:
            continue
            
        print(f"\nRetrieving product detailed information...")
        details = await get_product_details(product_url)
        
        if "error" in details:
            print(f"❌ Error: {details['error']}")
        else:
            print("\n【Product Detailed Information】")
            print("-" * 30)
            for key, value in details.items():
                if key not in ['source', 'product_url', 'search_time']:
                    print(f"{key}: {value}")
            print(f"\nRetrieval time: {details.get('search_time', 'N/A')} seconds")
        
        print("\nQuery completed. To query other products, please re-enter the product URL.")
        break  # Only query once then terminate

if __name__ == "__main__":
    asyncio.run(test_stage_two()) 