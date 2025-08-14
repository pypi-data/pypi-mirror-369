# coding:utf-8
import base64
import io
import os
import logging
import tempfile
import httpx
from typing import Any, Dict, Union
from PIL import Image
from volcengine.visual.VisualService import VisualService
from mcp.server.fastmcp import FastMCP

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("图像指令编辑工具")


class VolcImageEditor:
    """图像指令编辑处理器"""

    def __init__(self):
        self.visual_service = VisualService()
        self._setup_credentials()

    def _setup_credentials(self):
        """设置API凭证"""
        # 优先从环境变量获取
        ak = os.getenv('VOLC_ACCESS_KEY')
        sk = os.getenv('VOLC_SECRET_KEY')
        self.visual_service.set_ak(ak)
        self.visual_service.set_sk(sk)

    def seededit_process(self,
                        image_urls: list[str],
                        prompt: str = "",
                        seed: int = -1,
                        scale: float = 0.5) -> list[str]:
        """
        指令编辑，支持文本指令修改图像，直接返回base64列表

        Args:
           image_urls: 图像URL列表或本地文件路径列表，支持多张图像同时处理
                    支持格式：['https://example.com/image.jpg', '/path/to/local/image.png']
            prompt: 用于编辑图像的提示词，建议长度 <= 120字符，默认值："背景换成演唱会现场"
                   编辑指令使用自然语言即可，每次编辑使用单指令会更好
                   参考示例：
                   - 添加/删除实体：添加/删除xxx（删除图上的女孩/添加一道彩虹）
                   - 修改实体：把xxx改成xxx（把手里的鸡腿变成汉堡）
                   - 修改风格：改成xxx风格（改成漫画风格）
                   - 修改色彩：把xxx改成xx颜色（把衣服改成粉色的）
                   - 修改动作：修改表情动作（让他哭/笑/生气）
                   - 修改环境背景：背景换成xxx，在xxx（背景换成海边/在星空下）
            seed: 随机种子，作为确定扩散初始状态的基础，默认-1（随机）
                 若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致
            scale: 文本描述影响的程度，该值越大代表文本描述影响程度越大，且输入图片影响程度越小
                  默认值：0.5，取值范围：[0, 1]
        """
        try:
            # 参数验证
            scale = max(0.0, min(1.0, scale))  # 限制scale范围在[0, 1]

            # 构建请求表单
            form = {
                "req_key": "seededit_v3.0",  # 服务标识，固定值
                "image_urls": image_urls,  # 图像URL列表
                "prompt": prompt,  # 编辑指令
                "seed": seed,  # 随机种子
                "scale": scale  # 文本描述影响程度
            }

            # 记录日志信息
            if prompt and prompt.strip():
                logger.info(f"开始指令编辑，图像数量: {len(image_urls)}, 编辑指令: {prompt}, 影响强度: {scale}, 随机种子: {seed}")
            else:
                logger.info(f"开始图像处理，图像数量: {len(image_urls)}（无特定指令，将进行默认处理）, 影响强度: {scale}, 随机种子: {seed}")

            resp = self.visual_service.cv_process(form)

            if resp and 'data' in resp and 'binary_data_base64' in resp['data']:
                logger.info("指令编辑处理成功")
                # 直接返回base64列表
                return resp["data"]["binary_data_base64"]
            else:
                logger.error(f"指令编辑处理失败: {resp}")
                return []

        except Exception as e:
            logger.error(f"指令编辑处理异常: {str(e)}")
            return []

    def portrait_generation(self,
                          image_urls: list[str],
                          prompt: str = "",
                          width: int = 1024,
                          height: int = 1024,
                          gpen: float = 0.4,
                          skin: float = 0.3,
                          skin_unifi: float = 0.0,
                          gen_mode: str = "auto",
                          seed: int = -1) -> list[str]:
        """
        人物写真生成，基于输入的单人真人图片生成多样化写真，直接返回base64列表

        Args:
            image_urls: 图片URL列表，示例："https://图片1.png"
            prompt: 生图提示词，默认值："演唱会现场的合照，闪光灯拍摄"
            width: 生成图像的宽度，默认值：1024，取值范围：[512, 2048]
            height: 生成图像的高度，默认值：1024，取值范围：[512, 2048]
            gpen: 高清处理效果，越高人脸清晰度越高，建议使用默认值，默认值：0.4，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
            skin: 人脸美化效果，越高美颜效果越明显，建议使用默认值，默认值：0.3，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
            skin_unifi: 匀肤效果，越高均匀肤色去除瑕疵效果越明显，建议使用默认值，默认值：0，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
            gen_mode: 参考模式，取值说明：
                     "creative"：提示词模式（有prompt时自动切换此模式）（只参考人物的性别特征）
                     "reference"：全参考模式（无prompt时自动切换此模式）参考人物更多维度特征（性别、服饰、发型等）及背景
                     "reference_char"：人物参考模式，参考人物更多维度特征（性别、服饰、发型等），不参考背景
                     "auto"：自动模式，根据是否有prompt自动选择模式
            seed: 随机种子，作为确定扩散初始状态的基础，默认-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致
        """
        try:
            # 参数验证
            width = max(512, min(2048, width))  # 限制宽度范围
            height = max(512, min(2048, height))  # 限制高度范围
            gpen = max(0.0, min(1.0, round(gpen, 1)))  # 限制gpen范围并四舍五入到0.1
            skin = max(0.0, min(1.0, round(skin, 1)))  # 限制skin范围并四舍五入到0.1
            skin_unifi = max(0.0, min(1.0, round(skin_unifi, 1)))  # 限制skin_unifi范围并四舍五入到0.1

            # 自动选择生成模式
            if gen_mode == "auto":
                if prompt and prompt.strip():
                    gen_mode = "creative"  # 有提示词时使用创意模式
                else:
                    gen_mode = "reference"  # 无提示词时使用全参考模式

            # 构建请求表单
            form = {
                "req_key": "i2i_portrait_photo",  # 服务标识，固定值
                "image_urls": image_urls,  # 图片URL列表
                "prompt": prompt,  # 生图提示词
                "width": width,  # 生成图像宽度
                "height": height,  # 生成图像高度
                "gpen": gpen,  # 高清处理效果
                "skin": skin,  # 人脸美化效果
                "skin_unifi": skin_unifi,  # 匀肤效果
                "gen_mode": gen_mode,  # 参考模式
                "seed": seed  # 随机种子
            }

            # 记录日志信息
            if prompt and prompt.strip():
                logger.info(f"开始人物写真生成，图像数量: {len(image_urls)}, 写真风格: {prompt}, 尺寸: {width}x{height}, 模式: {gen_mode}")
            else:
                logger.info(f"开始人物写真生成，图像数量: {len(image_urls)}（使用默认风格）, 尺寸: {width}x{height}, 模式: {gen_mode}")

            resp = self.visual_service.cv_process(form)

            if resp and 'data' in resp and 'binary_data_base64' in resp['data']:
                logger.info("人物写真生成成功")
                # 直接返回base64列表
                return resp["data"]["binary_data_base64"]
            else:
                logger.error(f"人物写真生成失败: {resp}")
                return []

        except Exception as e:
            logger.error(f"人物写真生成异常: {str(e)}")
            return []



    async def upload_image_to_server(self, image_data: bytes, filename: str, content_type: str = "application/octet-stream") -> dict[str, Any]:
        """上传图片到服务器，尽量保留原始文件名与类型"""
        try:
            # 创建临时文件
            suffix = os.path.splitext(filename)[1] or ".bin"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name

            try:
                # 准备上传文件
                async with httpx.AsyncClient(timeout=30.0) as client:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (filename, f, content_type)}
                        logger.info(f"正在上传文件: {filename}, 大小: {os.path.getsize(temp_file_path)} 字节")
                        response = await client.post(
                            'https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile',
                            files=files
                        )
                        logger.info(f"上传响应状态码: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"上传响应内容: {result}")
                        if result.get('code') == 0:
                            logger.info(f"图片上传成功: {result['data']['url']}")
                            return {"success": True, "url": result['data']['url']}
                        else:
                            logger.error(f"上传失败: {result.get('msg', '未知错误')}")
                            return {"success": False, "error": result.get('msg', '未知错误')}
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
editor = VolcImageEditor()


@mcp.tool()
async def image_edit(
    image_urls: list[str],
    prompt: str = "背景换成演唱会现场",
    seed: int = -1,
    scale: float = 0.5
) -> Union[str, list[str]]:
    """
    图像进行指令编辑，支持通过文本描述来修改图像内容
    
    功能说明：
    - 支持物体移除等编辑操作
    - 支持添加、修改、替换图像中的元素
    - 支持风格转换、颜色调整等艺术效果
    - 支持局部编辑和全局编辑

    编辑技巧：
    - 建议长度 <= 120字符，prompt过长有概率出图异常或不生效
    - 编辑指令使用自然语言即可
    - 每次编辑使用单指令会更好
    - 局部编辑时指令描述尽量精准，尤其是画面有多个实体的时候，描述清楚对谁做什么
    - 发现编辑效果不明显的时候，可以调整一下编辑强度scale，数值越大越贴近指令执行
    - 尽量使用清晰的，分辨率高的底图，豆包模型生成的图片编辑效果会更好

    Args:
        image_urls: 图像URL列表，支持多张图像同时处理
        prompt: 用于编辑图像的提示词，建议长度 <= 120字符，默认值："背景换成演唱会现场"
               编辑指令使用自然语言即可，每次编辑使用单指令会更好
               参考示例：
               - 添加/删除实体：添加/删除xxx（删除图上的女孩/添加一道彩虹）
               - 修改实体：把xxx改成xxx（把手里的鸡腿变成汉堡）
               - 修改风格：改成xxx风格（改成漫画风格）
               - 修改色彩：把xxx改成xx颜色（把衣服改成粉色的）
               - 修改动作：修改表情动作（让他哭/笑/生气）
               - 修改环境背景：背景换成xxx，在xxx（背景换成海边/在星空下）
        seed: 随机种子，作为确定扩散初始状态的基础，默认-1（随机）
             若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致
        scale: 文本描述影响的程度，该值越大代表文本描述影响程度越大，且输入图片影响程度越小
              默认值：0.5，取值范围：[0, 1]

    Returns:
        单张图片时返回URL字符串，多张图片时返回URL列表
    """
    # 直接使用URL列表，不处理本地路径
    if not image_urls:
        return "图像编辑失败：未提供有效的图片URL"

    # 获取base64列表
    base64_images = editor.seededit_process(
        image_urls=image_urls,
        prompt=prompt,
        seed=seed,
        scale=scale
    )

    if not base64_images:
        return "图像编辑失败：未获取到有效的编辑结果"
    # 根据是否有prompt调整提示信息
    if prompt and prompt.strip():
        response_text = f"指令编辑完成！编辑指令：「{prompt}」\n共生成 {len(base64_images)} 张编辑结果:\n\n"
        filename_prefix = "seededit_edited"
    else:
        response_text = f"图像处理完成！共生成 {len(base64_images)} 张处理结果:\n\n"
        filename_prefix = "seededit_processed"
    uploaded_urls = []
    for i, base64_data in enumerate(base64_images):
        response_text += f"第 {i + 1} 张编辑结果:\n"
        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)
            # 使用PIL验证图片
            image = Image.open(io.BytesIO(image_data))
            response_text += f"- 图片尺寸: {image.size}\n"
            # 上传到服务器
            filename = f"{filename_prefix}_{i + 1}.png"
            upload_result = await editor.upload_image_to_server(image_data, filename)
            if upload_result.get('success'):
                uploaded_urls.append(upload_result['url'])
                response_text += f"- ✅ 上传成功: {upload_result['url']}\n"
            else:
                response_text += f"- ❌ 上传失败: {upload_result.get('error', '未知错误')}\n"

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
        return "图像编辑失败：所有图片上传失败"




