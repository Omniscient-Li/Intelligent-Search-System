#!/usr/bin/env python3
"""
Intelligent Product System  - Main Entry Point
Two-Stage Intelligent Product Retrieval System
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from src.core.dialogue_manager import DialogueManager
from src.core.semantic_search import SemanticSearchV2
from src.core.two_stage_system import TwoStageSystem
from src.utils.logger import setup_logger, get_logger
from src.utils.helpers import create_session_id, format_timestamp
from config.config import config

def setup_environment():
    """Setup environment variables for better performance"""
    os.environ['TOKENIZERS_PARALLELISM'] = config.tokenizers_parallelism
    os.environ['OMP_NUM_THREADS'] = config.omp_num_threads
    os.environ['MKL_NUM_THREADS'] = config.mkl_num_threads

async def run_stage_one(query: str) -> bool:
    """Run Stage One: Product Recommendation"""
    logger = get_logger("StageOne")
    
    print(f"🎯 Stage One: Product Recommendation")
    print(f"🔍 Search Query: '{query}'")
    print("-" * 50)
    
    try:
        # Create dialogue manager
        manager = DialogueManager()
        session_id = manager.create_session()
        
        logger.info(f"Created session: {session_id}")
        
        # Process user input
        response = await manager.process_user_input(session_id, query)
        print(response)
        
        # Get recommended products
        state = manager.get_session(session_id)
        if state and state.context.current_products:
            print(f"\n📋 Recommended Products: {len(state.context.current_products)}")
            print("Product List:")
            for i, product in enumerate(state.context.current_products, 1):
                name = product.get('name', 'Unknown')
                desc = product.get('description', 'No description')
                print(f"  {i}. {name}")
                if desc and desc != 'null':
                    print(f"     Description: {desc}")
        
        logger.info(f"Stage one completed successfully with {len(state.context.current_products) if state and state.context.current_products else 0} products")
        return True
        
    except Exception as e:
        logger.error(f"Stage one failed: {e}")
        print(f"❌ Stage One execution failed: {e}")
        return False

async def run_stage_two(product_name: str) -> bool:
    """Run Stage Two: Detailed Information Retrieval"""
    logger = get_logger("StageTwo")
    
    print(f"🔍 Stage Two: Detailed Information Retrieval")
    print(f"📦 Product Name: '{product_name}'")
    print("-" * 50)
    
    try:
        # Create semantic search instance
        semantic_search = SemanticSearchV2()
        
        # Get product details
        result = await semantic_search.get_product_details_by_name(product_name)
        
        if result:
            print("✅ Product details retrieved successfully!")
            print(result)
            logger.info(f"Successfully retrieved details for product: {product_name}")
        else:
            print("❌ No product details found")
            logger.warning(f"No details found for product: {product_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Stage two failed: {e}")
        print(f"❌ Stage Two execution failed: {e}")
        return False

async def run_two_stage_system() -> bool:
    """Run complete two-stage system"""
    logger = get_logger("TwoStageSystem")
    
    print("🚀 Two-Stage Intelligent Product Retrieval System")
    print("=" * 50)
    
    try:
        # Stage One: Product Recommendation
        query = input("Please enter your requirements (e.g., door handle modern style stainless steel): ").strip()
        if not query:
            print("❌ Please enter a valid requirement description")
            return False
        
        success = await run_stage_one(query)
        if not success:
            return False
        
        # Ask if user wants to proceed to Stage Two
        print("\n" + "=" * 50)
        choice = input("Would you like to get detailed information for a specific product? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes']:
            product_name = input("Please enter the product name: ").strip()
            if product_name:
                await run_stage_two(product_name)
        
        logger.info("Two-stage system completed successfully")
        return True
        
    except KeyboardInterrupt:
        print("\n👋 User interrupted, exiting system")
        logger.info("User interrupted the system")
        return True
    except Exception as e:
        logger.error(f"Two-stage system failed: {e}")
        print(f"❌ System execution failed: {e}")
        return False

async def run_batch_search(queries: list) -> bool:
    """Batch search multiple queries"""
    logger = get_logger("BatchSearch")
    
    print(f"📦 Batch Search: {len(queries)} queries")
    print("=" * 50)
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Processing Query {i}/{len(queries)}: '{query}'")
        print("-" * 30)
        
        try:
            success = await run_stage_one(query)
            results.append({
                'query': query,
                'success': success,
                'timestamp': format_timestamp()
            })
            
            if i < len(queries):
                print("\n⏳ Waiting 3 seconds before processing next query...")
                await asyncio.sleep(3)
                
        except Exception as e:
            logger.error(f"Batch search failed for query '{query}': {e}")
            results.append({
                'query': query,
                'success': False,
                'error': str(e),
                'timestamp': format_timestamp()
            })
    
    # Show results summary
    print(f"\n📊 Batch Search Completed")
    print(f"Success: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    return True

async def run_test() -> bool:
    """Run system test"""
    logger = get_logger("SystemTest")
    
    print("🧪 Running Intelligent Product System Test...")
    print("=" * 50)
    
    try:
        # Test stage one
        print("Testing Stage One: Product Recommendation")
        success = await run_stage_one("door handle modern style stainless steel")
        
        if success:
            print("\n✅ System test completed successfully!")
            print("   • Stage One: Product recommendation working")
            print("   • Stage Two: Detailed info retrieval ready")
            print("   • System status: All components working")
            logger.info("System test completed successfully")
        else:
            print("\n❌ System test failed")
            logger.error("System test failed")
            return False
            
    except Exception as e:
        logger.error(f"System test failed: {e}")
        print(f"❌ System test failed: {e}")
        return False
    
    return True

def show_help():
    """Show help information"""
    print("""
