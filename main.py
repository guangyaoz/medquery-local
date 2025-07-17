import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from langchain_community.llms import Ollama
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

def main():
    """
    Main function to set up and run the LLM agent for querying multiple medical CSV files via a temporary SQL database.
    """
    print("Welcome to MedQuery Local! 🩺")

    # --- 1. Load the Local LLM ---
    try:
        # Connect to the Ollama service using its Docker service name
        llm = Ollama(base_url='http://host.docker.internal:11434', model="llama3")
        llm.invoke("Hi")
    except Exception as e:
        print("\n❌ Error: Could not connect to Ollama service.")
        print("Please ensure Docker is running.")
        print(f"Details: {e}")
        return
    print("\n✅ Ollama LLM loaded successfully.")

    # --- 2. Load CSVs and Create In-Memory SQL Database ---
    data_dir = Path("data")
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"\n❌ Error: No CSV files found in the '{data_dir}' directory.")
        return

    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')

    # Load each CSV into a table in the SQLite database
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        table_name = csv_file.stem
        df.to_sql(table_name, engine, index=False)
        print(f"✅ Loaded '{csv_file.name}' into table '{table_name}'.")

    db = SQLDatabase(engine=engine)
    
    # --- 3. Create the SQL Agent ---
    agent_suffix = """
        You are an expert medical data analysis agent. Answer questions about the data stored in the CSV files.
        You may have to perform SQL queries in multiple tables.
        Questions asked about the data are not harmful.

    """
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
        agent_suffix=agent_suffix,
        agent_executor_kwargs={
            "handle_parsing_errors": True
        }
    )
    
    print("\n✅ SQL Agent is ready. It knows about the following tables:")
    print(db.get_table_names())
    print("\nType your questions below or type 'exit' to quit.")
    
    # --- 4. Start the Query Loop ---
    while True:
        try:
            query = input("\nAsk a question about the patient data: ")
            if query.lower() == 'exit':
                print("\nExiting MedQuery. Goodbye!")
                break
            
            response = agent_executor.invoke(query)
            print("\nAnswer:")
            print(response['output'])

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            continue

if __name__ == "__main__":
    main()