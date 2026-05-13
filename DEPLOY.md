# Render 部署指南

## 前置条件

1. 代码已推送到 **GitHub 公开仓库**
2. 注册 [Render](https://render.com) 账号（用 GitHub 登录，免费）

## 部署步骤

1. Render 控制台点 **New + → Web Service**
2. 关联你的 GitHub 仓库
3. 填写配置：

| 字段 | 值 |
|---|---|
| Name | `gamepulse` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python server.py` |
| Instance Type | **Free** |

4. 点 **Deploy Web Service**，等待 2-3 分钟
5. 部署完成后访问 `https://gamepulse.onrender.com`
6. 把链接发给同事，大家一起用

## 注意事项

- **首次访问慢**：免费实例 15 分钟无请求会自动休眠，首次唤醒约 30 秒。再次访问时瞬间响应。
- **数据备份**：部署新版本前先点右上角导出 JSON，因为重新部署会重置磁盘。
- **后续迁移**：SQLite 数据库文件可直接下载，迁移到国内服务器时导入即可。

## 本地开发

```bash
pip install flask
python server.py
# 打开 http://localhost:5000
```
