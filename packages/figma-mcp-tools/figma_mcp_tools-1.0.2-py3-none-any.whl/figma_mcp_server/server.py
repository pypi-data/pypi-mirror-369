#!/usr/bin/env python3
"""
Figma MCP Server
将Figma工具功能暴露为MCP工具，供AI助手调用
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# 导入我们的Figma工具类
from .figma_tree_extractor import FigmaTreeExtractor
from .figma_image_extractor import FigmaImageExtractor
from .figma_frame_extractor import FigmaFrameExtractor
from .figma_node_lister import FigmaNodeLister

# MCP相关导入
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("请先安装MCP: pip install mcp")
    sys.exit(1)

# 创建MCP服务器
server = Server("figma-tools")

# Define tool list
FIGMA_TOOLS = [
    {
        "name": "extract_figma_tree",
        "title": "Extract Figma Tree Structure",
        "description": "Extract complete tree structure information of Figma nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string", 
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "depth": {
                    "type": "integer",
                    "description": "Tree structure depth, default 4",
                    "default": 4
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "download_figma_images",
        "title": "Download Figma Images",
        "description": "Download images of Figma nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string",
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "format": {
                    "type": "string",
                    "description": "Image format: png, jpg, svg, pdf",
                    "default": "png"
                },
                "scale": {
                    "type": "number",
                    "description": "Scale ratio: 0.01-4",
                    "default": 1.0
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "get_complete_node_data",
        "title": "Get Complete Node Data",
        "description": "Get complete data of Figma nodes (tree structure + images) and organize into folders. Output structure designed for AI understanding: nodesinfo.json provides structured data, image files provide visual reference. ⚠️ Note: This tool will consume a lot of API quota, recommend using list_nodes_depth2 to get node IDs first",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string",
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "image_format": {
                    "type": "string",
                    "description": "Image format: png, jpg, svg, pdf",
                    "default": "png"
                },
                "image_scale": {
                    "type": "number",
                    "description": "Image scale ratio: 0.01-4",
                    "default": 1.0
                },
                "tree_depth": {
                    "type": "integer",
                    "description": "Tree structure depth",
                    "default": 4
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "extract_frame_nodes",
        "title": "Extract Frame Nodes",
        "description": "Extract Frame node information from Figma file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth, default 2",
                    "default": 2
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "list_nodes_depth2",
        "title": "List Nodes",
        "description": "List all node IDs and names in Figma file (depth limited to 2), help users find needed nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_types": {
                    "type": "string",
                    "description": "Node types to include, separated by commas (e.g.: FRAME,COMPONENT,TEXT), leave empty for all types",
                    "default": ""
                }
            },
            "required": ["file_key"]
        }
    }
]

class FigmaMCPServer:
    def __init__(self):
        # Auto-setup virtual environment path
        self.setup_environment()
        
        self.access_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            print("Warning: FIGMA_ACCESS_TOKEN environment variable not set")
        
        self.tree_extractor = FigmaTreeExtractor(self.access_token) if self.access_token else None
        self.image_extractor = FigmaImageExtractor(self.access_token) if self.access_token else None
        self.frame_extractor = FigmaFrameExtractor(self.access_token) if self.access_token else None
        self.node_lister = FigmaNodeLister(self.access_token) if self.access_token else None
    
    def setup_environment(self):
        """Setup environment, including virtual environment path"""
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if virtual environment exists
        venv_path = os.path.join(script_dir, "figma_env")
        if os.path.exists(venv_path):
            # Add virtual environment site-packages to Python path
            if sys.platform == "win32":
                site_packages = os.path.join(venv_path, "Lib", "site-packages")
            else:
                site_packages = os.path.join(venv_path, "lib", "python3.10", "site-packages")
            
            if os.path.exists(site_packages):
                sys.path.insert(0, site_packages)
        
        # Add current directory to Python path
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
    
    def get_node_name(self, tree_data: Dict[str, Any], node_id: str) -> str:
        """Get node name from tree structure data"""
        try:
            if "nodes" in tree_data and node_id in tree_data["nodes"]:
                node_name = tree_data["nodes"][node_id].get("name", "")
                return node_name.replace(':', '_').replace('/', '_').replace('\\', '_').strip() or f"node_{node_id.replace(':', '_')}"
            return f"node_{node_id.replace(':', '_')}"
        except Exception:
            return f"node_{node_id.replace(':', '_')}"
    
    def organize_files(self, file_key: str, node_ids: str, node_name: str, tree_result: Dict, image_result: Dict) -> Dict[str, Any]:
        """Organize files to specified folder"""
        import shutil
        
        # Create target folder
        first_node_id = node_ids.split(",")[0]
        target_dir = f"{node_name}_{first_node_id}"
        os.makedirs(target_dir, exist_ok=True)
        
        result = {
            "target_dir": target_dir,
            "files": {}
        }
        
        # Save tree structure file
        tree_file = f"{target_dir}/nodesinfo.json"
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree_result, f, indent=2, ensure_ascii=False)
        result["files"]["nodesinfo"] = tree_file
        
        # Process image files
        if image_result and "images" in image_result:
            for node_id, image_info in image_result["images"].items():
                if image_info.get("status") == "success" and image_info.get("filename"):
                    # Move image file to target directory
                    old_path = image_info["filename"]
                    new_path = f"{target_dir}/{node_id}.{image_result.get('format', 'png')}"
                    if os.path.exists(old_path):
                        shutil.move(old_path, new_path)
                        result["files"]["image"] = new_path
        
        return result

# 创建Figma MCP服务器实例（延迟初始化）
figma_server = None

def get_figma_server():
    """Get Figma server instance (lazy initialization)"""
    global figma_server
    if figma_server is None:
        figma_server = FigmaMCPServer()
    return figma_server

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    try:
        tools = []
        for tool_def in FIGMA_TOOLS:
            tools.append(Tool(**tool_def))
        
        return tools
    except Exception as e:
        logger.error(f"handle_list_tools error: {e}")
        raise

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent | ImageContent]:
    """Handle tool calls"""
    try:
        if name == "extract_figma_tree":
            return await handle_extract_tree(arguments)
        elif name == "download_figma_images":
            return await handle_download_images(arguments)
        elif name == "get_complete_node_data":
            return await handle_complete_data(arguments)
        elif name == "extract_frame_nodes":
            return await handle_extract_frames(arguments)
        elif name == "list_nodes_depth2":
            return await handle_list_nodes(arguments)
        else:
            logger.warning(f"Unknown tool: {name}")
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"handle_call_tool error: {e}")
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]

async def handle_extract_tree(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tree structure extraction"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    depth = arguments.get("depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.tree_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.tree_extractor.extract_tree(file_key, node_ids, depth)
    if not result:
        return [TextContent(type="text", text="Failed to extract tree structure")]
    
    # Save to file
    output_file = f"specific_nodes_{file_key}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        output_path = os.path.abspath(output_file)
        return [
            TextContent(
                type="text", 
                text=f"✅ Tree structure extraction successful!\n\n📁 File: {output_path}\n📊 Total nodes: {result['analysis']['total_nodes']}\n📋 Node type statistics: {json.dumps(result['analysis']['node_counts'], ensure_ascii=False, indent=2)}"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return [
            TextContent(
                type="text", 
                text=f"⚠️ Tree structure extraction completed but file generation failed!\n\n📊 Total nodes: {result['analysis']['total_nodes']}\n📋 Node type statistics: {json.dumps(result['analysis']['node_counts'], ensure_ascii=False, indent=2)}\n\nError: {str(e)}"
            )
        ]

async def handle_download_images(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle image download"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    format = arguments.get("format", "png")
    scale = arguments.get("scale", 1.0)
    
    figma_server = get_figma_server()
    if not figma_server.image_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.image_extractor.extract_images(file_key, node_ids, format, scale)
    if not result:
        return [TextContent(type="text", text="Failed to download images")]
    
    success_count = sum(1 for img in result["images"].values() if img.get("status") == "success")
    total_count = len(result["images"])
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Image download completed!\n\nSuccessfully downloaded: {success_count}/{total_count} images\nFormat: {format}\nScale: {scale}\nImages saved in: images_{file_key}/"
        )
    ]

async def handle_complete_data(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle complete data retrieval"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    image_format = arguments.get("image_format", "png")
    image_scale = arguments.get("image_scale", 1.0)
    tree_depth = arguments.get("tree_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.tree_extractor or not figma_server.image_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    # Step 1: Get tree structure
    tree_result = figma_server.tree_extractor.extract_tree(file_key, node_ids, tree_depth)
    if not tree_result:
        return [TextContent(type="text", text="Failed to get tree structure")]
    
    # Step 2: Get node name
    first_node_id = node_ids.split(",")[0]
    node_name = figma_server.get_node_name(tree_result, first_node_id)
    
    # Step 3: Download images
    image_result = figma_server.image_extractor.extract_images(file_key, node_ids, image_format, image_scale)
    if not image_result:
        return [TextContent(type="text", text="Failed to download images")]
    
    # Step 4: Organize files
    organize_result = figma_server.organize_files(file_key, node_ids, node_name, tree_result, image_result)
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Complete data retrieval successful!\n\n📁 Output folder: {organize_result['target_dir']}\n📊 Total nodes: {tree_result['analysis']['total_nodes']}\n🖼️ Image format: {image_format}\n📏 Scale ratio: {image_scale}\n\nIncluded files:\n- nodesinfo.json (node details)\n- nodesstatus.json (node statistics)\n- image.json (image information)\n- summary.json (summary information)\n- Image files"
        )
    ]

async def handle_extract_frames(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Frame node extraction"""
    file_key = arguments["file_key"]
    max_depth = arguments.get("max_depth", 2)
    
    figma_server = get_figma_server()
    if not figma_server.frame_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.frame_extractor.extract_frames(file_key, max_depth)
    if not result:
        return [TextContent(type="text", text="Failed to extract Frame nodes")]
    
    frame_count = len(result["pages"])
    frame_ids = [page["pageInfo"]["frameId"] for page in result["pages"]]
    
    # Save detailed result to file
    output_file = f"detailed_frame_info_{file_key}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        output_path = os.path.abspath(output_file)
    except Exception as e:
        logger.error(f"Failed to save detailed frame file: {e}")
        output_path = "failed_to_save"
    
    # Save simplified frame IDs to file
    simple_output_file = f"frame_ids_{file_key}.json"
    try:
        with open(simple_output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "file_key": file_key,
                "frame_ids": frame_ids,
                "count": len(frame_ids)
            }, f, indent=2, ensure_ascii=False)
        simple_output_path = os.path.abspath(simple_output_file)
    except Exception as e:
        logger.error(f"Failed to save simple frame file: {e}")
        simple_output_path = "failed_to_save"
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Frame node extraction successful!\n\n📋 Found {frame_count} Frame nodes (depth={max_depth}):\n" + "\n".join([f"- {page['pageInfo']['name']} (ID: {page['pageInfo']['frameId']})" for page in result["pages"]]) + f"\n\n📁 Detailed result saved to: {output_path}\n📁 Simplified result saved to: {simple_output_path}"
        )
    ]

