"""
Function Calling Agent 效果验证脚本
用法: python test_function_calling.py
"""
import sys
from dotenv import load_dotenv

load_dotenv()

from app.services.agent_service import agent_service

def run_case(question: str):
    print("=" * 60)
    print(f"❓ 问题: {question}")
    print("=" * 60)
    result = agent_service.run(question)
    print(f"\n✅ 最终回答: {result.get('answer', '')}")
    print(f"工具调用次数: {result.get('tool_calls', 0)}")
    for i, step in enumerate(result.get("intermediate_steps", []), 1):
        print(f"  [{i}] {step['tool']}({step['arguments']})")
    print()

if __name__ == "__main__":
    # 用例1: 无参数工具 + 带参数工具组合
    run_case("现在几点了？顺便帮我算一下 (123 * 456) + 789")

    # 用例2: 需要知识库检索（依赖 Milvus 运行）
    if len(sys.argv) > 1 and sys.argv[1] == "--kb":
        run_case("知识库里有哪些文档？")
