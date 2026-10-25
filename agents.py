import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from the project directory or current working directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url

# Verify GROQ_API_KEY is configured
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")

# Model setup with configurable GROQ_MODEL environment variable
DEFAULT_MODEL = "openai/gpt-oss-20b"
GROQ_MODEL = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

def get_model(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance using the configured model ID."""
    model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    return ChatGroq(
        model=model_name,
        temperature=temperature
    )

llm = get_model(temperature=0)


#1st agent 
def build_search_agent():
    return create_agent(
        model = get_model(temperature=0),
        tools= [web_search]
    )

#2nd agent 

def build_reader_agent():
    return create_agent(
        model = get_model(temperature=0),
        tools = [scrape_url]
    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()

