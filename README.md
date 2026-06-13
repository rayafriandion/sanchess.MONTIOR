# MONITOR

截取当前活动屏幕并进行高斯模糊处理后发送的 MaiBot 插件，仅支持 Windows 平台。

## 命令

| 命令 | 说明 |
|------|------|
| `/监视` | 截图当前屏幕并模糊发送 |
| `/sj` | 同上 |

## 配置

```toml
[plugin]
enabled = true

[permission]
allow_all = false
allowed_user_ids = []

[blur]
radius = 20
```

## 权限

`allow_all = true` 时放行所有用户；否则仅 `allowed_user_ids` 列表内的用户可用。

## 依赖

- Pillow >= 10.0.0

## 许可

MIT