🎯 Intelligent Product System
   Two-Stage Intelligent Product Retrieval System

Usage:
  python main.py [options]

Options:
  -h, --help          Show this help message
  -t, --test          Run system test
  -s, --search QUERY  Perform single search query (Stage One)
  -d, --details NAME  Get product details (Stage Two)
  -2, --two-stage     Run complete two-stage system
  -b, --batch FILE    Batch search (read queries from file)
  -i, --interactive   Run interactive CLI (default)

Examples:
  python main.py --test
  python main.py --search "kitchen drawer handle"
  python main.py --details "Modern Steel Pull - 305"
  python main.py --two-stage
  python main.py --batch queries.txt
  python main.py --interactive

Features:
  • Stage One: Multi-turn dialogue for product recommendation
  • Stage Two: Detailed product information retrieval
  • 5 different products recommendation with personalized reasons
  • No login required for Stage One
  • Product name-based search for Stage Two
  • Smart deduplication and diversity assurance
  • English/Chinese input support
  • Batch search functionality
  • Complete logging system
""")

async def main():
    """Main entry point"""
    # Setup environment
    setup_environment()
    
    # Setup logger
    setup_logger()
    logger = get_logger("Main")
    
    logger.info("Starting Intelligent Product System")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Intelligent Product System")
    parser.add_argument('-t', '--test', action='store_true', help='Run system test')
    parser.add_argument('-s', '--search', type=str, help='Perform single search query (Stage One)')
    parser.add_argument('-d', '--details', type=str, help='Get product details (Stage Two)')
    parser.add_argument('-2', '--two-stage', action='store_true', help='Run complete two-stage system')
    parser.add_argument('-b', '--batch', type=str, help='Batch search (read queries from file)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run interactive CLI')
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.test:
        success = await run_test()
        sys.exit(0 if success else 1)
    
    elif args.search:
        success = await run_stage_one(args.search)
        sys.exit(0 if success else 1)
    
    elif args.details:
        success = await run_stage_two(args.details)
        sys.exit(0 if success else 1)
    
    elif args.two_stage:
        success = await run_two_stage_system()
        sys.exit(0 if success else 1)
    
    elif args.batch:
        # Batch search mode
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            
            if not queries:
                print(f"❌ No valid queries found in file {args.batch}")
                sys.exit(1)
            
            success = await run_batch_search(queries)
            sys.exit(0 if success else 1)
            
        except FileNotFoundError:
            print(f"❌ File not found: {args.batch}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Batch search failed: {e}")
            sys.exit(1)
    
    elif args.interactive or (not args.test and not args.search and not args.details and not args.two_stage and not args.batch):
        # Default interactive mode
        success = await run_two_stage_system()
        sys.exit(0 if success else 1)
    
    else:
        show_help()
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 