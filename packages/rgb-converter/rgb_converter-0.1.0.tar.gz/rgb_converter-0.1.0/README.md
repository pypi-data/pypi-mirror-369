# RGB-Converter

RGB颜色转换器 - FastMCP示例项目。

## 功能

- 颜色转换工具：将颜色名称或16进制颜色码转换为RGB格式
- 问候语资源：根据提供的名称生成问候语
- 问候语提示词模板：根据名字和风格生成问候语提示词

## 安装

```bash
pip install rgb-converter
```

## 使用方法

```python
from rgb_converter import mcp

# 启动MCP服务器
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 许可证

MIT