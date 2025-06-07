import os
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

def test_api_connection():
    """测试DeepSeek API连接"""
    console.print(Panel.fit("DeepSeek API 连接测试", style="bold blue"))
    
    # 获取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        try:
            with open("config.txt", "r") as f:
                api_key = f.read().strip()
        except:
            console.print("[red]错误：无法从config.txt读取API密钥[/red]")
            return False
    
    if not api_key:
        console.print("[red]错误：未找到API密钥[/red]")
        return False
    
    console.print(f"[cyan]使用的API密钥前几位: {api_key[:8]}...[/cyan]")
    
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 测试API连接
        console.print("[yellow]正在测试API连接...[/yellow]")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'API连接测试成功'"}
            ],
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 检查响应
        if response.choices[0].message.content:
            console.print("[green]✓ API连接测试成功！[/green]")
            console.print(f"[cyan]响应时间: {response_time:.2f}ms[/cyan]")
            console.print(f"[cyan]模型响应: {response.choices[0].message.content}[/cyan]")
            return True
        else:
            console.print("[red]✗ API响应为空[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ API连接测试失败: {str(e)}[/red]")
        return False

def main():
    console.print("\n[bold]DeepSeek API 测试工具[/bold]")
    console.print("=" * 50)
    
    # 测试网络连接
    console.print("\n[cyan]1. 测试网络连接...[/cyan]")
    try:
        import requests
        response = requests.get("https://api.deepseek.com/v1", timeout=5)
        console.print("[green]✓ 可以访问DeepSeek API服务器[/green]")
    except Exception as e:
        console.print(f"[red]✗ 无法访问DeepSeek API服务器: {str(e)}[/red]")
        console.print("[yellow]提示：请检查网络连接或代理设置[/yellow]")
        return
    
    # 测试API连接
    console.print("\n[cyan]2. 测试API认证...[/cyan]")
    if test_api_connection():
        console.print("\n[green]所有测试通过！[/green]")
    else:
        console.print("\n[red]测试失败，请检查API密钥和网络设置[/red]")

if __name__ == "__main__":
    main() 