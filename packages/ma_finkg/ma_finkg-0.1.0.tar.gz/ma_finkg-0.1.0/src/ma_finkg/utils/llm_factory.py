import os
from langchain_openai import ChatOpenAI
import dspy


def create_openrouter_llm(model_name: str = "openai/gpt-3.5-turbo") -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for OpenRouter with standard settings."""
    return ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        request_timeout=30
    )


def create_dspy_llm(model_name: str = "openai/gpt-3.5-turbo") -> dspy.LM:
    """Create a DSPy-compatible LM instance for DSPy agents."""
    dspy_llm = dspy.LM(
        model=model_name,
        api_base="https://openrouter.ai/api/v1", 
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
        max_tokens=1000
    )
    
    dspy.settings.configure(lm=dspy_llm)
    
    return dspy_llm