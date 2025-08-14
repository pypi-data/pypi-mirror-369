#!/usr/bin/env python3
"""
Figma 图片获取器类
使用环境变量 FIGMA_ACCESS_TOKEN 存储访问令牌
获取指定节点的图片
"""

import requests
import json
import os
from typing import Dict, Any

class FigmaImageExtractor:
    def __init__(self, access_token: str = None):
        """初始化提取器"""
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("需要提供 access_token 或设置环境变量 FIGMA_ACCESS_TOKEN")
    
    def get_figma_images(self, file_key: str, node_ids: str, **kwargs) -> Dict[str, Any]:
        """获取Figma图片"""
        url = f"https://api.figma.com/v1/images/{file_key}"
        params = {"ids": node_ids}
        
        # 添加可选参数
        if "format" in kwargs:
            params["format"] = kwargs["format"]
        if "scale" in kwargs:
            params["scale"] = kwargs["scale"]
        if "version" in kwargs:
            params["version"] = kwargs["version"]
        if "svg_outline_text" in kwargs:
            params["svg_outline_text"] = kwargs["svg_outline_text"]
        if "svg_include_id" in kwargs:
            params["svg_include_id"] = kwargs["svg_include_id"]
        if "svg_include_node_id" in kwargs:
            params["svg_include_node_id"] = kwargs["svg_include_node_id"]
        if "svg_simplify_stroke" in kwargs:
            params["svg_simplify_stroke"] = kwargs["svg_simplify_stroke"]
        if "contents_only" in kwargs:
            params["contents_only"] = kwargs["contents_only"]
        if "use_absolute_bounds" in kwargs:
            params["use_absolute_bounds"] = kwargs["use_absolute_bounds"]
        
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def download_image(self, url: str, filename: str) -> bool:
        """下载图片"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"下载图片失败: {e}")
            return False
    
    def extract_images(self, file_key: str, node_ids: str, format: str = "png", scale: float = 1.0, output_dir: str = None) -> Dict[str, Any]:
        """提取图片"""
        print(f"正在获取文件 {file_key} 的图片...")
        print(f"目标节点: {node_ids}")
        print(f"图片格式: {format}")
        print(f"缩放比例: {scale}")
        
        # 获取图片信息
        images_data = self.get_figma_images(
            file_key, 
            node_ids, 
            format=format,
            scale=scale
        )
        
        if not images_data:
            return None
        
        print(f"文件名称: {images_data.get('name', 'Unknown')}")
        print(f"最后修改: {images_data.get('lastModified', 'Unknown')}")
        print(f"版本: {images_data.get('version', 'Unknown')}")
        
        # 处理图片
        images = images_data.get("images", {})
        
        if not images:
            print("未找到任何图片")
            return None
        
        print(f"\n找到 {len(images)} 个图片:")
        
        # 创建输出目录
        if not output_dir:
            output_dir = f"images_{file_key}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图片信息
        result = {
            "file_key": file_key,
            "file_name": images_data.get("name", ""),
            "last_modified": images_data.get("lastModified", ""),
            "version": images_data.get("version", ""),
            "target_nodes": node_ids,
            "format": format,
            "scale": scale,
            "images": {}
        }
        
        success_count = 0
        
        for node_id, image_url in images.items():
            if image_url:
                # 生成文件名
                filename = f"{output_dir}/{node_id}.{format}"
                
                print(f"\n下载图片: {node_id}")
                print(f"  URL: {image_url}")
                print(f"  保存到: {filename}")
                
                # 下载图片
                if self.download_image(image_url, filename):
                    print(f"  ✅ 下载成功")
                    success_count += 1
                    
                    # 获取文件大小
                    file_size = os.path.getsize(filename)
                    print(f"  文件大小: {file_size / 1024:.1f} KB")
                else:
                    print(f"  ❌ 下载失败")
                
                result["images"][node_id] = {
                    "url": image_url,
                    "filename": filename,
                    "status": "success" if os.path.exists(filename) else "failed"
                }
            else:
                print(f"\n节点 {node_id}: 无法生成图片")
                result["images"][node_id] = {
                    "url": None,
                    "filename": None,
                    "status": "failed"
                }
        
        # 保存图片信息到JSON文件
        info_file = f"{output_dir}/images_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== 下载完成 ===")
        print(f"成功下载: {success_count}/{len(images)} 个图片")
        print(f"图片保存在: {output_dir}/")
        print(f"图片信息保存在: {info_file}")
        
        return result

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python3 figma_image_extractor.py <file_key> [node_ids] [format] [scale]")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here your_node_id_here")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here your_node_id_here png 2")
        print("\n格式选项: jpg, png, svg, pdf")
        print("缩放选项: 0.01-4 (默认1)")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    
    # 检查是否提供了node_ids
    if len(sys.argv) > 2:
        node_ids = sys.argv[2]
    else:
        print("错误: 请提供节点ID")
        print("使用方法: python3 figma_image_extractor.py <file_key> <node_ids> [format] [scale]")
        print("提示: 使用 list_nodes_depth2 工具获取节点ID")
        sys.exit(1)
    
    # 获取格式参数
    image_format = "png"  # 默认格式
    if len(sys.argv) > 3:
        image_format = sys.argv[3]
    
    # 获取缩放参数
    scale = 1  # 默认缩放
    if len(sys.argv) > 4:
        try:
            scale = float(sys.argv[4])
        except ValueError:
            print("缩放参数必须是数字")
            sys.exit(1)
    
    try:
        extractor = FigmaImageExtractor()
        result = extractor.extract_images(file_key, node_ids, image_format, scale)
        
        if not result:
            sys.exit(1)
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
