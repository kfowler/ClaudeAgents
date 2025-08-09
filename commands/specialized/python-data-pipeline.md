# Python Data Pipeline & Analytics

Build robust data processing pipelines and analytics workflows:

**Modern Data Processing:**
- **Polars**: Lightning-fast DataFrame operations with lazy evaluation
- **DuckDB**: In-process analytics database for OLAP queries
- **Pandas 2.0**: Traditional DataFrame processing with Arrow backend
- **PyArrow**: Columnar data processing and Parquet handling

**Pipeline Orchestration:**
- **Prefect**: Modern workflow orchestration with Python-native approach
- **Airflow**: Established workflow management platform
- **Dagster**: Data orchestrator with strong typing and testing
- **Luigi**: Dependency resolution for complex data pipelines

**Database Integration:**
- Connect to PostgreSQL with asyncpg for high-performance queries
- Handle large datasets with chunked processing and streaming
- Use SQLAlchemy 2.0 for ORM and raw SQL execution
- Implement connection pooling and transaction management

**Data Validation & Quality:**
- **Pydantic**: Type-safe data validation and serialization
- **Great Expectations**: Data quality and validation framework
- **Pandera**: Statistical data validation for DataFrames
- **Cerberus**: Lightweight data validation library

**ETL/ELT Patterns:**
- Extract data from APIs, databases, and file systems
- Transform data using functional programming patterns
- Load data into warehouses, databases, or analytical systems
- Handle incremental updates and change data capture

**Performance Optimization:**
- Profile data processing bottlenecks with py-spy and scalene
- Optimize memory usage for large dataset processing
- Use multiprocessing and concurrent.futures for parallelization
- Implement caching strategies for expensive computations

**File Format Handling:**
- **Parquet**: Columnar storage for analytics workloads
- **Arrow**: In-memory columnar format for fast processing
- **JSON Lines**: Streaming JSON processing for large files
- **CSV/TSV**: Traditional delimited file handling with optimization

**Streaming & Real-time Processing:**
- Handle real-time data streams with asyncio patterns
- Process message queues (Redis, RabbitMQ) for event-driven pipelines
- Implement backpressure and flow control mechanisms
- Create reactive data processing workflows

**Monitoring & Observability:**
- Implement structured logging for pipeline monitoring
- Create metrics and alerts for data quality issues
- Track pipeline performance and resource usage
- Set up error handling and retry mechanisms

**Integration with Your Stack:**
- Deploy data pipelines to pi server via dokku
- Run processing jobs in OrbStack containers
- Connect to existing PostgreSQL databases
- Interface with Rust for performance-critical processing
- Create web dashboards for pipeline monitoring

**Testing & Quality Assurance:**
- Unit test data transformations and business logic
- Integration test full pipeline workflows
- Validate data schemas and business rules
- Create synthetic test data for development

Data Source/Pipeline Type: $ARGUMENTS

