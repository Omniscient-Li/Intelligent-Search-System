#!/usr/bin/env python3
"""
Command Line Interface Module
Provides interactive CLI for the intelligent search system
"""

import asyncio
import sys
from typing import Optional

from ..core.search_engine import SearchEngine
from ..utils.config import config
from ..utils.logger import logger

class CLI:
    """Command Line Interface Class"""
    
    def __init__(self):
        """Initialize CLI"""
        self.search_engine = None
        self.running = False
    
    async def start(self):
        """Start the CLI interface"""
        try:
            # Initialize search engine
            self.search_engine = SearchEngine()
            self.running = True
            
            # Display welcome message
            self._display_welcome()
            
            # Start interactive loop
            await self._interactive_loop()
            
        except Exception as e:
            logger.error(f"❌ CLI startup failed: {e}")
            print(f"❌ System startup failed: {e}")
            sys.exit(1)
    
    def _display_welcome(self):
        """Display welcome message and system status"""
        status = self.search_engine.get_system_status()
        
        print("\n" + "=" * 60)
        print("🎯 Intelligent Search System v2.0")
        print("   Intelligent Product Retrieval System - Friendly Expert Advisor")
        print("=" * 60)
        print(f"📊 Mode: {status['search_mode'].title()} Mode")
        print(f"🌐 Online Search: {'✅ Available' if status['browser_search_available'] else '❌ Unavailable'}")
        print(f"💾 Local Search: {'✅ Available' if status['local_search_available'] else '❌ Unavailable'}")
        print(f"📦 Local Products: {status['local_product_count']} items")
        print()
        print("💡 Usage Instructions:")
        print("   • Enter product descriptions to search Richelieu online catalog")
        print("   • System provides friendly expert advisor recommendations")
        print("   • Supports fuzzy search and detailed product analysis")
        print()
        print("🔧 Commands:")
        print("   'exit' - Exit system")
        print("   'backup on/off' - Enable/disable local backup search")
        print("   'mode' - Show current search mode")
        print("   'status' - Show system status")
        print("   'test' - Run test search")
        print("=" * 60)
    
    async def _interactive_loop(self):
        """Main interactive loop"""
        while self.running:
            try:
                # Get user input
                query = input("\n🔍 Product Search: ").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() == 'exit':
                    self._handle_exit()
                    break
                elif query.lower() == 'mode':
                    self._handle_mode()
                    continue
                elif query.lower() == 'status':
                    self._handle_status()
                    continue
                elif query.lower() == 'test':
                    await self._handle_test()
                    continue
                elif query.lower().startswith('backup '):
                    self._handle_backup(query)
                    continue
                
                # Perform search
                await self._perform_search(query)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ CLI error: {e}")
                print(f"❌ Error: {e}")
    
    async def _perform_search(self, query: str):
        """Perform product search"""
        try:
            # Search for products
            products = await self.search_engine.search_products(query)
            
            if not products:
                print("\n❌ No products found for your search.")
                print("💡 Try using different keywords or more general terms.")
                return
            
            # Generate AI recommendation
            print("\n🤖 Generating expert recommendation...")
            recommendation = self.search_engine.generate_recommendation(query, products)
            
            # Display results
            print("\n" + "=" * 60)
            print("🎯 EXPERT RECOMMENDATION")
            print("=" * 60)
            print(recommendation)
            print("=" * 60)
            
            # Ask if user wants to see raw results
            show_raw = input("\n📋 Show raw product list? (y/n): ").strip().lower()
            if show_raw in ['y', 'yes']:
                self.search_engine.print_results(products)
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            print(f"❌ Search failed: {e}")
    
    def _handle_exit(self):
        """Handle exit command"""
        print("\n👋 Thank you for using Intelligent Search System!")
        print("   Have a great day! 🌟")
        self.running = False
    
    def _handle_mode(self):
        """Handle mode command"""
        mode = self.search_engine.get_search_mode()
        print(f"\n📊 Current Search Mode: {mode.title()}")
        
        if mode == "hybrid":
            print("   • Online search + Local backup")
            print("   • Best performance and reliability")
        elif mode == "online-only":
            print("   • Browser-use only")
            print("   • Real-time data from Richelieu")
        elif mode == "local-only":
            print("   • Local data only")
            print("   • Fast but limited data")
    
    def _handle_status(self):
        """Handle status command"""
        status = self.search_engine.get_system_status()
        print("\n📊 System Status:")
        print(f"   • Search Mode: {status['search_mode']}")
        print(f"   • Browser Search: {'✅ Available' if status['browser_search_available'] else '❌ Unavailable'}")
        print(f"   • Local Search: {'✅ Available' if status['local_search_available'] else '❌ Unavailable'}")
        print(f"   • Local Products: {status['local_product_count']} items")
        print(f"   • Recommendation System: {'✅ Available' if status['recommendation_system_available'] else '❌ Unavailable'}")
    
    async def _handle_test(self):
        """Handle test command"""
        print("\n🧪 Running test search...")
        try:
            result = await self.search_engine.test_search()
            if result['success']:
                print(f"✅ Test successful!")
                print(f"   • Query: {result['query']}")
                print(f"   • Products found: {result['products_found']}")
                print(f"   • Search mode: {result['search_mode']}")
                print(f"   • Recommendation length: {result['recommendation_length']} characters")
            else:
                print(f"❌ Test failed: {result['error']}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    def _handle_backup(self, command: str):
        """Handle backup command"""
        parts = command.lower().split()
        if len(parts) != 2:
            print("❌ Usage: backup on/off")
            return
        
        action = parts[1]
        if action == 'on':
            config.enable_backup = True
            print("✅ Local backup search enabled")
        elif action == 'off':
            config.enable_backup = False
            print("❌ Local backup search disabled")
        else:
            print("❌ Usage: backup on/off")

async def main():
    """Main CLI entry point"""
    cli = CLI()
    await cli.start()

if __name__ == "__main__":
    asyncio.run(main()) 