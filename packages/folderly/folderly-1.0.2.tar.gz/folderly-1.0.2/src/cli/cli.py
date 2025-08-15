#!/usr/bin/env python3
"""
Folderly CLI - AI-Powered Desktop Organization Tool
"""

import os
import json
import openai
import asyncio
import sys
from pathlib import Path
from src.ai.prompts import (
    load_system_prompt, load_welcome_message, 
    load_goodbye_message, load_empty_input_message, load_error_message
)


async def start_ai_chat():
    """Start AI chat mode - the only function users need"""
    # Try environment variable first, then fallback to embedded key
    api_key = os.getenv("OPENAI_API_KEY") or "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"
    
    if not api_key:
        print("❌ Error: No API key available.")
        print("Please set OPENAI_API_KEY environment variable or contact the developer.")
        return
    
    # Check if using fallback key
    if api_key == "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":
        print("✅ Using developer API key (fallback)")
    else:
        print("✅ Using your custom API key")
    
    print("✅ API Key loaded successfully!")
    
    # Configure OpenAI client
    client = openai.AsyncOpenAI(api_key=api_key)
    
    print(load_welcome_message())
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": load_system_prompt()}
    ]
    
    while True:
        try:
            user_input = input("\n💭 You: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print(load_goodbye_message())
                break
                
            if not user_input:
                print(load_empty_input_message())
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    temperature=0.1,
                    max_tokens=2000,
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
                
                message = response.choices[0].message
                conversation_history.append(message)
                print(f"🤖 {message.content}")
                
            except Exception as e:
                print(f"❌ AI Error: {e}")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 See you later! 👋")
            break
        except Exception as e:
            print(load_error_message("generic", str(e)))


async def main():
    """Main entry point - starts AI chat immediately"""
    await start_ai_chat()


def main_sync():
    """Synchronous wrapper for async main function"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()