async def handle_list_nodes(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle node list retrieval"""
    file_key = arguments["file_key"]
    node_types = arguments.get("node_types", "")
    
    figma_server = get_figma_server()
    if not figma_server.node_lister:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.node_lister.list_nodes(file_key, node_types, max_depth=2)
    if not result:
        return [TextContent(type="text", text="Failed to get node list")]
    
    # Save detailed result to file
    output_file = f"node_list_{file_key}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        output_path = os.path.abspath(output_file)
    except Exception as e:
        logger.error(f"Failed to save detailed node list file: {e}")
        output_path = "failed_to_save"
    
    # Save simplified node IDs to file
    node_ids = [node["id"] for node in result["node_list"]]
    simple_output_file = f"node_ids_{file_key}.json"
    try:
        with open(simple_output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "file_key": file_key,
                "node_ids": node_ids,
                "count": len(node_ids),
                "max_depth": 2
            }, f, indent=2, ensure_ascii=False)
        simple_output_path = os.path.abspath(simple_output_file)
    except Exception as e:
        logger.error(f"Failed to save simple node list file: {e}")
        simple_output_path = "failed_to_save"
    
    # Build output text
    output_lines = [f"✅ Node list retrieval successful!\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Total nodes: {result['total_nodes']} (depth=2)")
    
    if node_types:
        output_lines.append(f"Filtered types: {node_types}")
    
    output_lines.append("\n📋 Node list:")
    
    # Output nodes by type
    for node_type, nodes in result["nodes_by_type"].items():
        output_lines.append(f"\n📁 {node_type} ({len(nodes)} items):")
        for node in nodes:
            indent = "  " * node["depth"]
            output_lines.append(f"{indent}- {node['name']} (ID: {node['id']})")
    
    output_lines.append(f"\n📁 Detailed result saved to: {output_path}")
    output_lines.append(f"📁 Simplified result saved to: {simple_output_path}")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def main():
    """Main function"""
    logger.info("Figma MCP server starting")
    
    # Check environment variables
    if not os.getenv("FIGMA_ACCESS_TOKEN"):
        logger.warning("FIGMA_ACCESS_TOKEN not set")
        print("Warning: FIGMA_ACCESS_TOKEN environment variable not set")
        print("Please set: export FIGMA_ACCESS_TOKEN='your_token_here'")
    else:
        logger.info("FIGMA_ACCESS_TOKEN is set")
    
    init_options = server.create_initialization_options()
    
    # Start MCP server
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                init_options,
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
