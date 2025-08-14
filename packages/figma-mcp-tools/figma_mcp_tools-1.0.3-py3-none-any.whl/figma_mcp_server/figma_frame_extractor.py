#!/usr/bin/env python3
"""
Figma Frame ID 提取器类
使用环境变量 FIGMA_ACCESS_TOKEN 存储访问令牌
返回详细的节点信息
"""

import requests
import json
import os
from typing import List, Dict, Any
from .file_saver import FigmaFileSaver

class FigmaFrameExtractor:
    def __init__(self, access_token: str = None):
        """初始化提取器"""
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
    
    def extract_node_info(self, node: Dict[str, Any], depth: int = 0, max_depth: int = 2) -> List[Dict[str, Any]]:
        """递归提取节点信息"""
        nodes_info = []
        
        # 提取当前节点信息
        node_info = {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
            "absoluteBoundingBox": node.get("absoluteBoundingBox"),
            "constraints": node.get("constraints"),
            "fills": node.get("fills"),
            "strokes": node.get("strokes"),
            "effects": node.get("effects"),
            "characters": node.get("characters"),  # 文本内容
            "style": node.get("style"),  # 文本样式
            "componentId": node.get("componentId"),  # 组件ID
            "componentProperties": node.get("componentProperties"),  # 组件属性
            "interactions": node.get("interactions"),  # 交互
            "transitionNodeID": node.get("transitionNodeID"),  # 过渡节点
            "transitionDuration": node.get("transitionDuration"),  # 过渡时长
            "transitionEasing": node.get("transitionEasing"),  # 过渡缓动
            "layoutMode": node.get("layoutMode"),  # 布局模式
            "primaryAxisSizingMode": node.get("primaryAxisSizingMode"),  # 主轴尺寸模式
            "counterAxisSizingMode": node.get("counterAxisSizingMode"),  # 交叉轴尺寸模式
            "primaryAxisAlignItems": node.get("primaryAxisAlignItems"),  # 主轴对齐
            "counterAxisAlignItems": node.get("counterAxisAlignItems"),  # 交叉轴对齐
            "paddingLeft": node.get("paddingLeft"),  # 左内边距
            "paddingRight": node.get("paddingRight"),  # 右内边距
            "paddingTop": node.get("paddingTop"),  # 上内边距
            "paddingBottom": node.get("paddingBottom"),  # 下内边距
            "itemSpacing": node.get("itemSpacing"),  # 项目间距
            "cornerRadius": node.get("cornerRadius"),  # 圆角半径
            "strokeWeight": node.get("strokeWeight"),  # 描边宽度
            "strokeAlign": node.get("strokeAlign"),  # 描边对齐
            "opacity": node.get("opacity"),  # 透明度
            "blendMode": node.get("blendMode"),  # 混合模式
            "isMask": node.get("isMask"),  # 是否为蒙版
            "effects": node.get("effects"),  # 效果
            "styles": node.get("styles"),  # 样式
            "boundVariables": node.get("boundVariables"),  # 绑定变量
            "overrides": node.get("overrides"),  # 覆盖
            "children": []  # 子节点（将在下面填充）
        }
        
        # 如果当前节点是FRAME类型，添加到列表
        if node.get("type") == "FRAME":
            nodes_info.append(node_info)
        
        # 如果达到最大深度，停止递归
        if depth >= max_depth:
            return nodes_info
        
        # 递归处理子节点
        children = node.get("children", [])
        for child in children:
            child_nodes_info = self.extract_node_info(child, depth + 1, max_depth)
            nodes_info.extend(child_nodes_info)
        
        return nodes_info
    
    def create_page_info(self, file_data: Dict[str, Any], document: Dict[str, Any]) -> Dict[str, Any]:
        """创建页面信息"""
        return {
            "pageInfo": {
                "name": document.get("name", ""),
                "english": document.get("name", ""),  # 可以根据需要翻译
                "frameId": document.get("id", ""),
                "type": document.get("type", ""),
                "devStatus": "READY_FOR_DEV"  # 可以根据需要设置
            }
        }
    
    def create_dimensions_info(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """创建尺寸信息"""
        bbox = node.get("absoluteBoundingBox", {})
        return {
            "dimensions": {
                "width": bbox.get("width", 0),
                "height": bbox.get("height", 0),
                "x": bbox.get("x", 0),
                "y": bbox.get("y", 0)
            }
        }
    
    def create_design_info(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """创建设计信息"""
        design_info = {
            "design": {
                "backgroundColor": {
                    "r": 1,
                    "g": 1,
                    "b": 1,
                    "a": 1
                }
            }
        }
        
        # 如果有背景色信息
        fills = node.get("fills", [])
        if fills and len(fills) > 0:
            fill = fills[0]
            if fill.get("type") == "SOLID":
                color = fill.get("color", {})
                design_info["design"]["backgroundColor"] = {
                    "r": color.get("r", 1),
                    "g": color.get("g", 1),
                    "b": color.get("b", 1),
                    "a": color.get("a", 1)
                }
        
        return design_info
    
    def extract_frames(self, file_key: str, max_depth: int = 2) -> Dict[str, Any]:
        """提取Frame节点信息"""
        print(f"正在获取文件 {file_key} 的信息...")
        
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
        
        # 提取节点信息
        nodes_info = self.extract_node_info(document, depth=0, max_depth=max_depth)
        
        # 输出结果
        if nodes_info:
            print(f"\n找到 {len(nodes_info)} 个Frame节点 (depth={max_depth}):")
            
            # 创建详细的结果结构
            result = {
                "file_key": file_key,
                "file_name": file_data.get("name", ""),
                "last_modified": file_data.get("lastModified", ""),
                "version": file_data.get("version", ""),
                "pages": []
            }
            
            for i, node_info in enumerate(nodes_info, 1):
                print(f"{i}. {node_info['name']} ({node_info['id']})")
                
                # 为每个frame创建详细页面信息
                page_data = {}
                page_data.update(self.create_page_info(file_data, node_info))
                page_data.update(self.create_dimensions_info(node_info))
                page_data.update(self.create_design_info(node_info))
                
                # 添加其他详细信息
                page_data["navigation"] = {
                    "components": [],
                    "note": "Navigation components would be populated here"
                }
                
                page_data["content"] = {
                    "sections": [],
                    "note": "Content sections would be populated at deeper depth levels"
                }
                
                page_data["interactions"] = node_info.get("interactions", [])
                page_data["assets"] = []
                page_data["notes"] = {
                    "layout": f"{node_info.get('layoutMode', 'Unknown')} layout system",
                    "responsive": f"{node_info.get('absoluteBoundingBox', {}).get('width', 0)}px width design",
                    "status": "Ready for development"
                }
                
                result["pages"].append(page_data)
            
            return result
        else:
            print("未找到任何Frame节点")
            return None

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python3 figma_frame_extractor.py <file_key>")
        print("示例: python3 figma_frame_extractor.py your_figma_file_key_here")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    
    try:
        extractor = FigmaFrameExtractor()
        result = extractor.extract_frames(file_key)
        
        if result:
            # 使用文件保存器保存Frame信息
            save_result = self.file_saver.save_frame_info(file_key, result, max_depth)
            detailed_path = save_result["detailed_path"]
            simple_path = save_result["simple_path"]
            
            print(f"\n详细结果已保存到: {detailed_path}")
            print(f"简化结果已保存到: {simple_path}")
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
