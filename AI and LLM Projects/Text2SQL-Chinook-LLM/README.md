# Text-to-SQL over the Chinook Database (LangChain + LangGraph)

An LLM application that converts natural language questions into executable SQL queries against
the [Chinook sample database](https://github.com/lerocha/chinook-database), returning both the generated
SQL and the query result. Evaluated against a held-out set of test questions with **~88% answer accuracy**.

## What this demonstrates
- Prompting an LLM (OpenAI via LangChain) to generate valid SQL from natural language, grounded in a real
  multi-table relational schema (11 tables, artists/albums/tracks/invoices/customers, etc.)
- A second iteration using **LangGraph** to structure the pipeline as a multi-step agent (schema retrieval →
  SQL generation → execution → self-correction) rather than a single prompt call
- A repeatable evaluation harness (`scripts/agent_test_runner.py`, `scripts/run_graph_tests.py`) that runs a
  fixed question set against the pipeline and scores accuracy, rather than relying on spot-checks

## Project structure
```
Text2SQL-Chinook-LLM/
├── notebooks/
│   ├── Text2SQL_Chinook_LangChain.ipynb   # Core LangChain Text-to-SQL pipeline
│   └── Text2SQL_LangGraph_Agent.ipynb     # LangGraph agent-based iteration
├── scripts/
│   ├── setup_download_chinook_db.py       # Downloads & builds the Chinook SQLite DB from source
│   ├── export_chinook_excel.py            # Exports DB tables to Excel for quick inspection
│   ├── sqlite_to_dbml.py                  # Generates a DBML schema diagram definition from the DB
│   ├── agent_test_runner.py               # Evaluation harness for the LangChain pipeline
│   └── run_graph_tests.py                 # Evaluation harness for the LangGraph agent
├── data/
│   ├── Chinook.db                         # SQLite database used for querying
│   ├── Chinook.dbml                       # Schema definition (viewable at dbdiagram.io)
│   ├── Chinook_ERD.pdf                    # Entity-relationship diagram
│   └── Chinook_all_tables_reference.xlsx  # Human-readable export of all tables
├── results/
│   ├── text2sql_evaluation_results.xlsx   # Question / generated SQL / result / answer, per test case
│   └── agent_evaluation_detailed.xlsx     # Detailed per-question evaluation output
└── requirements.txt
```

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root (not committed to this repo) with:
```
OPENAI_API_KEY=your-key-here
```

## Running it
- Open `notebooks/Text2SQL_Chinook_LangChain.ipynb` to run the core pipeline interactively
- Open `notebooks/Text2SQL_LangGraph_Agent.ipynb` for the agent-based version
- Run `scripts/agent_test_runner.py` or `scripts/run_graph_tests.py` to reproduce the evaluation results

## Notes
- Currently scoped to single/multi-table querying over one schema (Chinook); no vector-store retrieval yet.
- Planned extensions: RAG-based schema retrieval for larger schemas, multi-step reasoning for complex joins.

## References
- [LangChain SQL Q&A Tutorial](https://python.langchain.com/docs/tutorials/sql_qa/)
- [Chinook Database](https://github.com/lerocha/chinook-database)
