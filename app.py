import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2
import pandas as pd
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load env for local dev
load_dotenv()

# Get Supabase (PostgreSQL) credentials
host = os.getenv("SUPABASE_HOST") or st.secrets.get("SUPABASE_HOST")
port = os.getenv("SUPABASE_PORT") or st.secrets.get("SUPABASE_PORT")
user = os.getenv("SUPABASE_USER") or st.secrets.get("SUPABASE_USER")
password = quote_plus(os.getenv("SUPABASE_PASSWORD") or st.secrets.get("SUPABASE_PASSWORD", ""))
database = os.getenv("SUPABASE_DB") or st.secrets.get("SUPABASE_DB")

# Get Google API key
google_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

# PostgreSQL connection URI
postgres_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{int(port or 5432)}/{database}"

# Connect to database
db = SQLDatabase.from_uri(postgres_uri, sample_rows_in_table_info=1)

def get_schema(db):
    return db.get_table_info()

def execute_sql_query(sql_query):
    try:
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=user,
            password=os.getenv("SUPABASE_PASSWORD") or st.secrets.get("SUPABASE_PASSWORD"),
            database=database
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

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=google_api_key)

sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: get_schema(db))
    | sql_prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)

nl_chain = (
    RunnablePassthrough()
    | nl_prompt
    | llm
    | StrOutputParser()
)

st.title("Text-to-SQL with Natural Language Response (Gemini 2.5 Pro)")

question = st.text_input("Enter your natural language query:")

if st.button("Submit"):
    if question:
        sql_query = sql_chain.invoke({"question": question}).strip()

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
