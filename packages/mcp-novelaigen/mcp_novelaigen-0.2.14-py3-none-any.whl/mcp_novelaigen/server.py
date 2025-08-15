import os
import aiohttp
import zipfile
import io
import uuid
import random
import json
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Sequence
import logging

# --- File Logging Setup ---
log_file = Path(__file__).parent.parent.parent / "mcp_server_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=str(log_file),
    filemode='w'
)
logging.info("--- Server script started ---")
# --- End Logging Setup ---


from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

# --- 核心逻辑 ---

NOVELAI_API_CONFIG = {
    "BASE_URL": "https://image.novelai.net",
    "IMAGE_GENERATION_ENDPOINT": "/ai/generate-image",
    "DEFAULT_PARAMS": {
        "model": "nai-diffusion-4-5-full",
        "parameters": {
            "steps": 23,
            "scale": 5,
            "sampler": "k_euler_ancestral",
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "params_version": 3,
            "noise_schedule": "karras",
            "prefer_brownian": True,
            "add_original_image": False,
            "autoSmea": False,
            "cfg_rescale": 0,
            "controlnet_strength": 1,
            "deliberate_euler_ancestral_bug": False,
            "dynamic_thresholding": False,
            "legacy": False,
            "legacy_uc": False,
            "legacy_v3_extend": False,
            "normalize_reference_strength_multiple": True,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
        },
        "DEFAULT_NEGATIVE_PROMPT": "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page",
        "DEFAULT_ARTIST_STRING": "artist:ekita_kuro,[[[artist:yoneyama_mai]]],artist:toosaka_asagi,{{artist:syagamu}},{{{artist:momoko_(momopoco)}}},artist:drawdream1025",
    },
}
async def generate_image_from_novelai(args: Dict[str, Any], api_key: str) -> (bytes | None, list[str]):
    """
    根据参数调用 NovelAI API 生成图片。
    :return: 一个元组，包含 (图片字节, 调试消息列表)
    """
    debug_messages = ["[DEBUG] Starting image generation..."]
    
    
    # --- 读取配置 ---
    proxy_server = os.environ.get("PROXY_SERVER")
    project_base_path = os.environ.get("PROJECT_BASE_PATH", ".")
    server_port = os.environ.get("SERVER_PORT", "8000")
    image_key = os.environ.get("IMAGESERVER_IMAGE_KEY", "your-secret-key")
    var_http_url = os.environ.get("VarHttpUrl", "http://127.0.0.1")
    var_https_url = os.environ.get("VarHttpsUrl")
    debug_mode = True # Force debug mode
    debug_messages.append(f"[DEBUG] PROXY_SERVER: {proxy_server}")
    debug_messages.append(f"[DEBUG] PROJECT_BASE_PATH: {project_base_path}")


    # --- 参数校验和处理 ---
    debug_messages.append(f"[DEBUG] Received arguments: {args}")
    prompt = args.get("prompt")
    resolution = args.get("resolution")
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return None, debug_messages + [f"ValueError: 参数 'prompt' 不能为空。"]
    if not resolution or not isinstance(resolution, str):
        return None, debug_messages + [f"ValueError: 参数 'resolution' 不能为空。"]
    
    try:
        width_str, height_str = resolution.split('x')
        width, height = int(width_str.strip()), int(height_str.strip())
    except ValueError:
        return None, debug_messages + [f"ValueError: 参数 'resolution' 格式不正确，应为 '宽x高'，例如 '1024x1024'。"]

    # --- 构建请求 ---
    effective_negative_prompt = args.get("negative_prompt") or NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_NEGATIVE_PROMPT"]
    # Add the artist string to the prompt, same as the JS version
    artist_string = NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_ARTIST_STRING"]
    final_prompt = f"{prompt}, {artist_string}"
    debug_messages.append(f"[DEBUG] Final prompt: {final_prompt[:300]}...")
    debug_messages.append(f"[DEBUG] Negative prompt: {effective_negative_prompt[:300]}...")

    # Replicate the exact payload structure from the working JS plugin
    payload = {
        "action": "generate",
        "model": NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["model"],
        "input": final_prompt,
        "parameters": {
            **NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["parameters"],
            "width": width,
            "height": height,
            "seed": random.randint(0, 4294967295),
            "negative_prompt": effective_negative_prompt,
            # Add the required v4 structures
            "v4_prompt": {
                "caption": {"base_caption": final_prompt, "char_captions": []},
                "use_coords": False,
                "use_order": True,
            },
            "v4_negative_prompt": {
                "caption": {"base_caption": effective_negative_prompt, "char_captions": []},
                "legacy_uc": False,
            },
        },
    }
    
    debug_messages.append(f"[DEBUG] Final payload: {json.dumps(payload, indent=2)}")

    # --- 发送请求 ---
    debug_messages.append(f"[DEBUG] Preparing to send request to NovelAI API...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            f"{NOVELAI_API_CONFIG['BASE_URL']}{NOVELAI_API_CONFIG['IMAGE_GENERATION_ENDPOINT']}",
            json=payload,
            proxy=proxy_server if proxy_server and proxy_server.strip() else None,
            timeout=180.0
        ) as response:
            debug_messages.append(f"[DEBUG] Received response, status: {response.status}, content-type: {response.headers.get('content-type')}")

            # --- 处理响应 ---
            content_type = response.headers.get('content-type', '')
            is_zip_response = 'application/zip' in content_type or 'octet-stream' in content_type

            if response.status != 200 or not is_zip_response:
                error_text = await response.text()
                debug_messages.append(f"[ERROR] NovelAI API Error: {error_text}")
                return None, debug_messages

            debug_messages.append(f"[DEBUG] Reading response bytes...")
            response_bytes = await response.read()
            debug_messages.append(f"[DEBUG] Read {len(response_bytes)} bytes from response.")

    # --- 解压并保存图片 ---
    debug_messages.append(f"[DEBUG] Preparing to process ZIP file from response bytes...")
    novelai_image_dir = Path(project_base_path) / "image" / "novelaigen"
    novelai_image_dir.mkdir(parents=True, exist_ok=True)
    
    saved_images = []
    with io.BytesIO(response_bytes) as zip_buffer:
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            debug_messages.append(f"[DEBUG] ZIP contents: {zip_ref.namelist()}")
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # 只返回第一张找到的图片
                    debug_messages.append(f"[DEBUG] Found image: {file_info.filename}")
                    image_bytes = zip_ref.read(file_info.filename)
                    debug_messages.append("[DEBUG] Image extracted successfully.")
                    return image_bytes, debug_messages

    debug_messages.append("[ERROR] No valid image found in the returned ZIP file.")
    return None, debug_messages

