# NL2SQL - Natural Language to SQL Query Engine

A Retrieval-Augmented Generation (RAG) system that converts natural language queries into SQL statements using vector embeddings of database schemas. This project combines a PostgreSQL marketplace database with ChromaDB vector storage for intelligent query generation.

## Features

- **Natural Language Processing**: Convert human-readable questions into SQL queries
- **Vector-Based Schema Retrieval**: Uses sentence transformers to embed and retrieve database schema information
- **Marketplace Database**: Pre-configured schema with Users, Products, Orders, and OrderItems tables
- **Data Seeding**: Generate realistic test data using Faker
- **RAG Architecture**: Leverages ChromaDB for semantic search over database schema

## Project Structure

```
nl2sql/
├── src/
│   ├── database/
│   │   ├── db_models.py       # SQLAlchemy ORM models for marketplace database
│   │   └── data_seed.py       # Script to populate database with fake data
│   └── rag/
│       └── vector_store.py    # ChromaDB integration for schema embeddings
├── chroma_db/                  # Vector store storage (persistent)
├── requirements.txt            # Python dependencies
├── pyvenv.cfg                 # Virtual environment config
└── README.md
```

## Database Schema

### Tables

1. **Users** - Stores buyer and seller information
   - `user_id` (PK)
   - `username` (unique)
   - `user_type` (Buyer/Seller)

2. **Products** - Product information from sellers
   - `product_id` (PK)
   - `seller_id` (FK to Users)
   - `name`, `description`, `price`, `stock_count`, `category`

3. **Orders** - Order details and status
   - `order_id` (PK)
   - `buyer_id` (FK to Users)
   - `order_status`, `total_amount`, `created_at`

4. **OrderItems** - Individual items in orders
   - `item_id` (PK)
   - `order_id` (FK to Orders)
   - `product_id` (FK to Products)
   - `quantity`, `price_at_purchase`

## Dependencies

- **SQLAlchemy**: ORM for database modeling
- **ChromaDB**: Vector database for embeddings
- **sentence-transformers**: Pre-trained transformer for embedding text
- **psycopg2**: PostgreSQL adapter
- **Faker**: Generate realistic test data
- **faker-commerce**: Commerce-specific fake data provider
- **python-dotenv**: Environment variable management

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
```

### Querying

The vector store enables semantic search over the database schema to retrieve relevant table/column information for natural language queries.

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

## License

This project is provided as-is for development and testing purposes.
