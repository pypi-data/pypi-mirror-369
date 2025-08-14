#!/usr/bin/env python3
"""
Figma 特定节点树结构提取器类
使用环境变量 FIGMA_ACCESS_TOKEN 存储访问令牌
获取特定节点的depth=4树结构
"""

import requests
import json
import os
from typing import List, Dict, Any
from .file_saver import FigmaFileSaver

class FigmaTreeExtractor:
    def __init__(self, access_token: str = None):
        """初始化提取器"""
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("需要提供 access_token 或设置环境变量 FIGMA_ACCESS_TOKEN")
        self.file_saver = FigmaFileSaver()
    
    def get_specific_nodes(self, file_key: str, node_ids: str, depth: int = 4) -> Dict[str, Any]:
        """获取特定节点信息"""
        url = f"https://api.figma.com/v1/files/{file_key}/nodes"
        params = {
            "ids": node_ids,
            "depth": depth
        }
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def analyze_node_structure(self, node: Dict[str, Any], depth: int = 0, max_depth: int = 4) -> Dict[str, Any]:
        """递归分析节点结构"""
        node_info = {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
            "depth": depth,
            "absoluteBoundingBox": node.get("absoluteBoundingBox"),
            "characters": node.get("characters"),  # 文本内容
            "fills": node.get("fills"),  # 填充
            "strokes": node.get("strokes"),  # 描边
            "effects": node.get("effects"),  # 效果
            "componentId": node.get("componentId"),  # 组件ID
            "componentProperties": node.get("componentProperties"),  # 组件属性
            "interactions": node.get("interactions"),  # 交互
            "layoutMode": node.get("layoutMode"),  # 布局模式
            "cornerRadius": node.get("cornerRadius"),  # 圆角
            "strokeWeight": node.get("strokeWeight"),  # 描边宽度
            "opacity": node.get("opacity"),  # 透明度
            "blendMode": node.get("blendMode"),  # 混合模式
            "children": []  # 子节点
        }
        
        # 如果达到最大深度，停止递归
        if depth >= max_depth:
            return node_info
        
        # 递归处理子节点
        children = node.get("children", [])
        for child in children:
            child_info = self.analyze_node_structure(child, depth + 1, max_depth)
            node_info["children"].append(child_info)
        
        return node_info
    
    def count_nodes_by_type(self, node: Dict[str, Any]) -> Dict[str, int]:
        """统计各类型节点数量"""
        counts = {}
        
        def count_recursive(n):
            node_type = n.get("type", "UNKNOWN")
            counts[node_type] = counts.get(node_type, 0) + 1
            
            for child in n.get("children", []):
                count_recursive(child)
        
        count_recursive(node)
        return counts
    
    def find_nodes_by_type(self, node: Dict[str, Any], target_type: str) -> List[Dict[str, Any]]:
        """查找特定类型的节点"""
        results = []
        
        def search_recursive(n):
            if n.get("type") == target_type:
                results.append({
                    "id": n.get("id"),
                    "name": n.get("name"),
                    "depth": n.get("depth", 0)
                })
            
            for child in n.get("children", []):
                search_recursive(child)
        
        search_recursive(node)
        return results
    
    def extract_tree(self, file_key: str, node_ids: str, depth: int = 4) -> Dict[str, Any]:
        """提取节点树结构"""
        print(f"正在获取文件 {file_key} 的特定节点树结构 (depth={depth})...")
        print(f"目标节点: {node_ids}")
        
        # 获取特定节点信息
        nodes_data = self.get_specific_nodes(file_key, node_ids, depth)
        if not nodes_data:
            return None
        
        print(f"文件名称: {nodes_data.get('name', 'Unknown')}")
        print(f"最后修改: {nodes_data.get('lastModified', 'Unknown')}")
        print(f"版本: {nodes_data.get('version', 'Unknown')}")
        
        # 分析节点结构
        print("\n正在分析节点结构...")
        
        result = {
            "file_key": file_key,
            "file_name": nodes_data.get("name", ""),
            "last_modified": nodes_data.get("lastModified", ""),
            "version": nodes_data.get("version", ""),
            "target_nodes": node_ids,
            "nodes": {}
        }
        
        total_nodes = 0
        all_node_counts = {}
        
        # 处理每个目标节点
        for node_id in node_ids.split(","):
            if node_id in nodes_data.get("nodes", {}):
                node_data = nodes_data["nodes"][node_id]["document"]
                
                print(f"\n分析节点: {node_data.get('name', 'Unknown')} (ID: {node_id})")
                
                # 分析节点结构
                tree_structure = self.analyze_node_structure(node_data, depth=0, max_depth=depth)
                
                # 统计节点信息
                node_counts = self.count_nodes_by_type(tree_structure)
                node_total = sum(node_counts.values())
                total_nodes += node_total
                
                # 合并统计
                for node_type, count in node_counts.items():
                    all_node_counts[node_type] = all_node_counts.get(node_type, 0) + count
                
                print(f"节点 {node_id} 统计:")
                print(f"  总节点数: {node_total}")
                for node_type, count in sorted(node_counts.items()):
                    print(f"  {node_type}: {count}")
                
                result["nodes"][node_id] = {
                    "name": node_data.get("name", ""),
                    "type": node_data.get("type", ""),
                    "total_nodes": node_total,
                    "node_counts": node_counts,
                    "tree_structure": tree_structure
                }
        
        print(f"\n=== 总体统计 (depth={depth}) ===")
        print(f"总节点数: {total_nodes}")
        
        for node_type, count in sorted(all_node_counts.items()):
            print(f"{node_type}: {count}")
        
        # 查找重要节点类型
        important_types = ["FRAME", "TEXT", "RECTANGLE", "ELLIPSE", "INSTANCE", "COMPONENT"]
        print(f"\n=== 重要节点详情 ===")
        
        for node_type in important_types:
            if node_type in all_node_counts:
                all_nodes = []
                for node_id, node_info in result["nodes"].items():
                    nodes = self.find_nodes_by_type(node_info["tree_structure"], node_type)
                    all_nodes.extend(nodes)
                
                print(f"\n{node_type} 节点 ({len(all_nodes)}个):")
                for node in all_nodes[:5]:  # 只显示前5个
                    print(f"  - {node['name']} (ID: {node['id']}, 深度: {node['depth']})")
                if len(all_nodes) > 5:
                    print(f"  ... 还有 {len(all_nodes) - 5} 个")
        
        # 添加总体分析
        result["analysis"] = {
            "total_nodes": total_nodes,
            "node_counts": all_node_counts,
            "max_depth": depth
        }
        
        return result

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python3 figma_tree_extractor.py <file_key> [node_ids]")
        print("示例: python3 figma_tree_extractor.py your_figma_file_key_here")
        print("示例: python3 figma_tree_extractor.py your_figma_file_key_here your_node_id_here")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    
    # 检查是否提供了node_ids
    if len(sys.argv) > 2:
        node_ids = sys.argv[2]
    else:
        print("错误: 请提供节点ID")
        print("使用方法: python3 figma_tree_extractor.py <file_key> <node_ids>")
        print("提示: 使用 list_nodes_depth2 工具获取节点ID")
        sys.exit(1)
    
    try:
        extractor = FigmaTreeExtractor()
        result = extractor.extract_tree(file_key, node_ids)
        
        if result:
            # 使用文件保存器保存树结构
            save_result = self.file_saver.save_tree_structure(file_key, result, node_ids)
            tree_path = save_result["tree_path"]
            stats_path = save_result["stats_path"]
            
            print(f"\n特定节点树结构已保存到: {tree_path}")
            print(f"文件大小: {self.file_saver.get_file_size(tree_path):.1f} KB")
            print(f"统计信息已保存到: {stats_path}")
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
