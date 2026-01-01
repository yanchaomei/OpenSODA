#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成PPT图片脚本
从PPT markdown文件中提取所有prompt，调用API生成图片
"""

import requests
import base64
import re
import os
import time
import sys

# API配置
API_KEY = "sk-dRvTF9BROJSzsqOG398dFaE6D1184b0590Db4bEfC34cAcC1"
API_URL = "https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

# PPT文件路径
PPT_FILE = "docs/competition/PPT_PRESENTATION.md"

# 输出目录
OUTPUT_DIR = "ppt_images_final_presentation"

# 公共Style Prompt (会添加到每个prompt前面)
COMMON_STYLE_PROMPT = """
**Style Reference & Execution Instructions:**

1.  **Art Style (Visio/Illustrator Aesthetic):**
    Generate a **professional academic architecture diagram** suitable for a top-tier computer science paper (CVPR/NeurIPS).
    * **Visuals:** Flat vector graphics, distinct geometric shapes, clean thin outlines, and soft pastel fills (Azure Blue, Slate Grey, Coral Orange).
    * **Layout:** Strictly follow the spatial arrangement defined below.
    * **Vibe:** Technical, precise, clean white background. NOT hand-drawn, NOT photorealistic, NOT 3D render, NO shadows/shading.

2.  **CRITICAL TEXT CONSTRAINTS (Read Carefully):**
    * **DO NOT render meta-labels:** Do not write words like "ZONE 1", "LAYOUT CONFIGURATION", "Input", "Output", or "Container" inside the image. These are structural instructions for YOU, not text for the image.
    * **ONLY render "Key Text Labels":** Only text inside double quotes (e.g., "[Text]") listed under "Key Text Labels" should appear in the diagram.
    * **Font:** Use a clean, bold Sans-Serif font (like Roboto or Helvetica) for all labels.

3.  **Visual Schema Execution:**
    Translate the following structural blueprint into the final image:

4.  图片里面的英文尽量改成中文

---

"""

def extract_prompts_from_ppt(ppt_file):
    """
    从PPT markdown文件中提取所有图片prompt
    返回: [(页码, 标题, prompt), ...]
    """
    with open(ppt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prompts = []
    
    # 使用正则匹配每一页的内容 (## 第X页：标题 开头，到下一个 ## 第Y页 或文件结尾)
    # 这样可以避免被代码块中的 --- 干扰
    # 注意：匹配 ## 第X页 格式（二级标题）
    page_pattern = r'(##\s+第(\d+)页[：:]\s*(.+?))\n(.*?)(?=\n##\s+第\d+页[：:]|\Z)'
    page_matches = re.findall(page_pattern, content, re.DOTALL)
    
    for match in page_matches:
        full_header, page_num, title, page_content = match
        title = title.strip()
        
        # 查找prompt (在代码块内)
        prompt_match = re.search(r'---BEGIN PROMPT---\s*(.*?)\s*---END PROMPT---', page_content, re.DOTALL)
        if prompt_match:
            prompt = prompt_match.group(1).strip()
            prompts.append((page_num, title, prompt))
            print(f"✓ 找到 第{page_num}页: {title}")
    
    return prompts


def generate_image(prompt, output_path, max_retries=3):
    """
    调用API生成图片
    """
    # 将公共style prompt与具体prompt合并
    full_prompt = COMMON_STYLE_PROMPT + prompt
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "16:9",
                "imageSize": "2K"
            }
        }
    }
    
    for attempt in range(max_retries):
        try:
            print(f"  正在生成... (尝试 {attempt + 1}/{max_retries})")
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=300  # 5分钟超时
            )
            
            if response.status_code != 200:
                print(f"  ✗ API错误: HTTP {response.status_code}")
                print(f"    响应: {response.text[:500]}")
                continue
            
            data = response.json()
            
            # 检查响应结构
            if "candidates" not in data:
                print(f"  ✗ 响应格式错误: 缺少 candidates")
                print(f"    响应: {data}")
                continue
            
            if len(data["candidates"]) == 0:
                print(f"  ✗ 响应格式错误: candidates 为空")
                continue
            
            candidate = data["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                print(f"  ✗ 响应格式错误: 缺少 content/parts")
                continue
            
            parts = candidate["content"]["parts"]
            if len(parts) == 0:
                print(f"  ✗ 响应格式错误: parts 为空")
                continue
            
            part = parts[0]
            if "inlineData" not in part or "data" not in part["inlineData"]:
                print(f"  ✗ 响应格式错误: 缺少 inlineData/data")
                continue
            
            img_data = part["inlineData"]["data"]
            
            # 保存图片
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(img_data))
            
            print(f"  ✓ 保存成功: {output_path}")
            return True
            
        except requests.exceptions.Timeout:
            print(f"  ✗ 请求超时")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ 网络错误: {e}")
        except Exception as e:
            print(f"  ✗ 未知错误: {e}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 10
            print(f"  等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    return False


def sanitize_filename(name):
    """
    清理文件名中的非法字符
    """
    # 移除或替换非法字符
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除或替换中文特殊符号
    name = re.sub(r'[：→]', '_', name)
    # 移除空格
    name = name.replace(' ', '_')
    # 限制长度
    if len(name) > 50:
        name = name[:50]
    return name


def main():
    print("=" * 60)
    print("PPT 图片批量生成工具")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ppt_path = os.path.join(script_dir, PPT_FILE)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    
    # 检查PPT文件
    if not os.path.exists(ppt_path):
        print(f"✗ 找不到PPT文件: {ppt_path}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    
    # 提取所有prompt
    print("\n[1/2] 提取Prompt...")
    prompts = extract_prompts_from_ppt(ppt_path)
    
    if not prompts:
        print("✗ 没有找到任何prompt!")
        sys.exit(1)
    
    print(f"\n共找到 {len(prompts)} 个prompt")
    
    # 生成图片
    print("\n[2/2] 生成图片...")
    success_count = 0
    fail_count = 0
    
    for i, (page, title, prompt) in enumerate(prompts, 1):
        print(f"\n--- [{i}/{len(prompts)}] 第{page}页: {title} ---")
        
        # 生成文件名
        safe_title = sanitize_filename(title)
        filename = f"page{page.zfill(2)}_{safe_title}.png"
        output_path = os.path.join(output_dir, filename)
        
        # 跳过已存在的文件
        if os.path.exists(output_path):
            print(f"  ⊙ 文件已存在，跳过")
            success_count += 1
            continue
        
        # 生成图片
        if generate_image(prompt, output_path):
            success_count += 1
        else:
            fail_count += 1
        
        # 避免API限流
        if i < len(prompts):
            print("  等待5秒...")
            time.sleep(5)
    
    # 汇总
    print("\n" + "=" * 60)
    print("生成完成!")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print(f"  输出目录: {output_dir}")
    print("=" * 60)
    
    # 列出生成的文件
    if success_count > 0:
        print("\n生成的图片:")
        for f in sorted(os.listdir(output_dir)):
            if f.endswith('.png'):
                fpath = os.path.join(output_dir, f)
                size = os.path.getsize(fpath) / 1024
                print(f"  - {f} ({size:.1f} KB)")


if __name__ == "__main__":
    main()

