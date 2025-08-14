# coding:utf-8
import base64
import io
import os
import logging
import tempfile
import contextlib
import httpx
from typing import Any, Dict, Union
from PIL import Image
from volcengine.visual.VisualService import VisualService
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlsplit, urlunsplit, quote

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("图像抠图工具")

class VolcImageCutter:
    """图像抠图处理器"""
    
    def __init__(self):
        self.visual_service = VisualService()
        # 允许通过环境变量覆盖上传地址，便于排查与切换环境
        self.upload_url = os.getenv(
            "MCP_UPLOAD_URL",
            "https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile",
        )
        self._setup_credentials()

    def _normalize_url(self, url: str) -> str:
        """将可能包含空格、中文或其他非 ASCII 字符的 URL 进行标准化编码。
        仅对 path/query/fragment 做百分号编码，确保外部拉取方可正常访问。
        """
        try:
            parts = urlsplit(url)
            # 对 path / query / fragment 进行编码，空格、中文等都会被编码
            encoded_path = quote(parts.path, safe="/-_.~")
            encoded_query = quote(parts.query, safe="=&-_.~")
            encoded_fragment = quote(parts.fragment, safe="-_.~")
            normalized = urlunsplit((parts.scheme, parts.netloc, encoded_path, encoded_query, encoded_fragment))
            return normalized
        except Exception:
            # 出现解析异常则原样返回，避免影响主流程
            return url

    @contextlib.contextmanager
    def _maybe_disable_proxies(self):
        """根据环境变量 MCP_DISABLE_PROXIES=1 临时禁用代理配置。
        主要用于避免 httpx/requests 从环境中读取 SOCKS/HTTP 代理导致失败。
        """
        if os.getenv("MCP_DISABLE_PROXIES") == "1":
            keys = [
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
                "NO_PROXY",
                "no_proxy",
            ]
            backup = {k: os.environ.get(k) for k in keys}
            try:
                for k in keys:
                    if k in os.environ:
                        os.environ.pop(k)
                yield
            finally:
                for k, v in backup.items():
                    if v is not None:
                        os.environ[k] = v
        else:
            # 不修改环境
            yield
    
    def _setup_credentials(self):
        """设置API凭证"""
        # 优先从环境变量获取
        ak = os.getenv('VOLC_ACCESS_KEY')
        sk = os.getenv('VOLC_SECRET_KEY')
        self.visual_service.set_ak(ak)
        self.visual_service.set_sk(sk)
        if not ak or not sk:
            logger.error(
                "缺少火山引擎凭证：请设置环境变量 VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY 后再启动。"
            )
            raise RuntimeError(
                "未配置 VOLC_ACCESS_KEY 或 VOLC_SECRET_KEY，服务启动中止。"
            )
        logger.info(
            f"已配置火山AK/SK: ak={ak[:6]}*** sk_len={len(sk)}"
        )
    
    def saliency_segmentation(self, image_urls: list[str]) -> list[str]:
        """显著性分割抠图，直接返回base64列表"""
        try:
            # 在调用第三方服务前，将 URL 规范化，避免空格/中文导致远端无法拉取
            normalized_urls = []
            for u in image_urls:
                nu = self._normalize_url(u)
                if nu != u:
                    logger.info(f"URL 已标准化: original='{u}' -> normalized='{nu}'")
                normalized_urls.append(nu)

            form = {
                "req_key": "saliency_seg",
                "image_urls": normalized_urls,
            }
            logger.info(f"开始显著性分割，图像数量: {len(image_urls)}")
            # 可选禁用代理，避免代理导致 SDK 返回异常内容
            with self._maybe_disable_proxies():
                resp = self.visual_service.cv_process(form)

            if resp and 'data' in resp and 'binary_data_base64' in resp['data']:
                logger.info("显著性分割处理成功")
                # 直接返回base64列表
                return resp["data"]["binary_data_base64"]
            else:
                logger.error(f"显著性分割处理失败: {resp}")
                return []

        except Exception as e:
            logger.error(f"显著性分割处理异常: {str(e)}")
            return []

    async def upload_image_to_server(self, image_data: bytes, filename: str, content_type: str = "image/png") -> dict[str, Any]:
        """上传图片到服务器"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name

            try:
                # 准备上传文件
                # trust_env=False 避免从环境变量读取代理配置
                async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (filename, f, content_type)}
                        logger.info(f"正在上传文件: {filename}, 大小: {os.path.getsize(temp_file_path)} 字节")
                        response = await client.post(self.upload_url, files=files)
                        logger.info(f"上传响应状态码: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"上传响应内容: {result}")
                        if result.get('code') == 0:
                            logger.info(f"图片上传成功: {result['data']['url']}")
                            return {"success": True, "url": result['data']['url']}
                        else:
                            # 记录尽可能多的错误上下文
                            logger.error(
                                f"上传失败: code={result.get('code')} msg={result.get('msg')} data={result.get('data')}"
                            )
                            return {
                                "success": False,
                                "error": result.get('msg', '未知错误'),
                                "code": result.get('code'),
                                "raw": result,
                            }
                    else:
                        response_text = response.text[:500] if hasattr(response, 'text') else 'No response text'
                        logger.error(f"上传请求失败: HTTP {response.status_code}, 响应内容: {response_text}")
                        return {"success": False, "error": f"HTTP {response.status_code}: {response_text}"}

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"上传图片异常: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局处理器实例
cutter = VolcImageCutter()


async def _upload_local_paths_to_urls(image_paths: list[str]) -> list[str]:
    """将本地图片路径批量上传为可访问URL。

    - 使用 PIL 打开并统一转为 PNG 字节再上传，确保与当前上传实现一致。
    - 失败的图片会跳过并记录日志。
    """
    uploaded_urls: list[str] = []
    logger.info(f"开始处理 {len(image_paths)} 个本地图片路径")
    
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }
    
    for idx, path in enumerate(image_paths):
        logger.info(f"处理第 {idx+1}/{len(image_paths)} 个文件: {path}")
        try:
            if not os.path.exists(path):
                logger.error(f"本地文件不存在: {path}")
                continue
                
            base = os.path.basename(path)
            name_no_ext, ext = os.path.splitext(base)
            if not name_no_ext:
                name_no_ext = f"local_{idx+1}"
            ext_lower = ext.lower()
            
            logger.info(f"文件信息: 基础名={name_no_ext}, 扩展名={ext_lower}")

            if ext_lower in mime_map:
                # 直接读取原始字节并按原格式上传
                try:
                    with open(path, "rb") as f:
                        raw = f.read()
                    filename = f"{name_no_ext}{ext_lower}"
                    content_type = mime_map[ext_lower]
                    logger.info(f"读取原始文件成功，大小: {len(raw)} 字节，准备上传...")
                    result = await cutter.upload_image_to_server(raw, filename, content_type)
                    logger.info(f"上传结果: {result}")
                except Exception as e:
                    logger.error(f"读取原图失败({path})，尝试转PNG: {e}")
                    # 回退：转PNG
                    with Image.open(path) as img:
                        img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        png_bytes = buf.getvalue()
                    filename = f"{name_no_ext}.png"
                    logger.info(f"转换为PNG成功，大小: {len(png_bytes)} 字节，准备上传...")
                    result = await cutter.upload_image_to_server(png_bytes, filename, "image/png")
                    logger.info(f"上传结果: {result}")
            else:
                # 未知/不常见格式，转PNG后上传
                try:
                    with Image.open(path) as img:
                        img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert("RGB")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        png_bytes = buf.getvalue()
                    filename = f"{name_no_ext}.png"
                    logger.info(f"转换未知格式为PNG成功，大小: {len(png_bytes)} 字节，准备上传...")
                    result = await cutter.upload_image_to_server(png_bytes, filename, "image/png")
                    logger.info(f"上传结果: {result}")
                except Exception as e:
                    logger.error(f"无法处理为PNG({path}): {e}")
                    continue
                    
            if result.get("success"):
                uploaded_urls.append(result["url"])
                logger.info(f"文件 {path} 上传成功，URL: {result['url']}")
            else:
                logger.error(f"上传失败({path}): {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"处理本地图片失败({path}): {str(e)}")
            import traceback
            logger.error(f"完整错误堆栈: {traceback.format_exc()}")
            
    logger.info(f"批量上传完成，成功 {len(uploaded_urls)} 个，失败 {len(image_paths) - len(uploaded_urls)} 个")
    return uploaded_urls


def _is_url(s: str) -> bool:
    try:
        return s.lower().startswith(("http://", "https://"))
    except Exception:
        return False

@mcp.tool()
async def image_cutout(image_urls: list[str]) -> Union[str, list[str]]:
    """
    使用火山引擎对图像进行显著性分割抠图，自动识别并分离图像主体
    
    ✨ 核心功能：
    - 🎯 显著性分割抠图：智能识别图像主体，精准去除背景
    - 📁 支持本地文件：直接使用本地图片路径，无需预先上传
    - 🌐 支持在线URL：处理网络图片链接
    - 🔄 混合输入：本地路径和URL可以混合使用
    - ☁️ 自动上传：处理结果自动上传到服务器并返回可访问链接
    
    📝 使用示例：
    - 本地文件：["/Users/name/image.jpg", "/path/to/photo.png"]
    - 网络链接：["https://example.com/image.jpg"]  
    - 混合使用：["/local/image.jpg", "https://web.com/image.png"]
    
    Args:
        image_urls: 图像路径列表，支持：
                   • 本地文件绝对路径：如 "/Users/name/Desktop/photo.jpg"
                   • 本地文件相对路径：如 "./images/photo.png"  
                   • 网络URL：如 "https://example.com/image.jpg"
                   • 混合列表：本地路径和URL可同时使用
                   
                   支持格式：JPG, PNG, JPEG, WEBP, GIF, BMP, TIFF

    Returns:
        🔄 处理结果：
        - 单张图片：直接返回抠图后的URL字符串
        - 多张图片：返回抠图后的URL列表
        
        💡 返回的URL可直接用于下载、展示或进一步处理
    """
    # 支持本地路径与URL混合：先将本地路径上传为URL
    urls: list[str] = []
    local_paths: list[str] = []
    for it in image_urls:
        if _is_url(it):
            urls.append(it)
        else:
            local_paths.append(it)
    
    if local_paths:
        logger.info(f"开始上传本地文件: {local_paths}")
        uploaded = await _upload_local_paths_to_urls(local_paths)
        logger.info(f"上传结果: {uploaded}")
        urls.extend(uploaded)
    
    logger.info(f"最终URL列表: {urls}")
    if not urls:
        return "抠图失败：未获得有效的图片URL"

    # 获取base64列表
    base64_images = cutter.saliency_segmentation(urls)

    if not base64_images:
        return "抠图失败：未获取到有效的抠图结果"

    response_text = f"显著性分割抠图处理完成！共生成 {len(base64_images)} 张抠图结果:\n\n"
    uploaded_urls = []
    failure_details = []

    for i, base64_data in enumerate(base64_images):
        response_text += f"第 {i+1} 张抠图处理:\n"

        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)

            # 使用PIL验证图片
            image = Image.open(io.BytesIO(image_data))
            response_text += f"- 图片尺寸: {image.size}\n"

            # 上传到服务器
            filename = f"saliency_cutout_{i+1}.png"
            upload_result = await cutter.upload_image_to_server(image_data, filename)

            if upload_result.get('success'):
                uploaded_urls.append(upload_result['url'])
                response_text += f"- ✅ 上传成功: {upload_result['url']}\n"
            else:
                err = upload_result.get('error', '未知错误')
                code = upload_result.get('code')
                response_text += f"- ❌ 上传失败: {err} (code={code})\n"
                # 捕获更详细的失败上下文（若有）
                raw = upload_result.get('raw')
                if raw:
                    response_text += f"- 失败原始响应: {raw}\n"
                text = upload_result.get('text')
                if text:
                    response_text += f"- 失败响应文本: {text[:300]}\n"
                failure_details.append({"index": i, **upload_result})

        except Exception as e:
            response_text += f"- ❌ 处理失败: {str(e)}\n"

        response_text += "==========================================\n"

    # 最终结果汇总
    if uploaded_urls:
        # 如果只有一张图片，直接返回URL字符串
        if len(uploaded_urls) == 1:
            return uploaded_urls[0]
        else:
            # 多张图片，返回URL列表
            return uploaded_urls
    else:
        # 返回详细的失败信息，帮助定位（例如鉴权、字段名或服务异常等）
        return response_text + "\n抠图失败：所有图片上传失败"

def main():
    """命令行入口点"""
    logger.info("启动抠图工具MCP服务器...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
