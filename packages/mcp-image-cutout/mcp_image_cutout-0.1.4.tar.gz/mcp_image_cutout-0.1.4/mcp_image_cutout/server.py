# coding:utf-8
import base64
import io
import os
import logging
import tempfile
import contextlib
import httpx
import webbrowser
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
mcp = FastMCP("抠图工具")


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
            logger.warning("未检测到 VOLC_ACCESS_KEY 或 VOLC_SECRET_KEY，调用火山引擎接口可能失败")
        else:
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
            logger.info(f"请求参数: {form}")
            
            # 可选禁用代理，避免代理导致 SDK 返回异常内容
            with self._maybe_disable_proxies():
                resp = self.visual_service.cv_process(form)
            
            logger.info(f"火山引擎API完整响应: {resp}")
            
            # 检查响应结构的各种可能格式
            if resp:
                if 'data' in resp:
                    data = resp['data']
                    logger.info(f"响应data字段内容: {data}")
                    
                    # 检查多种可能的base64数据字段名
                    possible_fields = ['binary_data_base64', 'base64_images', 'images', 'result_images', 'image_base64']
                    for field in possible_fields:
                        if field in data:
                            result = data[field]
                            logger.info(f"找到图像数据字段 '{field}': {type(result)}")
                            if isinstance(result, list) and result:
                                logger.info("显著性分割处理成功")
                                return result
                            elif isinstance(result, str) and result:
                                logger.info("显著性分割处理成功（单图）")
                                return [result]
                
                # 如果data中没有找到，检查顶层结构
                possible_top_fields = ['binary_data_base64', 'base64_images', 'images', 'result_images']
                for field in possible_top_fields:
                    if field in resp:
                        result = resp[field]
                        logger.info(f"在顶层找到图像数据字段 '{field}': {type(result)}")
                        if isinstance(result, list) and result:
                            logger.info("显著性分割处理成功")
                            return result
                        elif isinstance(result, str) and result:
                            logger.info("显著性分割处理成功（单图）")
                            return [result]
                
                logger.error(f"未找到有效的base64图像数据，响应结构: {list(resp.keys()) if isinstance(resp, dict) else type(resp)}")
            else:
                logger.error("API返回空响应")
            
            return []

        except Exception as e:
            logger.error(f"显著性分割处理异常: {str(e)}", exc_info=True)
            return []

    async def upload_image_to_server(self, image_data: bytes, filename: str) -> dict[str, Any]:
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
                        files = {'file': (filename, f, 'image/png')}
                        response = await client.post(self.upload_url, files=files)
                    if response.status_code == 200:
                        result = response.json()
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
                        logger.error(f"上传请求失败: HTTP {response.status_code}")
                        # 返回更多原始信息，便于排查
                        try:
                            return {
                                "success": False,
                                "error": f"HTTP {response.status_code}",
                                "text": response.text,
                            }
                        except Exception:
                            return {"success": False, "error": f"HTTP {response.status_code}"}

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"上传图片异常: {str(e)}")
            return {"success": False, "error": str(e)}


# 创建全局处理器实例
cutter = VolcImageCutter()


@mcp.tool()
async def image_cutout(image_urls: list[str], open_in_browser: bool = True) -> Union[str, list[str]]:
    """
    对图像进行显著性分割抠图，自动上传到服务器并返回图片URL
    
    Args:
        image_urls: 图像URL列表，支持多张图像同时处理
        open_in_browser: 是否自动在默认浏览器中打开生成的图像，默认值：True

    Returns:
        单张图片时返回URL字符串，多张图片时返回URL列表
    """
    # 获取base64列表
    base64_images = cutter.saliency_segmentation(image_urls)

    if not base64_images:
        return "抠图失败：未获取到有效的抠图结果"

    response_text = f"显著性分割抠图处理完成！共生成 {len(base64_images)} 张抠图结果:\n\n"
    uploaded_urls = []
    failure_details = []

    for i, base64_data in enumerate(base64_images):
        response_text += f"第 {i + 1} 张抠图处理:\n"

        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)

            # 使用PIL验证图片
            image = Image.open(io.BytesIO(image_data))
            response_text += f"- 图片尺寸: {image.size}\n"

            # 上传到服务器
            filename = f"saliency_cutout_{i + 1}.png"
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
        # 如果启用了浏览器打开功能，打开所有生成的图像
        if open_in_browser and uploaded_urls:
            import time
            logger.info(f"正在浏览器中打开 {len(uploaded_urls)} 张抠图结果...")
            for i, url in enumerate(uploaded_urls):
                try:
                    # 使用 webbrowser.open_new_tab 确保在新标签页中打开
                    webbrowser.open_new_tab(url)
                    logger.info(f"已在浏览器中打开第 {i+1} 张抠图结果: {url}")
                    # 添加短暂延迟，避免同时打开多个标签页时浏览器响应不过来
                    if i < len(uploaded_urls) - 1:  # 最后一张图片不需要延迟
                        time.sleep(0.5)
                except Exception as e:
                    logger.error(f"无法在浏览器中打开图像 {url}: {str(e)}")
                    # 如果 open_new_tab 失败，尝试使用普通的 open 方法
                    try:
                        webbrowser.open(url)
                        logger.info(f"已用默认方式在浏览器中打开第 {i+1} 张抠图结果: {url}")
                    except Exception as e2:
                        logger.error(f"完全无法在浏览器中打开图像 {url}: {str(e2)}")
        
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
