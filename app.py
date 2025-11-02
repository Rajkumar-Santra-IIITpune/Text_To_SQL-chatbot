# Importing Libraries
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection details
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USERNAME")
password = quote_plus(os.getenv("POSTGRES_PASSWORD") or "")
database_schema = os.getenv("POSTGRES_DATABASE")

# ✅ Properly formatted PostgreSQL URI
postgres_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{int(port or 5432)}/{database_schema}"

# Connect to PostgreSQL database
db = SQLDatabase.from_uri(postgres_uri, sample_rows_in_table_info=1)

# Get database schema
def get_schema(db):
    return db.get_table_info()

# Execute SQL query and return results
def execute_sql_query(sql_query):
    try:
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=username,
            password=os.getenv("POSTGRES_PASSWORD"),
            database=database_schema
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return pd.DataFrame(results, columns=columns)
    except Exception as e:
        return str(e)

# Prompt templates
sql_template = """Based on the table schema below, write a SQL query that would answer the user's question.
Only output the SQL query — no explanation, no extra text.
Table Schema:
{schema}
Question:
{question}
SQL Query:
"""

nl_template = """Based on the SQL query and its results, provide a natural language answer.
SQL Query:
{sql_query}
Results:
{results}
Question:
{question}
Answer:
"""

sql_prompt = ChatPromptTemplate.from_template(sql_template)
nl_prompt = ChatPromptTemplate.from_template(nl_template)

# Google Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# SQL query generator chain
sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: get_schema(db))
    | sql_prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)

# Natural language response chain
nl_chain = (
    RunnablePassthrough()
    | nl_prompt
    | llm
    | StrOutputParser()
)

# Streamlit UI
st.title("Text-to-SQL with Natural Language Response (Gemini 2.5 Pro)")

question = st.text_input("Enter your natural language query:")

if st.button("Submit"):
    if question:
        sql_query = sql_chain.invoke({"question": question}).strip()

        # Clean LLM output
        for prefix in ["sql", "query", "SQL", "Query", "```sql", "```"]:
            if sql_query.lower().startswith(prefix.lower()):
                sql_query = sql_query[len(prefix):].strip()
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3].strip()

        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")

        results = execute_sql_query(sql_query)
        if isinstance(results, pd.DataFrame):
            st.subheader("Query Results:")
            st.dataframe(results)

            nl_response = nl_chain.invoke({
                "sql_query": sql_query,
                "results": results.to_string(),
                "question": question
            })
            st.subheader("Natural Language Answer:")
            st.write(nl_response)
        else:
            st.error(f"Error executing query: {results}")
    else:
        st.warning("Please enter a question.")
