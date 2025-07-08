import asyncio
from improved_dialogue_manager import DialogueManager
from semantic_search_v2 import get_product_details_by_name
import re

async def main():
    print("Welcome to the Intelligent Product Retrieval System!")
    print("=" * 50)
    # Stage One: Recommendation
    manager = DialogueManager()
    session_id = manager.create_session()
    while True:
        user_input = input("Please enter your requirements (or 'exit' to quit): ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("Thank you for using our system, goodbye!")
            return
        response = await manager.process_user_input(session_id, user_input)
        print(response)
        # Check if there are recommended products
        state = manager.get_session(session_id)
        if state and state.context.current_products:
            break
    # Display recommended products
    products = state.context.current_products
    print("\nHere are our recommended products:")
    for idx, product in enumerate(products):
        name = product.get('name', 'N/A')
        print(f"{idx+1}. {name}")
    # Stage Two: Detailed information (supports batch)
    while True:
        choice = input("\nPlease enter the product number(s) to view detailed information (use comma or space to separate, e.g., 1,3,5) (or 'exit' to quit): ").strip()
        if choice.lower() in ['exit', 'quit']:
            print("Thank you for using our system, goodbye!")
            return
        # Parse multiple numbers
        nums = re.split(r'[，,\s]+', choice)
        idxs = []
        for n in nums:
            if n.isdigit():
                idx = int(n) - 1
                if 0 <= idx < len(products):
                    idxs.append(idx)
        if not idxs:
            print(f"Please enter numbers between 1 and {len(products)}, separated by comma or space.")
            continue
        # Batch retrieve detailed information
        tasks = []
        for idx in idxs:
            product_name = products[idx].get('name', 'N/A')
            if not product_name or product_name == 'N/A':
                print(f"Product {idx+1} has no valid name, cannot retrieve detailed information.")
                continue
            tasks.append(get_product_details_by_name(product_name))
        print("\nRetrieving product detailed information in batch, please wait...")
        details_list = await asyncio.gather(*tasks)
        for i, details in zip(idxs, details_list):
            print(f"\n【Product {i+1} Detailed Information】")
            print("-" * 30)
            if "error" in details:
                print(f"❌ Error: {details['error']}")
            else:
                for k, v in details.items():
                    if k not in ['source', 'product_url', 'search_time']:
                        print(f"{k}: {v}")
                print(f"\nRetrieval time: {details.get('search_time', 'N/A')} seconds")
        print("\nQuery completed. To view other products, please re-enter the numbers, or enter 'exit' to quit.")

if __name__ == "__main__":
    asyncio.run(main()) 