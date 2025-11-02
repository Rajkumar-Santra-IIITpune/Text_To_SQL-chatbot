# Text-to-SQL with Natural Language Response

A Streamlit application that converts natural language queries into SQL queries using Google's Gemini 2.5 Pro model, executes them on a PostgreSQL database, and provides natural language responses.

## Features

- **Natural Language to SQL**: Convert plain English questions into SQL queries using AI.
- **Database Integration**: Connects to PostgreSQL database for query execution.
- **Natural Language Responses**: Provides human-readable answers based on query results.
- **Streamlit UI**: Simple web interface for interaction.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Generative AI API key

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/text-to-sql.git
   cd text-to-sql
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` (if provided) or create a `.env` file with the following variables:
     ```
     POSTGRES_HOST=localhost
     POSTGRES_PORT=5432
     POSTGRES_USERNAME=your_postgres_username
     POSTGRES_PASSWORD=your_postgres_password
     POSTGRES_DATABASE=your_database_name
     GOOGLE_API_KEY=your_google_api_key
     ```

## Usage

1. Ensure your PostgreSQL database is running and accessible.

2. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

3. Open your browser to the provided URL (usually `http://localhost:8501`).

4. Enter your natural language query in the text input field and click "Submit".

## Example Queries

- "Show me all users"
- "What is the total number of orders?"
- "List products with price greater than 100"
- "Who are the top 5 customers by purchase amount?"

## Project Structure

```
text_to_sql/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Dependencies

- streamlit: Web app framework
- langchain: LLM framework for chaining prompts
- langchain-google-genai: Google Generative AI integration
- langchain-core: Core LangChain components
- psycopg2-binary: PostgreSQL adapter
- pandas: Data manipulation
- python-dotenv: Environment variable management

## Configuration

The application uses the following environment variables:

- `POSTGRES_HOST`: PostgreSQL server host
- `POSTGRES_PORT`: PostgreSQL server port
- `POSTGRES_USERNAME`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DATABASE`: PostgreSQL database name
- `GOOGLE_API_KEY`: Google Generative AI API key

## How It Works

1. **Schema Retrieval**: The app connects to the PostgreSQL database and retrieves table schemas.
2. **Query Generation**: User input is processed by Gemini 2.5 Pro to generate SQL queries based on the schema.
3. **Query Execution**: Generated SQL is executed on the database.
4. **Response Generation**: Results are fed back to Gemini for natural language explanation.

## Security Notes

- Never commit `.env` files containing sensitive information.
- Use strong passwords for database access.
- Consider using environment-specific configuration for production deployments.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
