# 从环境变量获取API密钥，而不是硬编码
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from openai import OpenAI
import time
import sys

st.set_page_config(page_title="DeepSeek 数据分析 Agent", layout="wide")

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
    # 如果还是没有，使用Streamlit的输入框
    DEEPSEEK_API_KEY = st.text_input("请输入您的 DeepSeek API Key", type="password")
    if DEEPSEEK_API_KEY:
        # 保存到配置文件
        try:
            with open("config.txt", "w") as f:
                f.write(DEEPSEEK_API_KEY)
        except:
            st.warning("无法保存API Key到配置文件")
    else:
        st.error("请先输入API Key")
        st.stop()

st.title("🤖 DeepSeek 数据分析 Agent")
st.write("上传你的 CSV 文件，输入分析请求，Agent 会自动生成并执行代码并画图。")

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("数据预览")
        st.dataframe(df.head())
        st.write("列名：", list(df.columns))

        user_input = st.text_input('请输入你的数据分析请求（如"画出销量随月份的变化折线图"）')
        if st.button("分析并画图") and user_input:
            with st.spinner("正在调用 DeepSeek LLM 生成代码..."):
                system_prompt = (
                    "你是一个数据分析专家。用户会给你一个数据分析请求和一个pandas DataFrame的表头和列名。"
                    "请你只返回一段可直接运行的Python代码（不要解释），代码要用matplotlib画图，数据变量名为df。"
                    "如果用户请求画图，代码最后要用plt.show()显示图像。"
                )
                user_prompt = (
                    f"数据表头如下：\n{df.head().to_string()}\n"
                    f"列名为：{list(df.columns)}\n"
                    f"用户请求：{user_input}\n"
                    "请只返回代码，不要有任何解释。"
                )
                
                try:
                    # 使用新版本的OpenAI客户端
                    client = OpenAI(
                        api_key=DEEPSEEK_API_KEY,
                        base_url="https://api.deepseek.com/v1"
                    )
                    
                    # 打印API密钥前几位用于调试（不要在生产环境中这样做）
                    st.write(f"使用的API密钥前几位: {DEEPSEEK_API_KEY[:8]}...")
                    
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
                    st.error(f"API调用失败: {e}")
                    st.error("请检查API密钥是否正确，以及是否能够访问DeepSeek API")
                    st.stop()
                
                # 清理代码块标记
                if code.startswith("```python"):
                    code = code[9:]
                if code.startswith("```"):
                    code = code[3:]
                if code.endswith("```"):
                    code = code[:-3]
                code = code.strip()
                st.code(code, language="python")
                
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
                fig, ax = plt.subplots()
                exec_globals.update({"fig": fig, "ax": ax})
                exec(code, exec_globals)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"代码执行出错：{e}")
    except Exception as e:
        st.error(f"处理CSV文件时出错: {e}")
else:
    st.info("请先上传 CSV 文件。") 