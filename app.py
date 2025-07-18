import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate


# --- Configuration ---
# All the model downloader and GGUF path code is now gone!
# We just need to tell LangChain how to connect to the Ollama service.
# The hostname 'ollama' works because both services are in the same docker-compose network.
OLLAMA_BASE_URL = "http://host.docker.internal:11434"

# --- NEW: Simplified LLM Loader ---
@st.cache_resource
def load_llm():
    """Initializes the Ollama LLM client."""
    return OllamaLLM(
        model="llama3", # Tell Ollama which model to use
        base_url=OLLAMA_BASE_URL
    )
# --- NEW: A more detailed prompt template for the agent ---
CUSTOM_PROMPT_TEMPLATE = """
You are a powerful AI data analyst agent working with a SQLite database.
Your goal is to answer the user's question by generating and executing SQL queries.

**TOOLS:**
You have access to the following tools to help you:
{tools}

**Instructions:**
1.  Carefully analyze the user's question.
2.  Examine the database schema provided, paying close attention to the column descriptions to understand the meaning of each column.
3.  When a user asks "how many", "what is the total", or for an "average", use an appropriate SQL aggregation function like COUNT(*), SUM(), or AVG() to provide a single, calculated number as the answer.
4.  To use a tool, you must call one of [{tool_names}].
5.  After receiving the tool's output, proceed with your analysis to formulate the final answer.

**Database Schema with Descriptions:**
{table_info}

**User Question:**
{input}

**Your Thought Process and Actions:**
{agent_scratchpad}
"""
def get_schema_with_descriptions(engine):
    inspector = inspect(engine)
    schema_info = ""
    tables = inspector.get_table_names()
    for table_name in tables:
        schema_info += f"Table '{table_name}' has the following columns:\n"
        columns = inspector.get_columns(table_name)
        for column in columns:
            # You can add your own descriptions here based on the column name
            description = f" (Represents {column['name'].replace('_', ' ')})"
            schema_info += f"- {column['name']} (type: {column['type']}){description}\n"
    return schema_info

@st.cache_resource
def get_agent(_engine):
    """Creates the SQL agent."""
    
    db = SQLDatabase(engine=_engine)
    # Generate the custom schema string
    custom_table_info = get_schema_with_descriptions(_engine)

    # Create the prompt with our custom template and schema info
    prompt = PromptTemplate.from_template(CUSTOM_PROMPT_TEMPLATE).partial(table_info=custom_table_info)

    llm=load_llm()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=30,
        max_execution_time=None,
        #prompt=prompt,
        agent_executor_kwargs={
            "handle_parsing_errors": True
        },
    )

# --- Streamlit UI ---
st.set_page_config(page_title="MedQuery Agent 🩺", layout="wide")
st.title("MedQuery Agent: Ask Questions About Your EHR Data")

# Session state initialization
if 'engine' not in st.session_state:
    st.session_state.engine = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar for Data Loading ---
with st.sidebar:
    st.header("Setup")
    uploaded_file = st.file_uploader("Upload your EHR CSV file", type="csv")

    if uploaded_file is not None:
        if st.button("Load Data"):
            with st.spinner("Processing Data..."):
                engine = create_engine("sqlite:///ehr_data.db")
                df = pd.read_csv(uploaded_file)
                table_name = df.stem
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
                df.to_sql(table_name, engine, if_exists="replace", index=False)
                st.session_state.engine = engine
                st.session_state.messages = [{"role": "assistant", "content": "Data loaded. How can I help you query it?"}]
                st.success("Data loaded successfully!")
    else:
        st.info("Please upload a CSV file to begin.")

# --- Main Chat Interface ---
# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a question about your data..."):
    if st.session_state.engine is None:
        st.warning("Please upload and load your data using the sidebar first.", icon="⚠️")
    else:
        # Add user message to UI and state
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get the agent and invoke it
        agent_executor = get_agent(st.session_state.engine)
        
        with st.chat_message("assistant"):
            with st.spinner("The agent is thinking..."):
                try:
                    response = agent_executor.invoke({"input": prompt})
                    answer = response.get("output", "I couldn't find an answer.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_message = f"An error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})