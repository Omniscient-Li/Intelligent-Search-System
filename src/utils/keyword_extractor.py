import os
from openai import AzureOpenAI

# Initialize Azure OpenAI client (only initialize once)
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

def extract_keywords_llm_azure(user_input: str) -> str:
    """
    Use Azure OpenAI LLM to extract product keywords from user input.
    """
    prompt = f"""
    You are an intelligent shopping assistant. Please extract product categories, uses, styles, materials, and other keywords from the following user description and output them in JSON format. For example:
    
    User description: "I want to buy a cabinet handle suitable for Nordic style, preferably stainless steel."
    
    Output:
    {{
        "category": "handle",
        "usage": "cabinet",
        "style": "Nordic",
        "material": "stainless steel"
    }}
    
    User description: "I need a modern style door handle."
    
    Output:
    {{
        "category": "handle",
        "usage": "door",
        "style": "modern"
    }}
    
    Now, please extract keywords from this user input:
    "{user_input}"
    
    Please output only the JSON format result:
    """
    
    # Here you would call Azure OpenAI API
    # For now, return a placeholder
    return '{"category": "handle", "usage": "cabinet", "style": "modern", "material": "stainless steel"}'

def generate_clarification_question_llm_azure(user_input: str, current_keywords: dict) -> str:
    """
    Generate clarification questions using Azure OpenAI LLM.
    """
    prompt = f"""
    You are an intelligent shopping assistant. The known user input and extracted keywords are as follows:
    User input: "{user_input}"
    Current keywords: {current_keywords}
    
    Please determine what key information is still missing (such as use, style, material, etc.) and generate a clarification question to guide the user to supplement. For example:
    
    If missing style: "What style do you prefer for this product? Modern, classical, or industrial style?"
    If missing material: "What material do you prefer? Stainless steel, brass, or other materials?"
    
    Please generate a natural, friendly clarification question:
    """
    
    # Here you would call Azure OpenAI API
    # For now, return a placeholder
    return "What style do you prefer for this product?"

# Example usage (can be deleted)
if __name__ == "__main__":
    user_input = "I want to buy a handle"
    keywords = extract_keywords_llm_azure(user_input)
    print("Extracted keywords:", keywords)
    clarification = generate_clarification_question_llm_azure(user_input, keywords)
    print("Clarification question:", clarification) 