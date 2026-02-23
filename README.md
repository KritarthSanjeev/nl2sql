# NL2SQL - Natural Language to SQL Query Engine

A Retrieval-Augmented Generation (RAG) system that converts natural language queries into SQL statements using vector embeddings of database schemas. This project combines a PostgreSQL marketplace database with ChromaDB vector storage for intelligent query generation.

## Features

- **Natural Language Processing**: Convert human-readable questions into SQL queries
- **Vector-Based Schema Retrieval**: Uses sentence transformers to embed and retrieve database schema information
- **Marketplace Database**: Pre-configured schema with Users, Products, Orders, and OrderItems tables
- **Data Seeding**: Generate realistic test data using Faker
- **RAG Architecture**: Leverages ChromaDB for semantic search over database schema
- **AI-Powered SQL Agent**: Uses Groq API with advanced LLM models to generate and execute SQL queries
- **Security Guardrails**: Built-in protection against dangerous SQL operations (DROP, DELETE, UPDATE, etc.)
- **Self-Correcting Queries**: Automatic retry mechanism with up to 3 attempts for query refinement
- **JSON Structured Output**: Returns thought process and execution results in structured format

## Project Structure

```
nl2sql/
├── src/
│   ├── agents/
│   │   ├── sql_agent.py        # NL2SQL Agent using Groq API for query generation
│   │   └── __init__.py
│   ├── database/
│   │   ├── db_models.py        # SQLAlchemy ORM models for marketplace database
│   │   ├── data_seed.py        # Script to populate database with fake data
│   │   └── __pycache__/
│   ├── rag/
│   │   ├── vector_store.py     # ChromaDB integration for schema embeddings
│   │   ├── __init__.py
│   │   └── __pycache__/
│   ├── __init__.py
│   └── __pycache__/
├── chroma_db/                   # Vector store storage (persistent)
├── requirements.txt             # Python dependencies
├── pyvenv.cfg                   # Virtual environment config
└── README.md
```

## Dependencies

- **SQLAlchemy**: ORM for database modeling
- **ChromaDB**: Vector database for embeddings
- **sentence-transformers**: Pre-trained transformer for embedding text
- **psycopg2**: PostgreSQL adapter
- **Faker**: Generate realistic test data
- **faker-commerce**: Commerce-specific fake data provider
- **python-dotenv**: Environment variable management
- **Groq**: API client for accessing advanced LLM models

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment (if not already created)
python -m venv .

# Activate virtual environment
# On Windows:
Scripts\Activate.ps1
# On Linux/Mac:
source bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost/nl2sql_db
API_KEY=your_groq_api_key_here
```

### 4. Initialize Database

```bash
python -m src.database.data_seed
```

This will:
- Create the database schema
- Seed realistic marketplace data using Faker
- Index the schema in ChromaDB for RAG retrieval

## Usage

### Seeding Test Data

```python
from src.database.data_seed import seed_data

seed_data()  # Populates database with fake users, products, orders
```

### Using the Vector Store

```python
from src.rag.vector_store import SchemaVectorStorage

vec_store = SchemaVectorStorage()
vec_store.index_schema()  # Index database schema into ChromaDB

# Retrieve schema context for a query
schema_context = vec_store.retrieve_context(query="orders by customers")
```

### Using the NL2SQL Agent

The SQL Agent converts natural language questions into SQL queries, executes them, and provides structured results:

```python
from src.agents.sql_agent import NL2SQL_Agent
from src.rag.vector_store import SchemaVectorStorage

# Initialize agent and vector store
agent = NL2SQL_Agent(max_retries=3)
vec_store = SchemaVectorStorage()

# Get schema context for the query
user_question = "How many orders did each buyer make?"
schema_context = vec_store.retrieve_context(user_question)

# Run the agent to generate and execute SQL
result = agent.run(
    user_question=user_question,
    schema_context=schema_context
)

# Result contains:
# {
#     "status": "success",
#     "response": [execution results],
#     "Query": "generated SQL query"
# }
```

### Agent Features

- **Thought Process**: The agent explains its reasoning for table joins and filtering
- **Security Checks**: Automatically blocks dangerous operations (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, GRANT)
- **Self-Correction**: Implements automatic retry logic with up to 3 attempts to correct failed queries
- **Schema Context**: Retrieves relevant schema information from ChromaDB to provide context to the LLM
- **JSON Output**: Structured JSON responses containing the thought process, SQL query, and execution results

### Example Workflow

```python
from src.agents.sql_agent import NL2SQL_Agent
from src.rag.vector_store import SchemaVectorStorage

# Initialize components
agent = NL2SQL_Agent(max_retries=3)
vec_store = SchemaVectorStorage()

# Example queries
queries = [
    "What are the top 5 most popular products by order count?",
    "List all sellers and their total revenue",
    "Find customers with orders over $1000"
]

for question in queries:
    schema_context = vec_store.retrieve_context(question)
    result = agent.run(user_question=question, schema_context=schema_context)
    
    if result["status"] == "success":
        print(f"Question: {question}")
        print(f"Generated Query: {result['Query']}")
        print(f"Results: {result['response']}\n")
```

## Requirements

- Python 3.x
- PostgreSQL database
- Virtual environment (recommended)

## Technologies Used

- **SQLAlchemy** - Database ORM
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embedding models
- **PostgreSQL** - Primary database
- **Faker** - Test data generation
- **Groq** - LLM API for query generation

## License

This project is provided as-is for development and testing purposes.
