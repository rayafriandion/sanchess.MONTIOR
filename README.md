# MONITOR

你想在离你已经部署并启动了 Maibot 的 Windows 电脑很远的地方快速查看图形情况吗？
你想让其他群友视奸你正在做什么吗？
用于 Maibot 的 MONITOR 插件现已来临……

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
