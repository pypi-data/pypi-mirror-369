#!/usr/bin/env python3
"""
AI Agent Application

This application allows you to interact with an AI agent that can use various tools
to answer questions and perform tasks. The agent supports both streaming and non-streaming
responses from Ollama.

Usage:
1. Direct execution: python app.py
2. CLI with question: python app.py "Your question here"
3. CLI with flags: python app.py --question "Your question here" --no-save
4. Disable streaming: python app.py "Your question here" --no-stream
"""

import sys
import argparse
from helper import run_agent_with_question

def main():
    """
    Main function to handle both direct execution and CLI arguments.
    
    This function sets up argument parsing for the AI agent application,
    handles both interactive and command-line modes, and manages the
    conversation flow with the agent.
    
    The function supports:
    - Interactive mode when no arguments are provided
    - Single question mode via positional or flag arguments
    - Optional conversation saving to JSON files
    - Custom message file naming
    """
    parser = argparse.ArgumentParser(
        description="AI Agent that can use tools to answer questions and perform tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py
  python app.py "Get the latest trending songs and save them to a file"
  python app.py --question "What files are in the current directory?" --no-save
  python app.py -q "Create a new directory called 'test'" --messages-file "my_conversation.json"
  python app.py "Explain the weather" --no-stream
        """
    )
    
    parser.add_argument(
        'question', 
        nargs='?', 
        help='The question to ask the agent (if not provided, will prompt interactively)'
    )
    
    parser.add_argument(
        '-q', '--question',
        dest='question_flag',
        help='The question to ask the agent (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save the conversation history to a file'
    )
    
    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='Do not stream the response from Ollama (default: streaming enabled)'
    )
    
    parser.add_argument(
        '--messages-file',
        default='messages.json',
        help='Filename to save the conversation history (default: messages.json)'
    )
    
    args = parser.parse_args()
    
    question = None
    if args.question:
        question = args.question
    elif args.question_flag:
        question = args.question_flag
    
    if not question:
        print("🤖 AI Agent - Interactive Mode")
        print("=" * 50)
        print("Ask me anything! I can help you with various tasks using my tools.")
        print("Type 'quit', 'exit', or 'q' to end the session.")
        print()
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q', '']:
                    print("👋 Goodbye!")
                    break
                
                print("\n🔄 Processing your request...")
                print("-" * 30)
                
                result, messages = run_agent_with_question(
                    question=question,
                    save_messages=not args.no_save,
                    messages_file=args.messages_file,
                    stream=not args.no_stream
                )
                
                print(f"\n✅ Final Result:")
                print(result)
                
                if not args.no_save:
                    print(f"\n💾 Conversation saved to: {args.messages_file}")
                
                print("\n" + "=" * 50)
                
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different question.")
    
    else:
        print(f"🤖 AI Agent - Processing: {question}")
        print("=" * 50)
        
        try:
            result, messages = run_agent_with_question(
                question=question,
                save_messages=not args.no_save,
                messages_file=args.messages_file,
                stream=not args.no_stream
            )
            
            print(f"\n✅ Final Result:")
            print(result)
            
            if not args.no_save:
                print(f"\n💾 Conversation saved to: {args.messages_file}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Provide helpful error guidance
            if "CURRENT_AGENT" in str(e) or "API_KEY" in str(e) or "OLLAMA_MODEL" in str(e):
                print("\nThere might be an issue with your configuration.")
                print("Try running the command again to go through the interactive setup,")
                print("or see the environment management guide in the documentation.")
                
            sys.exit(1)

if __name__ == "__main__":
    main()
