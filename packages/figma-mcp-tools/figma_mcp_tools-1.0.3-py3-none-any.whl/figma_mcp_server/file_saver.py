#!/usr/bin/env python3
"""
Figma 文件保存工具类
统一管理所有Figma工具的文件保存逻辑
"""

import json
import os
from typing import Dict, Any, Optional

class FigmaFileSaver:
    def __init__(self, base_dir: str = None):
        """
        初始化文件保存器
        
        Args:
            base_dir: 基础目录，如果为None则使用当前工作目录
        """
        self.base_dir = base_dir or os.getcwd()
    
    def create_output_dir(self, dir_name: str) -> str:
        """
        创建输出目录
        
        Args:
            dir_name: 目录名称
            
        Returns:
            创建的目录的完整路径
        """
        output_dir = os.path.join(self.base_dir, dir_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def save_json_file(self, data: Dict[str, Any], filename: str, output_dir: str = None) -> str:
        """
        保存JSON文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
            output_dir: 输出目录，如果为None则保存到基础目录
            
        Returns:
            保存的文件完整路径
        """
        if output_dir:
            file_path = os.path.join(output_dir, filename)
        else:
            file_path = os.path.join(self.base_dir, filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def save_frame_info(self, file_key: str, result: Dict[str, Any], max_depth: int = 2) -> Dict[str, str]:
        """
        保存Frame信息文件
        
        Args:
            file_key: Figma文件键
            result: Frame提取结果
            max_depth: 最大深度
            
        Returns:
            包含文件路径的字典
        """
        frame_count = len(result["pages"])
        frame_ids = [page["pageInfo"]["frameId"] for page in result["pages"]]
        
        # 创建输出目录
        output_dir = self.create_output_dir(f"frame_info_{file_key}")
        
        # 保存详细结果
        detailed_file = f"detailed_frame_info_{file_key}.json"
        detailed_path = self.save_json_file(result, detailed_file, output_dir)
        
        # 保存简化结果
        simple_data = {
            "file_key": file_key,
            "frame_ids": frame_ids,
            "count": len(frame_ids),
            "max_depth": max_depth
        }
        simple_file = f"frame_ids_{file_key}.json"
        simple_path = self.save_json_file(simple_data, simple_file, output_dir)
        
        return {
            "detailed_path": detailed_path,
            "simple_path": simple_path,
            "output_dir": output_dir
        }
    
    def save_node_list(self, file_key: str, result: Dict[str, Any], max_depth: int = 2) -> Dict[str, str]:
        """
        保存节点列表文件
        
        Args:
            file_key: Figma文件键
            result: 节点列表结果
            max_depth: 最大深度
            
        Returns:
            包含文件路径的字典
        """
        node_ids = [node["id"] for node in result["node_list"]]
        
        # 创建输出目录
        output_dir = self.create_output_dir(f"node_list_{file_key}")
        
        # 保存详细结果
        detailed_file = f"node_list_{file_key}.json"
        detailed_path = self.save_json_file(result, detailed_file, output_dir)
        
        # 保存简化结果
        simple_data = {
            "file_key": file_key,
            "node_ids": node_ids,
            "count": len(node_ids),
            "max_depth": max_depth
        }
        simple_file = f"node_ids_{file_key}.json"
        simple_path = self.save_json_file(simple_data, simple_file, output_dir)
        
        return {
            "detailed_path": detailed_path,
            "simple_path": simple_path,
            "output_dir": output_dir
        }
    
    def save_tree_structure(self, file_key: str, result: Dict[str, Any], node_ids: str) -> Dict[str, str]:
        """
        保存树结构文件
        
        Args:
            file_key: Figma文件键
            result: 树结构结果
            node_ids: 目标节点ID
            
        Returns:
            包含文件路径的字典
        """
        # 创建输出目录
        output_dir = self.create_output_dir(f"tree_structure_{file_key}")
        
        # 保存完整结果
        tree_file = f"specific_nodes_{file_key}.json"
        tree_path = self.save_json_file(result, tree_file, output_dir)
        
        # 保存统计信息
        stats_data = {
            "file_key": file_key,
            "file_name": result.get("file_name", ""),
            "target_nodes": node_ids,
            "total_nodes": result["analysis"]["total_nodes"],
            "node_counts": result["analysis"]["node_counts"],
            "max_depth": result["analysis"]["max_depth"]
        }
        stats_file = f"specific_nodes_stats_{file_key}.json"
        stats_path = self.save_json_file(stats_data, stats_file, output_dir)
        
        return {
            "tree_path": tree_path,
            "stats_path": stats_path,
            "output_dir": output_dir
        }
    
    def save_images_info(self, file_key: str, result: Dict[str, Any]) -> Dict[str, str]:
        """
        保存图片信息文件
        
        Args:
            file_key: Figma文件键
            result: 图片提取结果
            
        Returns:
            包含文件路径的字典
        """
        # 创建输出目录
        output_dir = self.create_output_dir(f"images_{file_key}")
        
        # 保存图片信息
        info_file = "images_info.json"
        info_path = self.save_json_file(result, info_file, output_dir)
        
        return {
            "info_path": info_path,
            "output_dir": output_dir
        }
    
    def get_relative_path(self, file_path: str) -> str:
        """
        获取相对于基础目录的路径
        
        Args:
            file_path: 完整文件路径
            
        Returns:
            相对路径
        """
        return os.path.relpath(file_path, self.base_dir)
    
    def get_file_size(self, file_path: str) -> float:
        """
        获取文件大小（KB）
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（KB）
        """
        try:
            return os.path.getsize(file_path) / 1024
        except OSError:
            return 0.0
