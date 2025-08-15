# 加法 MCP 服务

这是一个简单的 Model Context Protocol (MCP) 服务示例，提供基本的加法计算功能和问候语生成功能。

## 功能介绍

本服务提供以下功能：

1. **加法计算工具**：计算两个整数的和
2. **问候语资源**：根据提供的名称生成个性化问候语
3. **问候语提示词模板**：根据不同风格生成问候语提示词

## 安装与配置

### 前提条件

- Python 3.6 或更高版本
- MCP 库

### 配置步骤

1. 将服务配置添加到 CodeBuddy 的 MCP 设置文件中：
   ```json
   "加法服务": {
     "disabled": false,
     "timeout": 60,
     "type": "stdio",
     "command": "python",
     "args": [
       "d:/mcp_ts/main.py"
     ]
   }
   ```

2. 配置文件位置：`c:\Users\93467\AppData\Roaming\CodeBuddy\User\globalStorage\tencent.planning-genie\settings\codebuddy_mcp_settings.json`

## 使用方法

### 启动服务

```bash
python d:/mcp_ts/main.py
```

### 使用加法工具

通过 CodeBuddy 调用加法工具：

```
<use_mcp_tool>
<server_name>加法服务</server_name>
<tool_name>add</tool_name>
<arguments>
{
  "a": 5,
  "b": 3
}
</arguments>
</use_mcp_tool>
```

### 访问问候语资源

```
<access_mcp_resource>
<server_name>加法服务</server_name>
<uri>greeting://World</uri>
</access_mcp_resource>
```

## 代码结构

- `main.py`: 主程序文件，包含 MCP 服务的所有功能实现

## 扩展开发

您可以通过以下方式扩展此服务：

1. 添加更多数学运算工具（如减法、乘法、除法等）
2. 增加更多资源类型
3. 开发更复杂的提示词模板

## 许可证

MIT
