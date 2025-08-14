# MCP feet Master 🐰🐔

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/mcp-feet-master.svg)](https://badge.fury.io/py/mcp-feet-master)

一個專門計算動物腳數的 Model Context Protocol (MCP) 伺服器。解決經典的「兔子和雞」數學問題，讓 AI 模型能夠準確計算農場動物的總腳數。

## ✨ 功能特色

- 🧮 **精確計算**：計算兔子（4腳）和雞（2腳）的總腳數
- 🔄 **反推功能**：根據總腳數推算可能的動物組合
- 📚 **範例資源**：內建計算範例和使用說明
- 📝 **提示模板**：生成標準化的數學問題
- 🔧 **FastMCP**：基於 FastMCP 框架，易於整合

## 🚀 安裝

### 使用 pip 安裝

```bash
pip install mcp-feet-master
```

### 從源碼安裝

```bash
git clone https://github.com/yourusername/mcp-feet-master.git
cd mcp-feet-master
pip install -e .
```

## 📖 使用方法

### 作為 MCP 伺服器運行

```bash
mcp-feet-master
```

或者在 Python 中：

```python
from mcp_feet_master import create_server

server = create_server()
server.run()
```

### 與 Claude Desktop 整合

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "mcp-feet-master": {
      "command": "mcp-feet-master",
      "args": []
    }
  }
}
```

## 🛠️ 可用工具

### 1. `get_foot_num(rabbits, chickens)`

計算兔子和雞的總腳數。

**參數：**
- `rabbits` (int): 兔子數量
- `chickens` (int): 雞的數量

**返回：**
```python
{
    "total_feet": 22,
    "rabbit_feet": 12,
    "chicken_feet": 10,
    "rabbits": 3,
    "chickens": 5,
    "calculation": "3 隻兔子 × 4 腳 + 5 隻雞 × 2 腳 = 22 隻腳",
    "formula": "3 × 4 + 5 × 2 = 22"
}
```

### 2. `calculate_animals_from_feet(total_feet, animal_type)`

根據總腳數反推動物組合。

**參數：**
- `total_feet` (int): 總腳數
- `animal_type` (str): `"rabbits"`, `"chickens"`, 或 `"mixed"`

**範例：**
```python
# 混合動物組合
{
    "total_feet": 20,
    "possible_combinations": [
        {"rabbits": 5, "chickens": 0, "verification": 20},
        {"rabbits": 3, "chickens": 4, "verification": 20},
        {"rabbits": 1, "chickens": 8, "verification": 20},
        {"rabbits": 0, "chickens": 10, "verification": 20}
    ],
    "count": 4
}
```

## 📚 可用資源

### `feet://examples`

獲取使用範例和計算說明。

## 📝 可用提示

### `animal_feet_problem`

生成標準化的動物腳數數學問題。

**參數：**
- `rabbits` (int): 兔子數量
- `chickens` (int): 雞的數量  
- `include_explanation` (bool): 是否包含解釋（預設：true）

## 💡 使用範例

### 與 AI 模型對話範例

**用戶：** "農場裡有 3 隻兔子和 5 隻雞，總共有多少隻腳？"

**AI 模型使用 MCP：** 
```
調用 get_foot_num(3, 5)
結果：22 隻腳 (3 × 4 + 5 × 2 = 12 + 10 = 22)
```

**用戶：** "如果總共有 20 隻腳，可能的動物組合有哪些？"

**AI 模型使用 MCP：**
```
調用 calculate_animals_from_feet(20, "mixed")
可能組合：
- 5 隻兔子 + 0 隻雞
- 3 隻兔子 + 4 隻雞  
- 1 隻兔子 + 8 隻雞
- 0 隻兔子 + 10 隻雞
```

## 🧪 開發

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 運行測試

```bash
pytest tests/
```

### 程式碼格式化

```bash
black src/ tests/
isort src/ tests/
```

### 型別檢查

```bash
mypy src/
```

## 📈 版本歷史

- **0.1.0**: 初始版本
  - 基本的兔子雞腳數計算功能
  - 反推動物組合功能
  - FastMCP 整合

## 🤝 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳細說明。

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案使用 MIT 授權。詳見 [LICENSE](LICENSE) 文件。

## 🔗 相關連結

- [Model Context Protocol 官方文檔](https://modelcontextprotocol.io/)
- [FastMCP 文檔](https://github.com/modelcontextprotocol/python-sdk)
- [專案首頁](https://github.com/yourusername/mcp-feet-master)

## 📞 支援

如果遇到問題或有建議，請：
- 開啟 [GitHub Issue](https://github.com/yourusername/mcp-feet-master/issues)
- 查看 [文檔](https://github.com/yourusername/mcp-feet-master/wiki)

---

**讓 AI 計算動物腳數變得簡單又準確！** 🎯