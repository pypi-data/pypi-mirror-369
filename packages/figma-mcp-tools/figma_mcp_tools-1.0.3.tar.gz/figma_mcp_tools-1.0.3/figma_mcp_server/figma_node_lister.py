#!/usr/bin/env python3
"""
Figma 节点列表工具
列出Figma文件中所有节点的ID和名称，帮助用户找到需要的节点
深度限制为2，避免输出过多信息
"""

import requests
import json
import os
from typing import List, Dict, Any
from .file_saver import FigmaFileSaver

class FigmaNodeLister:
    def __init__(self, access_token: str = None):
        """初始化列表工具"""
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("需要提供 access_token 或设置环境变量 FIGMA_ACCESS_TOKEN")
        self.file_saver = FigmaFileSaver()
    
    def get_figma_file(self, file_key: str) -> Dict[str, Any]:
        """获取Figma文件信息"""
        url = f"https://api.figma.com/v1/files/{file_key}"
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def extract_nodes_info(self, node: Dict[str, Any], depth: int = 0, max_depth: int = 2, 
                          node_types: List[str] = None) -> List[Dict[str, Any]]:
        """递归提取节点信息"""
        nodes_info = []
        
        # 如果达到最大深度，停止递归
        if depth >= max_depth:
            return nodes_info
        
        # 提取当前节点信息
        node_type = node.get("type", "")
        
        # 如果指定了节点类型过滤，检查当前节点类型
        if node_types and node_type not in node_types:
            pass  # 跳过不匹配的节点类型
        else:
            node_info = {
                "id": node.get("id"),
                "name": node.get("name"),
                "type": node_type,
                "depth": depth,
                "parent_id": getattr(self, '_current_parent_id', None)
            }
            nodes_info.append(node_info)
        
        # 递归处理子节点
        children = node.get("children", [])
        for child in children:
            # 设置当前节点为父节点
            self._current_parent_id = node.get("id")
            child_nodes_info = self.extract_nodes_info(child, depth + 1, max_depth, node_types)
            nodes_info.extend(child_nodes_info)
        
        return nodes_info
    
    def list_nodes(self, file_key: str, node_types: str = "", max_depth: int = 2) -> Dict[str, Any]:
        """列出所有节点信息"""
        print(f"正在获取文件 {file_key} 的节点信息...")
        
        # 获取文件信息
        file_data = self.get_figma_file(file_key)
        if not file_data:
            return None
        
        # 获取文档根节点
        document = file_data.get("document", {})
        if not document:
            print("未找到文档数据")
            return None
        
        print(f"文件名称: {file_data.get('name', 'Unknown')}")
        
        # 解析节点类型过滤
        filter_types = []
        if node_types.strip():
            filter_types = [t.strip() for t in node_types.split(",")]
            print(f"过滤节点类型: {filter_types}")
        
        # 提取节点信息
        nodes_info = self.extract_nodes_info(document, depth=0, max_depth=max_depth, node_types=filter_types)
        
        # 按类型分组
        nodes_by_type = {}
        for node in nodes_info:
            node_type = node["type"]
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        # 输出结果
        if nodes_info:
            print(f"\n找到 {len(nodes_info)} 个节点 (depth={max_depth}):")
            
            # 创建结果结构
            result = {
                "file_key": file_key,
                "file_name": file_data.get("name", ""),
                "last_modified": file_data.get("lastModified", ""),
                "version": file_data.get("version", ""),
                "max_depth": max_depth,
                "total_nodes": len(nodes_info),
                "nodes_by_type": nodes_by_type,
                "node_list": nodes_info
            }
            
            # 按类型输出节点信息
            for node_type, nodes in nodes_by_type.items():
                print(f"\n📁 {node_type} ({len(nodes)} 个):")
                for i, node in enumerate(nodes, 1):
                    indent = "  " * node["depth"]
                    print(f"{indent}{i}. {node['name']} ({node['id']})")
            
            return result
        else:
            print("未找到任何节点")
            return None

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python3 figma_node_lister.py <file_key> [node_types] [max_depth]")
        print("示例: python3 figma_node_lister.py your_figma_file_key_here")
        print("示例: python3 figma_node_lister.py your_figma_file_key_here FRAME,COMPONENT")
        print("示例: python3 figma_node_lister.py your_figma_file_key_here FRAME,COMPONENT 2")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    node_types = sys.argv[2] if len(sys.argv) > 2 else ""
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    try:
        lister = FigmaNodeLister()
        result = lister.list_nodes(file_key, node_types, max_depth)
        
        if result:
            # 使用文件保存器保存节点列表
            save_result = self.file_saver.save_node_list(file_key, result, max_depth)
            detailed_path = save_result["detailed_path"]
            simple_path = save_result["simple_path"]
            
            print(f"\n详细结果已保存到: {detailed_path}")
            print(f"简化结果已保存到: {simple_path}")
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
