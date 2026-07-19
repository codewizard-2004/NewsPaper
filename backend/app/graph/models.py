import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

def get_llm(desk_name: str) -> BaseChatModel:
    """
    Factory function to return the correct LLM based on the assigned Desk.
    Provides a 7-model diverse ecosystem.
    """
    # 1. Chief Editor (Reasoning / Routing)
    if desk_name == "chief_editor":
        return ChatGoogleGenerativeAI(
            model="models/gemini-3.5-flash",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    # 2. Front Desk (Fast fetching / aggregation)
    elif desk_name == "front_desk":
        return ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
    # 3. AI & ML Desk (Precision / Nuance)
    elif desk_name == "ai_ml_desk":
        return ChatOpenAI(
            model="gpt-5.4-nano",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
    # 4. Economics Desk (Complex analysis - OpenRouter Nemotron)
    elif desk_name == "economics_desk":
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            temperature=0.4
        )
        
    # 5. Weather & Puzzles Desk (Creativity / Logic)
    elif desk_name == "weather_puzzles_desk":
        return ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    # 6. Classifieds Desk (Structured output - OpenRouter Llama3)
    elif desk_name == "classifieds_desk":
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="meta-llama/llama-3-8b-instruct:free",
            temperature=0.3
        )
        
    # 7. Obituaries & Births Desk (Opinion / Satire)
    elif desk_name == "obituaries_births_desk":
        # Assumes Ollama is running locally or via a custom hosted URL
        return ChatOllama(
            model="minimax-m3:cloud",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.8
        )

    # 8. Sports Desk (Tech competition / play-by-play)
    elif desk_name == "sports_desk":
        return ChatGroq(
            model="qwen/qwen3.6-27b",
            temperature=0.6,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    # Fallback
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.5,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
