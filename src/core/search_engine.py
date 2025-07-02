#!/usr/bin/env python3
"""
Search Engine Core Module
Integrates online search and local search, providing a unified search interface
"""

import time
from typing import List, Dict, Any

from .browser_search import BrowserUseSearch
from .local_search import LocalSearch
from .recommendation import RecommendationSystem
from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import sort_products_by_relevance

class SearchEngine:
    """Search Engine Core Class"""
    
    def __init__(self):
        """Initialize search engine"""
        logger.info("🚀 Initializing Intelligent Product Retrieval System...")
        
        # Initialize Browser-use search
        self.browser_search = None
        try:
            self.browser_search = BrowserUseSearch()
            logger.info("✅ Browser-use search initialized successfully")
        except Exception as e:
            logger.error(f"❌ Browser-use search initialization failed: {e}")
        
        # Initialize local search
        self.local_search = LocalSearch()
        
        # Initialize recommendation system
        self.recommendation_system = RecommendationSystem()
        
        # Determine search mode
        self._determine_search_mode()
    
    def _determine_search_mode(self):
        """Determine search mode"""
        if self.browser_search and self.local_search.is_available():
            self.search_mode = "hybrid"
            logger.info("✅ Hybrid mode: Online search + Local backup")
        elif self.browser_search:
            self.search_mode = "online-only"
            logger.info("✅ Online mode: Browser-use only")
        elif self.local_search.is_available():
            self.search_mode = "local-only"
            logger.info("✅ Local mode: Local data only")
        else:
            raise ValueError("❌ No available search methods")
    
    async def search_products(self, query: str, max_products: int = None, enable_backup: bool = None) -> List[Dict[str, Any]]:
        """
        Search for products
        
        Args:
            query (str): Search query
            max_products (int): Maximum number of products
            enable_backup (bool): Whether to enable backup search
            
        Returns:
            list: Product list
        """
        # Use configuration defaults
        if max_products is None:
            max_products = config.max_products
        if enable_backup is None:
            enable_backup = config.enable_backup
        
        start_time = time.time()
        logger.search_start(query)
        print(f"\n=== Searching Richelieu Product Catalog: '{query}' ===")
        
        all_products = []
        
        # 1. Online search (if available)
        if self.browser_search:
            online_products = await self.browser_search.search_products(query, max_products)
            print(f"DEBUG: Online search parsed product count: {len(online_products)}")
            print(f"DEBUG: Online product content: {online_products[:2]}")
            all_products.extend(online_products)
            print(f"🌐 Online search found {len(online_products)} products")
        
        # 2. Local backup search (if enabled and online search failed)
        if (enable_backup and self.local_search.is_available() and len(all_products) == 0):
            print("🔄 No online results, trying local backup...")
            local_products = self.local_search.search(query, top_k=3)
            print(f"DEBUG: Local search parsed product count: {len(local_products)}")
            print(f"DEBUG: Local product content: {local_products[:2]}")
            all_products.extend(local_products)
            print(f"💾 Local backup found {len(local_products)} products")
        
        # 3. Sort results
        all_products = sort_products_by_relevance(all_products)
        print(f"📊 Total found {len(all_products)} products")
        print(f"DEBUG: Final product content: {all_products[:2]}")
        
        duration = time.time() - start_time
        logger.search_complete(query, len(all_products), duration)
        
        return all_products
    
    def generate_recommendation(self, query: str, products: List[Dict[str, Any]]) -> str:
        """Generate AI recommendation"""
        return self.recommendation_system.generate_recommendation(query, products)
    
    def print_results(self, products: List[Dict[str, Any]]):
        """Print search results"""
        self.recommendation_system.print_results(products)
    
    def get_search_mode(self) -> str:
        """Get current search mode"""
        return self.search_mode
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'search_mode': self.search_mode,
            'browser_search_available': self.browser_search is not None,
            'local_search_available': self.local_search.is_available(),
            'local_product_count': self.local_search.get_product_count(),
            'recommendation_system_available': True
        }
    
    def update_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                logger.info(f"Configuration updated: {key} = {value}")
    
    async def test_search(self, query: str = "kitchen drawer handle") -> Dict[str, Any]:
        """Test search functionality"""
        logger.info(f"🧪 Starting test search: '{query}'")
        
        try:
            # Execute search
            products = await self.search_products(query, max_products=2)
            
            # Generate recommendation
            recommendation = self.generate_recommendation(query, products)
            
            return {
                'success': True,
                'query': query,
                'products_found': len(products),
                'search_mode': self.search_mode,
                'recommendation_length': len(recommendation),
                'products': products[:2]  # Only return first 2 products for testing
            }
            
        except Exception as e:
            logger.error(f"Test search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            } 