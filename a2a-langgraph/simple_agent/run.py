#!/usr/bin/env python3
"""
Simple Agent Runner - Test the A2A agent

Usage:
    # With a question
    python simple_agent/run.py "What are the latest AI developments?"

    # Interactive mode
    python simple_agent/run.py
"""

import sys
import os

import httpx
from dotenv import load_dotenv

# Add parent directory to path so we can import simple_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_agent.agent import SimpleAgent

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the simple agent."""

    print("=" * 70)
    print("Simple A2A Agent")
    print("=" * 70)
    print()

    # Initialize the agent
    try:
        agent = SimpleAgent()
        print("✓ Agent initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing agent: {e}")
        print("\nMake sure you have OPENAI_API_KEY in your .env file")
        return

    # Check if A2A server is accessible
    print("✓ Checking A2A server connection...")
    test_url = os.getenv('A2A_SERVER_URL', 'http://localhost:10000')
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{test_url}/.well-known/agent.json")
            if response.status_code == 200:
                print(f"✓ A2A server is running at {test_url}")
            else:
                print(f"⚠ A2A server responded with status {response.status_code}")
    except Exception:
        print(f"⚠ Cannot connect to A2A server at {test_url}")
        print("  Start it with: uv run python -m app")

    print()
    print("=" * 70)
    print()

    # Check if query provided as argument
    if len(sys.argv) > 1:
        # Use command line argument
        query = ' '.join(sys.argv[1:])
        print(f"Query: {query}")
        print()
        print("Response:")
        print("-" * 70)

        # Stream the response
        for chunk in agent.stream(query):
            print(chunk, end='', flush=True)
        print()
        print("-" * 70)

    else:
        # Interactive mode
        print("Interactive mode - Enter your questions (or 'quit' to exit)")
        print()

        while True:
            try:
                query = input("You: ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                print()
                print("Agent: ", end='', flush=True)
                # Stream the response
                for chunk in agent.stream(query):
                    print(chunk, end='', flush=True)
                print("\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == '__main__':
    main()
