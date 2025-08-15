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
    # Set the API key in environment FIRST
    api_key = os.getenv("OPENAI_API_KEY") or "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"
    
    if not api_key:
        print("❌ Error: No API key available.")
        print("Please set OPENAI_API_KEY environment variable or contact the developer.")
        return
    
    # Set environment variable BEFORE importing AI integration
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Check if using fallback key
    if api_key == "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":
        print("✅ Using developer API key (fallback)")
    else:
        print("✅ Using your custom API key")
    
    print("✅ API Key loaded successfully!")
    
    # NOW import and use the working AI integration
    from src.ai.ai_integration import chat_with_ai
    await chat_with_ai()


async def main():
    """Main entry point - starts AI chat immediately"""
    await start_ai_chat()


def main_sync():
    """Synchronous wrapper for async main function"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()

