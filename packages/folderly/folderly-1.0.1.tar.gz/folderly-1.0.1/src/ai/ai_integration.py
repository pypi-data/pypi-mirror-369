import os
import json
import openai
import asyncio
from dotenv import load_dotenv
from src.ai.function_schemas import get_function_schemas
from src.ai.prompts import (
    load_system_prompt, load_force_prompt, load_welcome_message, 
    load_goodbye_message, load_empty_input_message, load_error_message
)
from src.core.core import list_directory_items, filter_and_sort_by_modified, create_directory, create_multiple_directories, move_items_to_directory, delete_single_item, delete_multiple_items, delete_items_by_pattern, list_nested_folders_tree, count_files_by_extension, get_file_type_statistics, copy_multiple_items, rename_multiple_items
from pathlib import Path

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(load_error_message("api_key"))
    exit(1)

print(f"API Key loaded: {'Yes' if api_key else 'No'}")

# Configure OpenAI client - use async client
client = openai.AsyncOpenAI(api_key=api_key)

def main():
    """Main entry point for Poetry script"""
    asyncio.run(chat_with_ai())

async def chat_with_ai():
    print(load_welcome_message())
    
    # Initialize conversation history with fresh system prompt
    conversation_history = [
        {"role": "system", "content": load_system_prompt()}
    ]
    
    # Force fresh start - clear any cached model responses
    # print("🔄 Fresh AI session started - all caches cleared!")
    
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

            # Inner loop to handle multiple function calls per user input
            while True:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto",
                    temperature=0.1,
                    # Force fresh response, no caching
                    max_tokens=2000,
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
                
                message = response.choices[0].message
                
                if message.function_call:
                    function_name = message.function_call.name
                    function_args = json.loads(message.function_call.arguments)
                    print(f"🔧 DEBUG: Calling function: {function_name}")
                    
                    # Execute appropriate function
                    if function_name == "list_directory_items":
                        folder_name = function_args.get("folder_name", None)
                        extension = function_args.get("extension", None)
                        file_type = function_args.get("file_type", None)
                        pattern = function_args.get("pattern", None)
                        date_range = function_args.get("date_range", None)
                        size_range = function_args.get("size_range", None)
                        sort_by = function_args.get("sort_by", "name")
                        sort_order = function_args.get("sort_order", "asc")
                        include_folders = function_args.get("include_folders", True)
                        include_files = function_args.get("include_files", True)
                        max_results = function_args.get("max_results", None)
                        
                        result = await list_directory_items(
                            folder_name=folder_name,
                            extension=extension,
                            file_type=file_type,
                            pattern=pattern,
                            date_range=date_range,
                            size_range=size_range,
                            sort_by=sort_by,
                            sort_order=sort_order,
                            include_folders=include_folders,
                            include_files=include_files,
                            max_results=max_results
                        )
                    elif function_name == "filter_and_sort_by_modified":
                        # Get items first, then filter by date
                        items_result = await list_directory_items()
                        if items_result["success"]:
                            # Convert string paths back to Path objects for the filter function
                            items = [Path(path) for path in items_result["results"]]
                            days = function_args.get("days", 7)
                            result = filter_and_sort_by_modified(items, days)
                        else:
                            result = items_result
                    elif function_name == "create_directory":
                        # Create directory with base path support
                        target_dir = Path(function_args.get("target_dir", ""))
                        base_path = function_args.get("base_path", "Desktop")
                        result = await create_directory(target_dir, base_path)
                    elif function_name == "create_multiple_directories":
                        # Create multiple directories with base path support
                        directories = function_args.get("directories", [])
                        base_path = function_args.get("base_path", "Desktop")
                        result = await create_multiple_directories(directories, base_path)
                    elif function_name == "move_items_to_directory":
                        # Move items to destination directory
                        items = [Path(item) for item in function_args.get("items", [])]
                        destination_dir = Path(function_args.get("destination_dir", ""))
                        result = await move_items_to_directory(items, destination_dir)
                    elif function_name == "delete_single_item":
                        # Delete a single item
                        item_path = function_args.get("item_path", "")
                        result = await delete_single_item(item_path)
                    elif function_name == "delete_multiple_items":
                        # Delete multiple items
                        item_paths = function_args.get("item_paths", [])
                        result = await delete_multiple_items(item_paths)
                    elif function_name == "delete_items_by_pattern":
                        # Delete items by pattern
                        pattern = function_args.get("pattern", "")
                        target_dir = function_args.get("target_dir", None)
                        result = await delete_items_by_pattern(pattern, target_dir)
                    elif function_name == "list_nested_folders_tree":
                        # List nested folders in tree structure
                        target_dir = function_args.get("target_dir", None)
                        max_depth = function_args.get("max_depth", 3)
                        result = list_nested_folders_tree(target_dir, max_depth)
                    elif function_name == "count_files_by_extension":
                        # Count files by extension
                        folder_name = function_args.get("folder_name", None)
                        result = await count_files_by_extension(folder_name)
                    elif function_name == "get_file_type_statistics":
                        # Get file type statistics
                        folder_name = function_args.get("folder_name", None)
                        result = await get_file_type_statistics(folder_name)
                    elif function_name == "copy_multiple_items":
                        # Copy multiple items to destination directory
                        items = [Path(item) for item in function_args.get("items", [])]
                        destination_dir = Path(function_args.get("destination_dir", ""))
                        result = await copy_multiple_items(items, destination_dir)
                    elif function_name == "rename_multiple_items":
                        # Rename multiple items with new names
                        items_data = function_args.get("items", [])
                        items = [(Path(item["old_path"]), item["new_name"]) for item in items_data]
                        result = await rename_multiple_items(items)
                    else:
                        result = {"success": False, "error": f"Unknown function: {function_name}"}
                    
                    # Add function result to conversation
                    conversation_history.append({
                        "role": "function", 
                        "name": function_name, 
                        "content": json.dumps(result, indent=2)
                    })
                    
                    # Continue the inner loop to see if AI wants to call another function
                    continue
                
                else:
                    # No function call, final model response ready
                    conversation_history.append(message)
                    print(f"🤖 {message.content}")
                    break  # Exit the inner loop and wait for next user input
                
        except KeyboardInterrupt:
            print("\n👋 See you later! 👋")
            break
        except Exception as e:
            print(load_error_message("generic", str(e)))

if __name__ == "__main__":
    main()