# --- MCP 服务器实现 ---

async def serve() -> None:
    logging.info("Entering serve() function.")
    try:
        server = Server("mcp-novelaigen")
        logging.info("Server object created.")
        api_key = os.environ.get("NOVELAI_API_KEY")
        logging.info(f"API Key loaded (is_present: {bool(api_key)}).")

        @server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="NovelAIGen",
                    description="""## Prompt_Generation_Workflow (提示词生成工作流)
这是一个严格的、分步执行的AI思维链，用于生成高质量的图像提示。此工作流必须按顺序精确执行。

### **步骤 1: [核心动作分析与插件集成]**
- **输出**: 一个具体的姿势串

### **步骤 2: [电影化构图与场面调度]**
- **动作**: 构建场景的视觉框架。
  1.  确定最佳**摄像机视角**（例如：`cowboy shot`, `from above`, `low-angle shot`, `dutch angle`, `point of view`）。
  2.  使用25格网格系统（A1-E5）为每个角色分配中心点（例如：`|centers:b2,d4`），确保角色位置分布均衡（或根据艺术需要有意不均衡），并避免中心点直接相邻。
  3.  规划**光线布局**（光源、风格、阴影）和**景深**（例如：`shallow depth of field`, `bokeh`）。
- **输出**: 摄像机视角标签、角色网格位置标签、光线和景深相关标签。

### **步骤 3: [场景与氛围定义]**
- **动作**: 生成全局场景描述标签。此部分必须包含：**总人数**（例如：`2girls`, `1boy`）、**时间**（例如：`day`, `night`, `golden hour`）、**地点**（例如：`indoors`, `outdoors`, `bedroom`, `forest`）、**天气/环境**（例如：`rain`, `sunny`, `underwater`）、**核心道具**（例如：`bed`, `sword`, `book`）、**光影效果**（例如：`cinematic lighting`, `rim lighting`, `dramatic shadow`）、以及**情感/艺术基调**（例如：`serene`, `tense`, `erotic`, `melancholy`, `mysterious`)。
- **输出**: 一组定义全局场景、光照和情感氛围的标签。

### **步骤 4: [角色提示构建]**
- **动作**: 为每个角色生成独立的、极其详细的描述。严格遵循以下顺序：
  1.  **角色身份**（标准英文标签，如 `hu_tao_(genshin_impact)`）
  2.  **物种/种族**（如 `human`, `elf`）
  3.  **职业**（如 `sorceress`）
  4.  **服装**（主体、材质、颜色、内衣、配饰、状态如`wet`或`torn`），当剧情角色cosplay其他角色时在被cosplay角色的标签中加入"(Cosplay)"并放到剧情角色标签后面
  5.  **头部**（发型、发色、眼睛颜色、瞳孔形状、表情）
  6.  **身体**（乳房尺寸、体型、肌肉线条、皮肤细节如`sweat`或`tan lines`）
  7.  **动作**（**此处插入占位符`POSE_AWAITING_PLUGIN_RESULT`**）
  8.  **互动**（使用`source#/target#/mutual#`语法精确描述角色间的交互，如 `source#hand_on_hip`, `target#looking_at_source`）。
- **输出**: 每个角色的完整、独立的标签字符串，其中动作部分包含`POSE_AWAITING_PLUGIN_RESULT`占位符。

### **步骤 5: [负面提示与质量控制]**
- **动作**: 生成一套简洁而高效的负面提示（UC）。首先包含通用质量UC（如 `lowres`, `bad anatomy`, `worst quality`），然后根据需要为特定角色添加UC以避免不希望出现的特征（例如，`extra limbs`, `missing fingers`）。
- **输出**: 一个全局UC字符串，可能包含针对特定角色的额外UC。

### **步骤 6: [最终组装与占位符替换]**
- **动作**: 整合所有步骤的输出。将`PoseLibrarySearcher`插件返回的姿势标签字符串，精确替换掉每个角色描述中的`POSE_AWAITING_PLUGIN_RESULT`占位符。将全局场景标签与各角色标签用`|`分隔符连接，形成一个完整的、待格式化的提示草稿。
- **输出**: 一个完整的、逻辑连贯的、但尚未应用最终权重和格式化规则的提示字符串。

## NAI_Syntax_and_Formatting_Rules (NAI 语法与格式化规则)
【最终格式化规则库】在所有内容生成和验证后，由工作流的最后一步调用。严禁在生成内容的中间步骤应用这些规则。

### **权重 (Weighting)**
- **括号权重**: 使用 `{}` 增加权重（每层乘以1.05），使用 `[]` 降低权重（每层除以1.05）。应谨慎使用，以微调概念。
- **数值权重**: 使用 `w::tag::` 进行精确权重调整（w > 1 增强, 0 < w < 1 减弱）。适用于需要强力引导的关键标签。
- **负向权重**: 使用 `–w::tag::` 反转或移除概念（典型范围 -0.5 到 -3.0）。主要用于高级UC或概念消除。
- **混合权重**: 允许混合使用，例如 `–2::{sparkles}::`。

### **结构 (Structure)**
- **标签分隔符**: 所有标签必须由逗号 `, ` 分隔（逗号后带一个空格）。
- **多角色**: 使用 `|` 分隔符来区分全局场景描述和每个独立的角色描述。最终结构应为：`[全局标签] | [角色1标签] | [角色2标签] |centers:grid_code1,grid_code2`。
- **互动**: 使用 `source#action`, `target#action`, `mutual#action` 来精确定义角色间的互动。
- **定位**: 在提示的末尾使用 `|centers:grid_code` 来指定每个角色在25格系统中的精确位置。

### **核心原则与约束 (Core Principles and Constraints)**
- 默认不添加通用质量标签（如 `masterpiece`, `best quality`）或艺术家标签，除非用户在原始请求中明确指定。
- 严禁使用任何Stable Diffusion语法，如 `(full body:1.2)` 或 `AND`。
- 确保标签的内部一致性。例如，若场景为`rain`，角色应包含`wet hair`, `wet clothes`等相关标签。
- 避免使用相互矛盾的标签（例如，在同一个角色上同时使用 `smiling` 和 `crying`）。
- 优先使用更具体、更精确的标签（例如，用`hakama`代替`pants`，用`katana`代替`sword`）。
---
""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "核心【英文】提示词。请严格遵循文档中的工作流和语法规则。",
                            },
                            "resolution": {
                                "type": "string",
                                "description": "图片分辨率，例如 '1024x1024'。默认为 '832x1216'。",
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "反向提示词(UC)。用于避免不希望出现的特征。",
                            },
                        },
                        "required": ["prompt", "resolution"],
                    },
                )
            ]

        @server.call_tool()
        async def call_tool(
            name: str, arguments: dict
        ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls for NovelAI image generation."""
            if name != "NovelAIGen":
                raise ValueError(f"Unknown tool: {name}")

            if not api_key:
                return [TextContent(type="text", text="服务器配置错误: 环境变量 NOVELAI_API_KEY 未设置。")]

            image_bytes, debug_logs = await generate_image_from_novelai(arguments, api_key)
            
            log_text = "\n".join(debug_logs)

            if image_bytes:
                # Encode the image bytes to Base64 and provide the correct mimeType
                import base64
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                return [ImageContent(type="image", data=base64_image, mimeType="image/png")]
            else:
                error_message = f"Failed to generate image. See logs for details.\n\n--- DEBUG LOGS ---\n{log_text}"
                return [TextContent(type="text", text=error_message)]

        options = server.create_initialization_options()
        logging.info("Initialization options created.")
        async with stdio_server() as (read_stream, write_stream):
            logging.info("Entering stdio_server context. About to call server.run().")
            await server.run(read_stream, write_stream, options)
            logging.info("server.run() completed.")
            
    except Exception as e:
        logging.exception("An unhandled exception occurred in serve()")
        raise