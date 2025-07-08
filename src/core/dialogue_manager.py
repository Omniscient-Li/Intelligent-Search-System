import json
import os
import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from ..utils.keyword_extractor import extract_keywords_llm_azure, generate_clarification_question_llm_azure, client, deployment_name
from browser_use import Agent
from langchain_openai import AzureChatOpenAI


# Dialogue state enumeration
class DialoguePhase(Enum):
    GREETING = "greeting"
    INFORMATION_GATHERING = "information_gathering"
    CLARIFICATION = "clarification"
    PRODUCT_SEARCH = "product_search"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PRODUCT_DETAIL = "product_detail"
    FOLLOW_UP = "follow_up"
    END = "end"
    INIT = "init"


# User intent enumeration
class UserIntent(Enum):
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    CLARIFICATION_RESPONSE = "clarification_response"
    PRODUCT_SELECTION = "product_selection"
    MORE_DETAILS = "more_details"
    RESTART = "restart"
    END = "end"


@dataclass
class DialogueContext:
    """Dialogue context management"""
    session_id: str
    start_time: datetime
    current_phase: DialoguePhase = DialoguePhase.GREETING
    user_info: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    current_products: List[Dict[str, Any]] = field(default_factory=list)
    selected_product: Optional[Dict[str, Any]] = None
    turn_count: int = 0
    last_user_input: str = ""
    last_system_response: str = ""
    
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add conversation history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "phase": self.current_phase.value,
            "turn": self.turn_count
        }
        if metadata:
            entry["metadata"] = metadata
        self.conversation_history.append(entry)
    
    def get_recent_context(self, turns: int = 3) -> str:
        """Get recent conversation context"""
        recent = self.conversation_history[-turns:] if len(self.conversation_history) >= turns else self.conversation_history
        context = []
        for entry in recent:
            context.append(f"{entry['role']}: {entry['content']}")
        return "\n".join(context)


@dataclass
class DialogueState:
    """Enhanced dialogue state management"""
    context: DialogueContext
    required_fields: List[str] = field(default_factory=lambda: ["category", "usage", "style", "material"])
    optional_fields: List[str] = field(default_factory=lambda: ["budget", "brand_preference", "installation_method", "color_preference"])
    
    def update_user_info(self, new_info: Dict[str, Any]):
        """Update user information"""
        self.context.user_info.update({k: v for k, v in new_info.items() if v})
    
    def get_missing_fields(self) -> List[str]:
        """Get missing required fields"""
        return [f for f in self.required_fields if f not in self.context.user_info or not self.context.user_info[f]]
    
    def get_completion_rate(self) -> float:
        """Get information completion rate"""
        total_fields = len(self.required_fields) + len(self.optional_fields)
        filled_fields = len([f for f in self.required_fields + self.optional_fields 
                           if f in self.context.user_info and self.context.user_info[f]])
        return filled_fields / total_fields
    
    def has_sufficient_info(self) -> bool:
        """Determine if there is sufficient information for product search"""
        missing_required = self.get_missing_fields()
        completion_rate = self.get_completion_rate()
        return len(missing_required) == 0 or completion_rate >= 0.7


