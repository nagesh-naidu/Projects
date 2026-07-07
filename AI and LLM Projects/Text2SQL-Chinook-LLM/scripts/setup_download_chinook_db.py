# %%
%%capture --no-stderr
%pip install --upgrade --quiet langchain-community langgraph

# %%
import requests
import sqlite3

# Step 1: Download the SQL file
url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
sql_script = requests.get(url).text

# Step 2: Create the database
conn = sqlite3.connect("Chinook.db")
cursor = conn.cursor()
cursor.executescript(sql_script)
conn.commit()
conn.close()

# %%
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("Chinook.db")

# Step 1: Get all table names
tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql_query(tables_query, conn)['name'].tolist()

# Step 2: Loop through tables and display first 3 rows
for table in tables:
    print(f"\n📌 Table: {table}")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 3;", conn)
        display(df)  # Only works in Jupyter
    except Exception as e:
        print(f"❌ Error reading table {table}: {e}")

conn.close()


# %%
#import sys
#sys.path.append("scripts")

import sys
sys.path.append("../scripts")  # relative path from notebook to scripts folder

#db_path = r"C:\Users\NageshN\Documents\Documents 2\Documents\Unilever Project - Procurement Analytics\Proc GPT KT\FC GPT\Demo\data\Chinook.db"
#output_path = r"C:\Users\NageshN\Documents\Documents 2\Documents\Unilever Project - Procurement Analytics\Proc GPT KT\FC GPT\Demo\data\Chinook.dbml"

from sqlite_to_dbml import sqlite_to_dbml

db_path = "../data/Chinook.db"
output_path = "../data/Chinook.dbml"


# Execute
sqlite_to_dbml(db_path, output_path)

# %%
# Add scripts folder to Python path
import sys
sys.path.append("../scripts")

# Import the module
import export_chinook_excel

# Reload the module to pick up any changes
import importlib
importlib.reload(export_chinook_excel)

# Execute the function to export all Chinook tables to Excel
export_chinook_excel.export_all_tables()



# %%
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

# %%
pip install -qU "langchain[google-genai]"

# %% [markdown]
# Requesting the User to Input the API Key

# %%
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# %% [markdown]
# Prompt Template Creation and System Messages
# 

# %%
from langchain_core.prompts import ChatPromptTemplate

"""system_message = 
Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question.

Only use the exact table and column names as provided in {table_info}.
Do not make up table or column names.
Also,
pay attention to which column is in which table.

Only use the following tables:
{table_info}
"""


system_message = """
You are an expert SQL generator.

Given an input question, generate a syntactically correct {dialect} SQL query to answer the question.

ONLY use the table and column names exactly as provided in the schema below.

Do not rename or modify any table or column names. Do not guess. Do not use plural or singular variations. Do not add aliases unless explicitly required by the question.
If a table is named `Employee`, DO NOT use `Employees`.
If a table is named `OrderDetails`, DO NOT use `OrderDetail`.
Always use the table and column names EXACTLY as shown below. No corrections. No guesses.

Never query for all columns (no SELECT *). Select only the relevant columns based on the question.

Unless the question asks for more, limit your results to at most {top_k} rows. You can sort the results using a relevant column if appropriate.




### Database schema:
{table_info}

### Example format:
```sql
SELECT column1, column2 FROM table_name WHERE ... LIMIT {top_k};

"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate(
    [("system", system_message), ("user", user_prompt)]
)

for message in query_prompt_template.messages:
    message.pretty_print()

# %%
## Notes for self learning

'''system_message = "A very long message giving specific instructions to the model, can include database schema details"
user_prompt = "Question: {Input}"

query_prompt_template = ChatPromptTemplate ([
    ("system", system_message),('user', user_prompt)
])'''

# %%
query_prompt_template.messages

# %%
for message in query_prompt_template.messages:
    print(message.input_variables)

# %% [markdown]
# Query Generation with a user input

# %%
from typing_extensions import Annotated


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]

def write_query(state: State) -> State:
    
    """Generate SQL query to fetch information."""

    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)

    return {
        **state,
        "query": result["query"]
    }


# %%
blank_state = {
    "question": "",
    "query": "",
    "result": "",
    "answer": ""
}
blank_state["question"] = "How many Employees are there?"

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
blank_state = write_query(blank_state)
print(blank_state)


# %% [markdown]
# Query Execution Function using a Langchain Tool

# %%
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

def execute_query(state: State) -> State:
    """Execute SQL query and return updated state with result."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    
    result = execute_query_tool.invoke(state["query"])

    return {
        **state,           # Keep all existing keys (question, query, answer)
        "result": result   # Add/update the result key
    }


# %%
blank_state = execute_query(blank_state)
print(blank_state)

# %% [markdown]
# Generating an Answer

# %%
def generate_answer(state: State) -> State:
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f"Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['result']}"
    )
    response = llm.invoke(prompt)

    return {
        **state,                      # preserve all previous fields
        "answer": response.content   # add new field
    }


# %%
blank_state = generate_answer(blank_state)
print(blank_state)

# %%
from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

# %%
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))

# %%
for step in graph.stream(
    {"question": "How many employees are there?"}, stream_mode="updates"
):
    print(step)

# %%
result = graph.invoke({"question": "How many employees are there?"})

print(result)

# %%
result['answer']

# %%
result_2 = graph.invoke({"question": "How many customers are there?"})

print(result_2)

# %% [markdown]
# Executing the same with an Agentic Architecture

# %%
## Step 1 - Importing the SQL toolkit which contains different SQL tools


from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

tools

# %% [markdown]
# Creating a system message for the agent

# %%
system_message_agent = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect="SQLite",
    top_k=5,
)

# %% [markdown]
# Initializing the Agent

# %%
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, tools, prompt=system_message_agent)

# %% [markdown]
# Executing the Agent as well as tracing the intermediate steps for understanding

# %%
question = "Which country's customers spent the most?"

for step in agent_executor.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

# %% [markdown]
# Agent Execution without the displaying intermediate steps and only the final output

# %%
# User's natural language question
question = "Which country's customers spent the most?"

# Invoke agent and get final result (no intermediate steps)
result = agent_executor.invoke({
    "messages": [{"role": "user", "content": question}]
})

# Extract and print only the final message
print("Final Answer:", result["messages"][-1].content)


# %%



