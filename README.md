# DeepSeek 数据分析 Agent

这是一个基于 DeepSeek LLM 的数据分析工具，可以通过自然语言指令分析 CSV 数据并生成可视化图表。

## 功能特点

- 支持命令行和 Web 界面两种使用方式
- 通过自然语言指令分析数据
- 自动生成并执行 Python 代码
- 使用 matplotlib 生成数据可视化图表

## 安装依赖

```bash
pip install pandas matplotlib openai streamlit rich
```

## 使用方法

### 设置 API 密钥

在使用前，请设置 DeepSeek API 密钥：

```bash
# Linux/macOS
export DEEPSEEK_API_KEY="your-api-key-here"

# Windows
set DEEPSEEK_API_KEY=your-api-key-here
```

### 命令行版本

运行以下命令启动命令行版本：

```bash
python deepseek_data_agent.py
```

按照提示输入 CSV 文件路径和分析请求。

### Web 版本

运行以下命令启动 Web 版本：

```bash
streamlit run deepseek_data_agent_web.py
```

在浏览器中打开显示的地址，上传 CSV 文件并输入分析请求。

## 示例分析请求

- "画出销量随月份的变化折线图"
- "计算每个类别的平均价格并绘制柱状图"
- "分析销售额与广告支出的相关性并绘制散点图"
- "按地区分组计算总销售额并绘制饼图"

## 安全注意事项

- 请勿在代码中硬编码 API 密钥
- 使用环境变量或配置文件存储敏感信息
- 注意保护您的数据安全

## 许可证

MIT 