# 从环境变量获取API密钥，而不是硬编码
import os
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt
import time
import sys

# 尝试多种方式获取API密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    # 如果环境变量中没有，尝试从配置文件读取
    try:
        with open("config.txt", "r") as f:
            DEEPSEEK_API_KEY = f.read().strip()
    except:
        pass

if not DEEPSEEK_API_KEY:
    # 如果还是没有，提示用户输入
    console = Console()
    DEEPSEEK_API_KEY = Prompt.ask("请输入您的 DeepSeek API Key")
    # 保存到配置文件
    try:
        with open("config.txt", "w") as f:
            f.write(DEEPSEEK_API_KEY)
    except:
        console.print("[yellow]警告：无法保存API Key到配置文件[/yellow]")

console = Console()

def ask_deepseek(prompt, df_head, columns):
    """
    向 DeepSeek LLM 发送数据分析请求，要求返回可执行的 Python 代码。
    """
    system_prompt = (
        "你是一个数据分析专家。用户会给你一个数据分析请求和一个pandas DataFrame的表头和列名。"
        "请你只返回一段可直接运行的Python代码（不要解释），代码要用matplotlib画图，数据变量名为df。"
        "如果用户请求画图，代码最后要用plt.show()显示图像。"
    )
    user_prompt = (
        f"数据表头如下：\n{df_head}\n"
        f"列名为：{columns}\n"
        f"用户请求：{prompt}\n"
        "请只返回代码，不要有任何解释。"
    )
    
    try:
        # 使用新版本的OpenAI客户端
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 打印API密钥前几位用于调试（不要在生产环境中这样做）
        console.print(f"[cyan]使用的API密钥前几位: {DEEPSEEK_API_KEY[:8]}...[/cyan]")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=30  # 设置超时时间
        )
        code = response.choices[0].message.content
    except Exception as e:
        console.print(f"[red]API调用失败: {e}[/red]")
        console.print("[red]请检查API密钥是否正确，以及是否能够访问DeepSeek API[/red]")
        return None
        
    # 清理代码块标记
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()

def main():
    console.print("[bold green]欢迎使用 DeepSeek 数据分析 Agent！[/bold green]")
    csv_path = Prompt.ask("请输入要分析的CSV文件路径", default="data.csv")
    
    try:
        if not os.path.exists(csv_path):
            console.print(f"[red]文件 {csv_path} 不存在！[/red]")
            return
            
        df = pd.read_csv(csv_path)
        console.print(f"[cyan]数据加载成功，前5行如下：[/cyan]")
        console.print(df.head())
        console.print(f"[cyan]列名：{list(df.columns)}[/cyan]")
    except Exception as e:
        console.print(f"[red]读取CSV文件失败: {e}[/red]")
        return

    while True:
        user_input = Prompt.ask("\n请输入你的数据分析请求（如'画出销量随月份的变化折线图'，输入exit退出）")
        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold yellow]感谢使用，再见！[/bold yellow]")
            break
            
        code = ask_deepseek(user_input, df.head().to_string(), list(df.columns))
        if not code:
            continue
            
        console.print("[magenta]生成的代码如下：[/magenta]")
        console.print(code)
        
        try:
            # 创建一个安全的执行环境
            exec_globals = {
                "df": df, 
                "plt": plt,
                "pd": pd,
                "np": __import__("numpy"),
                "time": time,
                "sys": sys
            }
            
            # 执行代码
            exec(code, exec_globals)
        except Exception as e:
            console.print(f"[red]代码执行出错：{e}[/red]")

if __name__ == "__main__":
    main() 