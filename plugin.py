"""MONITOR - 屏幕监视插件

截取当前活动屏幕并进行高斯模糊处理后发送，仅支持 Windows 平台。
"""

from __future__ import annotations

import base64
import io
import sys
from typing import Any

from maibot_sdk import (
    CONFIG_RELOAD_SCOPE_SELF,
    Command,
    Field,
    MaiBotPlugin,
    PluginConfigBase,
)

try:
    from PIL import Image, ImageFilter, ImageGrab

    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

HELP_TEXT = (
    "━━━ MONITOR 屏幕监视插件 ━━━\n"
    "\n"
    "⚠ 警告：本插件会截取当前屏幕内容！\n"
    "请仅在私人/安全环境中使用。\n"
    "\n"
    "支持的命令：\n"
    "  /监视         截图当前屏幕并模糊发送\n"
    "  /sj           同上\n"
    "  /监视 help    显示本帮助\n"
    "\n"
    "权限说明：\n"
    "  permission.allow_all = true  放行所有用户\n"
    "  permission.allow_all = false 则仅 allowed_user_ids 内的用户可用\n"
    "\n"
    "提示：\n"
    "  本插件仅支持 Windows 系统\n"
    "  截图将进行高斯模糊处理后再发送"
)


class PluginSection(PluginConfigBase):
    __ui_label__ = "插件设置"

    enabled: bool = Field(default=False, description="是否启用插件")
    config_version: str = Field(default="0.1.0", description="配置版本")


class PermissionSection(PluginConfigBase):
    __ui_label__ = "权限设置"

    allow_all: bool = Field(
        default=False,
        description="允许所有用户使用（开启后忽略 allowed_user_ids 限制）",
    )
    allowed_user_ids: list[str] = Field(
        default=[],
        description="允许使用命令的用户 ID 列表。allow_all 关闭时生效",
    )


class BlurSection(PluginConfigBase):
    __ui_label__ = "模糊设置"

    radius: int = Field(
        default=20,
        description="高斯模糊半径（数值越大越模糊）",
        ge=5,
        le=100,
    )


class MonitorConfig(PluginConfigBase):
    plugin: PluginSection = Field(default_factory=PluginSection)
    permission: PermissionSection = Field(default_factory=PermissionSection)
    blur: BlurSection = Field(default_factory=BlurSection)


class MonitorPlugin(MaiBotPlugin):
    """MONITOR - 屏幕监视插件"""

    config_model = MonitorConfig

    async def on_load(self) -> None:
        if sys.platform != "win32":
            self.ctx.logger.error("MONITOR 插件仅支持 Windows 平台，当前平台无法加载")
            raise RuntimeError("MONITOR 插件仅支持 Windows 平台")
        if not _HAS_PIL:
            self.ctx.logger.error("MONITOR 插件依赖 Pillow，请安装: uv add Pillow")
            raise RuntimeError("缺少 Pillow 依赖")
        self.ctx.logger.info("MONITOR 插件已加载")

    async def on_unload(self) -> None:
        return None

    async def on_config_update(
        self, scope: str, config_data: dict[str, object], version: str
    ) -> None:
        del config_data
        del version
        if scope == CONFIG_RELOAD_SCOPE_SELF:
            self.ctx.logger.info("MONITOR 插件配置已更新")

    @Command(
        "monitor_screenshot",
        description="截取当前活动屏幕并进行模糊处理（命令: /监视 或 /sj）",
        pattern=r"(?i)(?P<monitor_cmd>^/(?:监视|sj)(?:\s+help)?\s*$)",
        aliases=["/监视", "/sj"],
    )
    async def handle_screenshot(
        self,
        stream_id: str = "",
        platform: str = "",
        user_id: str = "",
        matched_groups: dict | None = None,
        **kwargs: Any,
    ) -> tuple[bool, str, int]:
        del kwargs

        if not self.config.permission.allow_all:
            allowed_ids = self.config.permission.allowed_user_ids
            if allowed_ids and user_id not in allowed_ids:
                msg = "你没有权限使用此命令"
                if stream_id:
                    await self.ctx.send.text(msg, stream_id)
                return False, msg, 0

        raw = (matched_groups or {}).get("monitor_cmd", "").strip()
        parts = raw.split() if raw else []
        if len(parts) >= 2 and parts[1].lower() == "help":
            if stream_id:
                await self.ctx.send.text(HELP_TEXT, stream_id)
            return True, HELP_TEXT, 2

        if not stream_id:
            return False, "stream_id 为空", 0

        try:
            screenshot = ImageGrab.grab(all_screens=True)

            blur_radius = self.config.blur.radius
            blurred = screenshot.filter(ImageFilter.GaussianBlur(radius=blur_radius))

            buf = io.BytesIO()
            blurred.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")

            await self.ctx.send.image(b64, stream_id)
            return True, "屏幕截图已发送", 2

        except Exception as e:
            err_msg = f"截图失败: {e}"
            self.ctx.logger.error(err_msg)
            if stream_id:
                await self.ctx.send.text(err_msg, stream_id)
            return False, err_msg, 0


def create_plugin() -> MonitorPlugin:
    return MonitorPlugin()