class DialogueManager:
    """Enhanced dialogue manager with multi-turn conversation support"""
    
    def __init__(self):
        self.sessions: Dict[str, DialogueState] = {}
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.1
        )
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new dialogue session"""
        if not session_id:
            session_id = f"session_{len(self.sessions) + 1}_{int(datetime.now().timestamp())}"
        
        context = DialogueContext(session_id=session_id, start_time=datetime.now())
        state = DialogueState(context=context)
        self.sessions[session_id] = state
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DialogueState]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def detect_intent(self, user_input: str, context: DialogueContext) -> UserIntent:
        """Detect user intent"""
        user_input_lower = user_input.lower()
        
        # Greeting intent
        if any(word in user_input_lower for word in ["hello", "hi", "start", "begin"]):
            return UserIntent.GREETING
        
        # End intent
        if any(word in user_input_lower for word in ["end", "exit", "quit", "bye", "goodbye", "thank you", "thanks"]):
            return UserIntent.END
        
        # Restart intent
        if any(word in user_input_lower for word in ["restart", "start over", "new search", "reset"]):
            return UserIntent.RESTART
        
        # Product selection intent
        if re.search(r'select|choose|pick|number\s*\d+', user_input):
            return UserIntent.PRODUCT_SELECTION
        
        # More details intent
        if any(word in user_input_lower for word in ["details", "more", "information", "specs"]):
            return UserIntent.MORE_DETAILS
        
        # Clarification response intent
        if context.current_phase == DialoguePhase.CLARIFICATION:
            return UserIntent.CLARIFICATION_RESPONSE
        
        # Default product inquiry intent
        return UserIntent.PRODUCT_INQUIRY
    
    def generate_smart_clarification(self, state: DialogueState) -> str:
        """Generate smart clarification questions"""
        missing_fields = state.get_missing_fields()
        completion_rate = state.get_completion_rate()
        
        if not missing_fields:
            return "Information is complete, let me search for products for you..."
        
        # Generate different questions based on completion rate
        if completion_rate < 0.3:
            # Very little information, ask basic questions
            primary_field = missing_fields[0]
            clarification_prompts = {
                "category": "What type of product do you need? For example: door handles, drawer pulls, cabinet handles, etc.",
                "usage": "Where will this product be used? For example: kitchen cabinets, bedroom wardrobes, bathroom cabinets, etc.",
                "style": "What style do you prefer? For example: modern minimalist, European classical, industrial style, etc.",
                "material": "What material requirements do you have? For example: stainless steel, brass, zinc alloy, etc."
            }
            return clarification_prompts.get(primary_field, f"Please tell me about {primary_field}")
        
        elif completion_rate < 0.7:
            # Medium information, ask more specific questions
            if "style" in missing_fields:
                return "What style do you want for the product? Modern minimalist, European classical, or other styles?"
            elif "material" in missing_fields:
                return "What material preferences do you have? For example: stainless steel, brass, zinc alloy, etc."
            else:
                return f"Please supplement the information about {missing_fields[0]}"
        
        else:
            # Information is relatively complete, ask optional information
            optional_missing = [f for f in self.optional_fields if f not in self.context.user_info]
            if optional_missing:
                return f"Do you have any requirements for {optional_missing[0]}?"
            else:
                return "Information is complete, let me search for products for you..."
    
    def generate_personalized_greeting(self, context: DialogueContext) -> str:
        """Generate personalized greeting"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        return f"{greeting}! I'm your intelligent product recommendation assistant. Please tell me what type of product you need, and I'll help you find the most suitable one."
    
    async def process_user_input(self, session_id: str, user_input: str) -> str:
        """Process user input"""
        state = self.get_session(session_id)
        if not state:
            return "Session does not exist, please start over."
        
        context = state.context
        context.turn_count += 1
        context.last_user_input = user_input
        
        # Add user input to history
        context.add_to_history("user", user_input)
        
        # Detect intent
        intent = self.detect_intent(user_input, context)
        
        # Handle intent
        response = await self._handle_intent(intent, state, user_input)
        
        # Add system response to history
        context.add_to_history("assistant", response)
        context.last_system_response = response
        
        return response
    
    async def _handle_intent(self, intent: UserIntent, state: DialogueState, user_input: str) -> str:
        """Handle user intent"""
        context = state.context
        
        if intent == UserIntent.GREETING:
            context.current_phase = DialoguePhase.GREETING
            return self.generate_personalized_greeting(context)
        
        elif intent == UserIntent.END:
            context.current_phase = DialoguePhase.END
            return "Thank you for using our system, goodbye!"
        
        elif intent == UserIntent.RESTART:
            # Reset session state
            context.user_info.clear()
            context.current_products.clear()
            context.selected_product = None
            context.current_phase = DialoguePhase.GREETING
            return "Alright, let's start over. Please tell me your requirements."
        
        elif intent == UserIntent.PRODUCT_SELECTION:
            return await self._handle_product_selection(state, user_input)
        
        elif intent == UserIntent.MORE_DETAILS:
            return await self._handle_more_details(state, user_input)
        
        elif intent == UserIntent.CLARIFICATION_RESPONSE:
            return await self._handle_clarification_response(state, user_input)
        
        elif intent == UserIntent.PRODUCT_INQUIRY:
            return await self._handle_product_inquiry(state, user_input)
        
        else:
            return "Sorry, I didn't understand what you meant. Please re-describe your requirements."
    
    async def _handle_product_inquiry(self, state: DialogueState, user_input: str) -> str:
        """Handle product inquiry"""
        context = state.context
        
        # Extract keywords
        llm_keywords = extract_keywords_llm_azure(user_input)
        keywords = self._parse_keywords(llm_keywords)
        state.update_user_info(keywords)
        
        # Check information completeness
        if state.has_sufficient_info():
            context.current_phase = DialoguePhase.PRODUCT_SEARCH
            return await self._search_products(state)
        else:
            context.current_phase = DialoguePhase.CLARIFICATION
            clarification = self.generate_smart_clarification(state)
            context.clarification_questions.append(clarification)
            return clarification
    
    async def _search_products(self, state: DialogueState) -> str:
        """Search products (Stage One: Use browser_use for recommendation)"""
        context = state.context
        context.current_phase = DialoguePhase.PRODUCT_SEARCH
        
        # Build search query
        query = " ".join([str(v) for v in state.context.user_info.values() if v])
        
        # Translate Chinese query
        if self._contains_chinese(query):
            query = await self._translate_to_english(query)
        
        # Use browser_use to search
        instruction = f"""
        Go to https://www.richelieu.com/ca/en/
        
        1. Search for "{query}" in the Richelieu catalog (no login required for search).
        2. On the search results page, look for AT LEAST 5 DIFFERENT products.
        3. Make sure to select products with different names, models, or SKUs.
        4. If you see similar products, choose the ones with different numbers or variations.
        5. For each of the 5 different products, extract ONLY the following fields:
           - Product name (exact title)
           - Short description (if available)
        6. Return the result as a JSON array with this structure:
        [
          {{
            "name": "Product Name 1",
            "description": "Short description or null"
          }},
          {{
            "name": "Product Name 2", 
            "description": "Short description or null"
          }},
          {{
            "name": "Product Name 3",
            "description": "Short description or null"
          }},
          {{
            "name": "Product Name 4",
            "description": "Short description or null"
          }},
          {{
            "name": "Product Name 5",
            "description": "Short description or null"
          }}
        ]
        
        CRITICAL REQUIREMENTS:
        - You MUST find and return EXACTLY 5 different products
        - Look for products with different model numbers (e.g., 305, 306, 307, etc.)
        - Look for products with different styles (e.g., knob, pull, handle, etc.)
        - Look for products with different materials (e.g., steel, brass, chrome, etc.)
        - If you can't find 5 different products, look at more search results or try different variations
        - Only extract information from the product list/search results page
        - Do NOT visit product detail pages
        - Do NOT extract price, image, dimensions, material, or any other detailed info
        - Do NOT extract product URLs (not needed for recommendation phase)
        - This is for a fast recommendation phase, not for detailed info
        """
        
        agent = Agent(task=instruction, llm=self.llm)
        result = await agent.run()
        
        # Parse product results
        products = self._parse_browser_use_result(result)
        
        if not products:
            return "Sorry, I couldn't find a product that meets your requirements. Please try adjusting your search criteria or re-describe your requirements."
        
        print(f"[DEBUG] Found {len(products)} products")
        
        # Deduplication processing: ensure different products are recommended
        unique_products = self._remove_duplicate_products(products)
        
        print(f"[DEBUG] After deduplication, {len(unique_products)} products remain")
        
        if not unique_products:
            return "Sorry, all the products in the search results are the same. Please try adjusting your search criteria or re-describe your requirements."
        
        # If too few products after deduplication, try to relax deduplication conditions
        if len(unique_products) < 3:
            print(f"[DEBUG] Insufficient product count, trying to relax deduplication conditions")
            unique_products = self._remove_duplicate_products_relaxed(products)
            print(f"[DEBUG] After relaxing conditions, {len(unique_products)} products remain")
        
        # Save deduplicated product list
        context.current_products = unique_products
        context.current_phase = DialoguePhase.PRODUCT_RECOMMENDATION
        
        # Generate recommendations
        return self._generate_product_recommendations(state, unique_products)
    
    def _generate_product_recommendations(self, state: DialogueState, products: List[Dict]) -> str:
        """Generate product recommendations"""
        context = state.context
        user_info = ", ".join([f"{k}:{v}" for k, v in state.context.user_info.items()])
        
        print(f"[DEBUG] User information: {user_info}")
        print(f"[DEBUG] Product count: {len(products)}")
        
        response = "Here are the products we recommend for you:\n\n"
        
        for idx, product in enumerate(products[:5]):
            product_name = self._extract_product_name(product)
            print(f"[DEBUG] Processing product {idx+1}: {product_name}")
            
            try:
                reason = self._generate_recommendation_reason(user_info, product_name)
                print(f"[DEBUG] Recommendation reason generated successfully: {len(reason)} characters")
            except Exception as e:
                print(f"[DEBUG] Failed to generate recommendation reason: {e}")
                reason = "This product meets your requirements and has good quality and design."
            
            response += f"{idx+1}. {product_name}\n"
            response += f"   Recommendation reason: {reason}\n\n"
        
        response += "\n\nRecommendation completed! If you want to search again, please re-describe your requirements."
        return response
    
    def _extract_product_name(self, product: Dict) -> str:
        """Extract product name"""
        name_fields = ['name', 'product_name', 'title', 'product_title']
        for field in name_fields:
            if field in product and product[field]:
                return str(product[field])
        return "N/A"
    
    def _extract_alternative_name(self, product: Dict) -> str:
        """Extract alternative product name"""
        # Try to extract name from description
        description = product.get('description', '')
        if description:
            # Simple name extraction logic
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and not line.startswith('http'):
                    return line
        return "N/A"
    
    def _remove_duplicate_products(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate products, ensure different products are recommended"""
        seen_names = set()
        unique_products = []
        
        for product in products:
            name = self._extract_product_name(product)
            # Normalize product name for deduplication
            normalized_name = self._normalize_product_name(name)
            
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_products.append(product)
        
        return unique_products[:5]  # Return at most 5 different products
    
    def _remove_duplicate_products_relaxed(self, products: List[Dict]) -> List[Dict]:
        """Relaxed deduplication processing, keep more products"""
        if not products:
            return []
        
        unique_products = []
        seen_names = set()
        
        for product in products:
            name = product.get('name', '').strip()
            if not name or name == "N/A":
                continue
            
            # More relaxed normalization: only remove obvious duplicates
            normalized = name.lower().strip()
            
            # If exactly the same name, skip
            if normalized in seen_names:
                continue
            
            # Check if it's a different variant of the same product (more relaxed judgment)
            is_duplicate = False
            for existing in unique_products:
                existing_name = existing.get('name', '').lower().strip()
                
                # If names are exactly the same, skip
                if normalized == existing_name:
                    is_duplicate = True
                    break
                
                # If core name is the same but model is different, keep (more relaxed)
                # For example: Modern Steel Knob - 305 and Modern Steel Knob - 306 should both be kept
                if self._is_same_product_different_model(normalized, existing_name):
                    continue  # Don't consider as duplicate
            
            if not is_duplicate:
                unique_products.append(product)
                seen_names.add(normalized)
        
        return unique_products[:5]  # Return at most 5 different products
    
    def _is_same_product_different_model(self, name1: str, name2: str) -> bool:
        """Determine if it's the same product with different model"""
        # Remove model numbers, compare core names
        import re
        
        # Remove model numbers (like - 305, - 306, etc.)
        core1 = re.sub(r'\s*-\s*\d+', '', name1).strip()
        core2 = re.sub(r'\s*-\s*\d+', '', name2).strip()
        
        # If core names are the same, consider as same product with different model
        return core1 == core2 and core1 != ""
    
    def _normalize_product_name(self, name: str) -> str:
        """Normalize product name for deduplication comparison"""
        if not name or name == "N/A":
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common meaningless words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = normalized.split()
        words = [word for word in words if word not in stop_words]
        
        # Keep numbers (model numbers are important), but remove special characters
        core_name = ' '.join(words)
        core_name = ''.join(c for c in core_name if c.isalnum() or c.isspace())
        
        return core_name.strip()
    
    def _parse_keywords(self, llm_output: str) -> Dict[str, Any]:
        """Parse keywords"""
        try:
            return json.loads(llm_output)
        except Exception:
            return {}
    
    def _generate_recommendation_reason(self, user_info: str, product_info: str) -> str:
        """Generate recommendation reason"""
        prompt = f'''
        You are a professional home furnishing consultant. User requirements: {user_info}
        Recommended product information: {product_info}
        Please use concise, professional language to explain why this product is recommended to the user, with reasons that combine user requirements and product features.
        '''
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=256
        )
        return response.choices[0].message.content
    
    def _contains_chinese(self, text: str) -> bool:
        """Check if contains Chinese characters"""
        return bool(re.search('[\u4e00-\u9fff]', text))
    
    async def _translate_to_english(self, text: str) -> str:
        """Translate to English"""
        prompt = f"Please translate the following product keywords to English, keep it concise: {text}"
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=64
        )
        return response.choices[0].message.content.strip()
    
    async def _handle_clarification_response(self, state: DialogueState, user_input: str) -> str:
        """Handle clarification response"""
        # Extract user supplemented information
        llm_keywords = extract_keywords_llm_azure(user_input)
        keywords = self._parse_keywords(llm_keywords)
        state.update_user_info(keywords)
        
        # Check information completeness
        if state.has_sufficient_info():
            state.context.current_phase = DialoguePhase.PRODUCT_SEARCH
            return await self._search_products(state)
        else:
            clarification = self.generate_smart_clarification(state)
            state.context.clarification_questions.append(clarification)
            return clarification
    
    async def _handle_product_selection(self, state: DialogueState, user_input: str) -> str:
        """Handle product selection (stage two disabled)"""
        return "Recommendation completed. If you want to search again, please re-describe your requirements."
    
    async def _handle_more_details(self, state: DialogueState, user_input: str) -> str:
        """Handle more details request (disabled)"""
        return "Recommendation completed. If you want to search again, please re-describe your requirements."
    
    def _parse_browser_use_result(self, result) -> List[Dict]:
        """Parse browser use agent result"""
        print(f"[DEBUG] Original result type: {type(result)}")
        
        # Handle AgentHistoryList object
        if hasattr(result, 'final_result'):
            final_result = result.final_result()
            if final_result:
                result = final_result
                print(f"[DEBUG] Using final_result: {type(result)}")
        elif hasattr(result, 'action_results'):
            # Extract results.md file path from AgentHistoryList
            for action_result in result.action_results():
                if hasattr(action_result, 'attachments') and action_result.attachments:
                    for attachment in action_result.attachments:
                        if isinstance(attachment, str) and attachment.endswith('results.md'):
                            # Read results.md file
                            try:
                                with open(attachment, 'r', encoding='utf-8') as f:
                                    result = f.read()
                                print(f"[DEBUG] Read content from results.md: {len(result)} characters")
                                break
                            except Exception as e:
                                print(f"[DEBUG] Failed to read results.md: {e}")
                                continue
        
        # If it's a file path, read content first
        if isinstance(result, str) and result.strip().endswith('.md') and os.path.exists(result.strip()):
            with open(result.strip(), 'r', encoding='utf-8') as f:
                result = f.read()
            print(f"[DEBUG] Read content from file path: {len(result)} characters")
        
        # If result is not a string, try to convert to string
        if not isinstance(result, str):
            result = str(result)
            print(f"[DEBUG] Converted to string: {len(result)} characters")
        
        print(f"[DEBUG] Result length before processing: {len(result)}")
        print(f"[DEBUG] First 500 characters of result: {result[:500]}")
        
        # Method 1: Priority use regex to extract JSON array
        import re
        try:
            array_match = re.search(r'\[\s*{.*?}\s*\]', result, re.DOTALL)
            if array_match:
                json_str = array_match.group(0)
                data = json.loads(json_str)
                if isinstance(data, list):
                    print(f"[DEBUG] Method 1 regex extraction successful: found {len(data)} products")
                    return data
        except Exception as e:
            print(f"[DEBUG] Method 1 regex extraction failed: {e}")
        
        # Method 2: Try to parse as JSON array
        try:
            data = json.loads(result)
            if isinstance(data, list):
                print(f"[DEBUG] Method 2 successful: found {len(data)} products")
                return data
            elif isinstance(data, dict) and 'products' in data:
                print(f"[DEBUG] Method 2 successful: found {len(data['products'])} products from dict")
                return data['products']
        except Exception as e:
            print(f"[DEBUG] Method 2 failed: {e}")
        
        # Method 3: Extract all independent JSON objects
        products = []
        lines = result.split('\n')
        current_json = ""
        brace_count = 0
        
        for line in lines:
            current_json += line + '\n'
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_json.strip():
                try:
                    # Clean possible markdown format
                    clean_json = current_json.strip()
                    if clean_json.startswith('```json'):
                        clean_json = clean_json[7:]
                    if clean_json.endswith('```'):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()
                    
                    if clean_json and clean_json.startswith('{'):
                        product = json.loads(clean_json)
                        if 'name' in product or 'product_name' in product:
                            products.append(product)
                except Exception:
                    pass
                current_json = ""
        
        if products:
            print(f"[DEBUG] Method 3 successful: found {len(products)} products")
            return products
        
        # Method 4: If method 3 fails, try regex extraction
        try:
            # Use more relaxed regex to match JSON objects
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, result)
            for match in matches:
                try:
                    product = json.loads(match)
                    if 'name' in product or 'product_name' in product:
                        products.append(product)
                except Exception:
                    continue
        except Exception as e:
            print(f"[DEBUG] Method 4 failed: {e}")
        
        if products:
            print(f"[DEBUG] Method 4 successful: found {len(products)} products")
            return products
        
        # Method 5: If still fails, try manual parsing
        try:
            # Find all lines containing "name", then expand forward and backward
            lines = result.split('\n')
            for i, line in enumerate(lines):
                if '"name"' in line or '"product_name"' in line:
                    # Find starting { forward
                    start = i
                    while start >= 0 and '{' not in lines[start]:
                        start -= 1
                    
                    # Find ending } backward
                    end = i
                    brace_count = 0
                    while end < len(lines):
                        brace_count += lines[end].count('{') - lines[end].count('}')
                        if brace_count == 0:
                            break
                        end += 1
                    
                    if start >= 0 and end < len(lines):
                        json_text = '\n'.join(lines[start:end+1])
                        try:
                            product = json.loads(json_text)
                            if 'name' in product or 'product_name' in product:
                                products.append(product)
                        except Exception:
                            continue
        except Exception as e:
            print(f"[DEBUG] Method 5 failed: {e}")
        
        print(f"[DEBUG] Final parsing result: {len(products)} products")
        return products


async def improved_dialogue_loop():
    """Improved dialogue loop"""
    dialogue_manager = DialogueManager()
    session_id = dialogue_manager.create_session()
    
    print("Hello! I'm your intelligent product recommendation assistant.")
    print("Please describe your requirements, and I'll help you find the most suitable product.")
    print("Type 'exit' to exit the program.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Thank you for using our system, goodbye!")
                break
            
            if not user_input:
                continue
            
            response = await dialogue_manager.process_user_input(session_id, user_input)
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nProgram interrupted, goodbye!")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    asyncio.run(improved_dialogue_loop()) 