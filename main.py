#!/usr/bin/env python3
"""
Intelligent Search System Main Entry Point
Provides command-line interface for the intelligent product retrieval system
"""

import asyncio
import argparse
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.search_engine import SearchEngine
from src.ui.cli import CLI
from src.utils.config import config
from src.utils.logger import logger

def setup_environment():
    """Setup environment variables for better performance"""
    os.environ['TOKENIZERS_PARALLELISM'] = config.tokenizers_parallelism
    os.environ['OMP_NUM_THREADS'] = config.omp_num_threads
    os.environ['MKL_NUM_THREADS'] = config.mkl_num_threads

async def run_test():
    """Run system test"""
    print("🧪 Running Intelligent Search System Test...")
    
    try:
        # Initialize search engine
        engine = SearchEngine()
        
        # Run test search
        result = await engine.test_search()
        
        if result['success']:
            print("✅ System test completed successfully!")
            print(f"   • Query: {result['query']}")
            print(f"   • Products found: {result['products_found']}")
            print(f"   • Search mode: {result['search_mode']}")
            print(f"   • Recommendation length: {result['recommendation_length']} characters")
            print(f"   • System status: All components working")
        else:
            print(f"❌ System test failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False
    
    return True

async def run_interactive():
    """Run interactive CLI"""
    try:
        cli = CLI()
        await cli.start()
    except Exception as e:
        logger.error(f"❌ Interactive mode failed: {e}")
        print(f"❌ Interactive mode failed: {e}")
        return False
    
    return True

async def run_single_search(query: str):
    """Run single search query"""
    print(f"🔍 Searching for: '{query}'")
    
    try:
        # Initialize search engine
        engine = SearchEngine()
        
        # Perform search
        products = await engine.search_products(query)
        
        if not products:
            print("❌ No products found for your search.")
            print("💡 Try using different keywords or more general terms.")
            return False
        
        # Generate recommendation
        print("\n🤖 Generating expert recommendation...")
        recommendation = engine.generate_recommendation(query, products)
        
        # Display results
        print("\n" + "=" * 60)
        print("🎯 EXPERT RECOMMENDATION")
        print("=" * 60)
        print(recommendation)
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        print(f"❌ Search failed: {e}")
        return False

def show_help():
    """Show help information"""
    print("""
🎯 Intelligent Search System v2.0
   Intelligent Product Retrieval System - Friendly Expert Advisor

Usage:
  python main.py [options]

Options:
  -h, --help          Show this help message
  -t, --test          Run system test
  -s, --search QUERY  Perform single search query
  -i, --interactive   Run interactive CLI (default)

Examples:
  python main.py --test
  python main.py --search "kitchen drawer handle"
  python main.py --interactive

Features:
  • Online search using Browser-use automation
  • Local semantic search with FAISS
  • AI-powered expert recommendations
  • Friendly advisor-style interface
  • Hybrid search mode for reliability
""")

async def main():
    """Main entry point"""
    # Setup environment
    setup_environment()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Intelligent Search System")
    parser.add_argument('-t', '--test', action='store_true', help='Run system test')
    parser.add_argument('-s', '--search', type=str, help='Perform single search query')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run interactive CLI')
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.test:
        success = await run_test()
        sys.exit(0 if success else 1)
    
    elif args.search:
        success = await run_single_search(args.search)
        sys.exit(0 if success else 1)
    
    elif args.interactive or (not args.test and not args.search):
        # Default to interactive mode
        success = await run_interactive()
        sys.exit(0 if success else 1)
    
    else:
        show_help()
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 