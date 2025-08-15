"""
Folderly AI Function Calling Schemas
JSON schemas for AI function calling in the Folderly codebase.
"""

from typing import Dict, List, Any

# ============================================================================
# AI FUNCTION CALLING SCHEMAS
# ============================================================================

FOLDERLY_FUNCTIONS = [
    {
        "name": "list_directory_items",
        "description": "Lists files and folders in any root folder with advanced filtering options (Desktop, Downloads, Documents, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Name of the root folder to list (Desktop, Downloads, Documents, Pictures, Music, Videos, etc.)"
                },
                "extension": {
                    "type": "string",
                    "description": "Filter by file extension (e.g., 'txt', 'pdf', 'docx'). Use without the dot."
                },
                "file_type": {
                    "type": "string",
                    "description": "Filter by file type category: 'documents', 'images', 'videos', 'audio', 'archives', 'executables', 'code'"
                },
                "pattern": {
                    "type": "string", 
                    "description": "Filter by name pattern (case-insensitive substring match, e.g., 'assignment', '2024')"
                },
                "date_range": {
                    "type": "integer",
                    "description": "Filter by days ago (e.g., 7 for files modified in last 7 days)"
                },
                "size_range": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by file size in bytes [min_size, max_size]. Use null for no limit."
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort by: 'name', 'modified', 'size' (default: 'name')"
                },
                "sort_order": {
                    "type": "string",
                    "description": "Sort order: 'asc' or 'desc' (default: 'asc')"
                },
                "include_folders": {
                    "type": "boolean",
                    "description": "Include folders in results (default: true)"
                },
                "include_files": {
                    "type": "boolean", 
                    "description": "Include files in results (default: true)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (useful for large directories)"
                }
            },
            "required": []
        }
    },
    {
        "name": "filter_and_sort_by_modified",
        "description": "Finds recently modified items within specified days and sorts them by modification time",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file/folder paths to filter"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back for modified items"
                }
            },
            "required": ["items", "days"]
        }
    },
    {
        "name": "list_nested_folders_tree",
        "description": "Lists all nested folders in a tree structure format with proper hierarchy visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "target_dir": {
                    "type": "string",
                    "description": "Directory to search in (default: Desktop)"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse (default: 3)"
                }
            },
            "required": []
        }
    },
    {
        "name": "create_directory",
        "description": "Creates a new directory in the specified base path",
        "parameters": {
            "type": "object",
            "properties": {
                "target_dir": {
                    "type": "string",
                    "description": "Name of directory to create"
                },
                "base_path": {
                    "type": "string",
                    "description": "Base path where to create (Desktop, Documents, Downloads, etc.)",
                    "default": "Desktop"
                }
            },
            "required": ["target_dir"]
        }
    },
    {
        "name": "create_multiple_directories",
        "description": "Creates multiple directories in the specified base path",
        "parameters": {
            "type": "object",
            "properties": {
                "directories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of directory names to create (can include nested paths like 'folder/subfolder')"
                },
                "base_path": {
                    "type": "string",
                    "description": "Base path where to create (Desktop, Documents, Downloads, etc.)",
                    "default": "Desktop"
                }
            },
            "required": ["directories"]
        }
    },
    {
        "name": "delete_single_item",
        "description": "Deletes a single file or directory permanently",
        "parameters": {
            "type": "object",
            "properties": {
                "item_path": {
                    "type": "string",
                    "description": "Path to the file or directory to delete"
                }
            },
            "required": ["item_path"]
        }
    },
    {
        "name": "delete_multiple_items",
        "description": "Deletes multiple files and directories permanently",
        "parameters": {
            "type": "object",
            "properties": {
                "item_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of paths to files or directories to delete"
                }
            },
            "required": ["item_paths"]
        }
    },
    {
        "name": "delete_items_by_pattern",
        "description": "Deletes files and directories matching a pattern permanently. Use this for deleting files by type (e.g., 'all txt files', 'all temp files')",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match (e.g., '*.txt', 'test*', '*temp*', 'temp*')"
                },
                "target_dir": {
                    "type": "string",
                    "description": "Directory to search in (default: Desktop)"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "list_nested_folders_tree",
        "description": "Lists all nested folders in a tree structure format with proper hierarchy visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "target_dir": {
                    "type": "string",
                    "description": "Directory to search in (default: Desktop)"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse (default: 3)"
                }
            },
            "required": []
        }
    },
    {
        "name": "create_structured_hierarchy",
        "description": "Creates a structured folder hierarchy with predefined categories like Documents/Education/Work/Personal with subfolders for better organization",
        "parameters": {
            "type": "object",
            "properties": {
                "base_path": {
                    "type": "string",
                    "description": "Base path where the hierarchy should be created (default: Desktop)"
                },
                "hierarchy_type": {
                    "type": "string",
                    "description": "Type of hierarchy to create: 'documents' (Documents/Education/Work/Personal), 'projects' (Projects/Client/Personal/Archive), 'media' (Media/Photos/Videos/Music), or 'custom'",
                    "enum": ["documents", "projects", "media", "custom"]
                },
                "custom_structure": {
                    "type": "object",
                    "description": "Custom folder structure (only used when hierarchy_type is 'custom')",
                    "properties": {
                        "root_name": {"type": "string"},
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "subcategories": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "include_readme": {
                    "type": "boolean",
                    "description": "Whether to create a README file in each folder explaining its purpose (default: true)"
                }
            },
            "required": ["hierarchy_type"]
        }
    },
    {
        "name": "count_files_by_extension",
        "description": "Counts files by extension in the specified folder and provides statistics about file types",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Name of the folder to analyze (Desktop, Downloads, Documents, etc.)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_file_type_statistics",
        "description": "Gets file type statistics (documents, images, videos, etc.) for the specified folder",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Name of the folder to analyze (Desktop, Downloads, Documents, etc.)"
                }
            },
            "required": []
        }
    },
    {
        "name": "move_items_to_directory",
        "description": "Moves multiple files and folders to a destination directory",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file/folder paths to move"
                },
                "destination_dir": {
                    "type": "string",
                    "description": "Destination directory path"
                }
            },
            "required": ["items", "destination_dir"]
        }
    },
    {
        "name": "copy_multiple_items",
        "description": "Copies multiple files and folders to a destination directory",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file/folder paths to copy"
                },
                "destination_dir": {
                    "type": "string",
                    "description": "Destination directory path"
                }
            },
            "required": ["items", "destination_dir"]
        }
    },
    {
        "name": "rename_multiple_items",
        "description": "Renames multiple files and folders with new names",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_path": {"type": "string"},
                            "new_name": {"type": "string"}
                        },
                        "required": ["old_path", "new_name"]
                    },
                    "description": "List of (old_path, new_name) objects"
                }
            },
            "required": ["items"]
        }
    }
]

def get_function_schemas() -> List[Dict[str, Any]]:
    """
    Returns the list of function schemas for AI function calling.
    
    Returns:
        List[Dict[str, Any]]: List of function schemas in OpenAI function calling format
    """
    return FOLDERLY_FUNCTIONS 