@mcp.tool()
async def portrait_generation(
    image_urls: list[str],
    prompt: str = "演唱会现场的合照，闪光灯拍摄",
    width: int = 1024,
    height: int = 1024,
    gpen: float = 0.4,
    skin: float = 0.3,
    skin_unifi: float = 0.0,
    gen_mode: str = "auto",
    seed: int = -1
) -> Union[str, list[str]]:
    """
    使用人物写真生成功能，基于输入的单人真人图片生成多样化写真

    功能说明：
    - 基于单人真人图片的人脸特征进行写真生成
    - 支持多种写真风格和场景
    - 保持人物面部特征的高度相似性
    - 适用于互动娱乐、写真特效、电商营销等场景

    常用风格示例：
    - "古风写真" - 生成古典中国风格写真
    - "欧美复古风" - 欧美复古摄影风格
    - "日系清新风" - 日式小清新风格
    - "商务正装" - 专业商务形象
    - "婚纱写真" - 婚纱摄影风格
    - "艺术肖像" - 艺术化肖像风格
    - "时尚大片" - 时尚杂志风格
    - "校园青春" - 校园青春风格
    - "职业形象" - 各种职业装扮
    - "节日主题" - 节日庆典风格

    Args:
        image_urls: 单人真人图片URL列表，建议使用清晰的正面或半身照
        prompt: 生图提示词，描述想要的写真风格、场景或主题，默认值："演唱会现场的合照，闪光灯拍摄"
        width: 生成图像的宽度，默认值：1024，取值范围：[512, 2048]
        height: 生成图像的高度，默认值：1024，取值范围：[512, 2048]
        gpen: 高清处理效果，越高人脸清晰度越高，建议使用默认值，默认值：0.4，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        skin: 人脸美化效果，越高美颜效果越明显，建议使用默认值，默认值：0.3，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        skin_unifi: 匀肤效果，越高均匀肤色去除瑕疵效果越明显，建议使用默认值，默认值：0，取值范围：[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        gen_mode: 参考模式，取值说明：
                 "creative"：提示词模式（有prompt时自动切换此模式）（只参考人物的性别特征）
                 "reference"：全参考模式（无prompt时自动切换此模式）参考人物更多维度特征（性别、服饰、发型等）及背景
                 "reference_char"：人物参考模式，参考人物更多维度特征（性别、服饰、发型等），不参考背景
                 "auto"：自动模式，根据是否有prompt自动选择模式（推荐）
        seed: 随机种子，作为确定扩散初始状态的基础，默认-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致

    Returns:
        单张图片时返回URL字符串，多张图片时返回URL列表
    """
    # 直接使用URL列表，不处理本地路径
    if not image_urls:
        return "人物写真生成失败：未提供有效的图片URL"

    # 获取base64列表
    base64_images = editor.portrait_generation(
        image_urls=image_urls,
        prompt=prompt,
        width=width,
        height=height,
        gpen=gpen,
        skin=skin,
        skin_unifi=skin_unifi,
        gen_mode=gen_mode,
        seed=seed
    )
    if not base64_images:
        return "人物写真生成失败：未获取到有效的生成结果"
    # 根据是否有prompt调整提示信息
    if prompt and prompt.strip():
        response_text = f"人物写真生成完成！写真风格：「{prompt}」\n共生成 {len(base64_images)} 张写真结果:\n\n"
        filename_prefix = "portrait_styled"
    else:
        response_text = f"人物写真生成完成！共生成 {len(base64_images)} 张写真结果:\n\n"
        filename_prefix = "portrait_default"

    uploaded_urls = []

    for i, base64_data in enumerate(base64_images):
        response_text += f"第 {i + 1} 张写真结果:\n"

        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)

            # 使用PIL验证图片
            image = Image.open(io.BytesIO(image_data))
            response_text += f"- 图片尺寸: {image.size}\n"

            # 上传到服务器
            filename = f"{filename_prefix}_{i + 1}.png"
            upload_result = await editor.upload_image_to_server(image_data, filename)

            if upload_result.get('success'):
                uploaded_urls.append(upload_result['url'])
                response_text += f"- ✅ 上传成功: {upload_result['url']}\n"
            else:
                response_text += f"- ❌ 上传失败: {upload_result.get('error', '未知错误')}\n"

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
        return "人物写真生成失败：所有图片上传失败"




def main():
    """主函数入口"""
    logger.info("图像指令编辑工具MCP服务器启动...")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
