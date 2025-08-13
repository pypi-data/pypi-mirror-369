# MCP Airflow API Prompt Template

## 1. Overview

This MCP server provides natural language tools for managing Apache Airflow clusters via REST API. All prompts and tool outputs are designed for minimal, LLM-friendly English responses.

## 2. Available MCP Tools

### Basic DAG Management
- `list_dags`: List all DAGs in the Airflow cluster.
- `running_dags`: List all currently running DAG runs.
- `failed_dags`: List all recently failed DAG runs.
- `trigger_dag(dag_id)`: Trigger a DAG run by ID.
- `pause_dag(dag_id)`: Pause a DAG (prevent scheduling).
- `unpause_dag(dag_id)`: Unpause a DAG (allow scheduling).

### Cluster Management & Health
- `get_health`: Get the health status of the Airflow webserver instance.
- `get_version`: Get version information of the Airflow instance.

### Pool Management
- `list_pools(limit, offset)`: List all pools in the Airflow instance.
- `get_pool(pool_name)`: Get detailed information about a specific pool.

### DAG Analysis & Monitoring
- `dag_details(dag_id)`: Get comprehensive details for a specific DAG.
- `dag_graph(dag_id)`: Get task dependency graph structure for a DAG.
- `list_tasks(dag_id)`: List all tasks for a specific DAG.
- `dag_code(dag_id)`: Retrieve source code for a specific DAG.
- `list_event_logs(dag_id, task_id, run_id, limit, offset)`: List event log entries with filtering.
- `get_event_log(event_log_id)`: Get a specific event log entry by ID.
- `all_dag_event_summary()`: Get event count summary for all DAGs.
- `list_import_errors(limit, offset)`: List import errors with filtering.
- `get_import_error(import_error_id)`: Get a specific import error by ID.
- `all_dag_import_summary()`: Get import error summary for all DAGs.
- `dag_run_duration(dag_id, limit)`: Get run duration statistics for a DAG.
- `dag_task_duration(dag_id, run_id)`: Get task duration info for a DAG run.
- `dag_calendar(dag_id, start_date, end_date)`: Get calendar/schedule info for a DAG.

## 3. Tool Map

| Tool Name           | Role/Description                          | Input Args                    | Output Fields                        |
|---------------------|-------------------------------------------|-------------------------------|--------------------------------------|
| **Basic DAG Management** |                                     |                               |                                      |
| list_dags           | List all DAGs                             | None                          | dag_id, dag_display_name, is_active, is_paused, owners, tags |
| running_dags        | List running DAG runs                     | None                          | dag_id, run_id, state, execution_date, start_date, end_date |
| failed_dags         | List failed DAG runs                      | None                          | dag_id, run_id, state, execution_date, start_date, end_date |
| trigger_dag         | Trigger a DAG run                         | dag_id (str)                  | dag_id, run_id, state, execution_date, start_date, end_date |
| pause_dag           | Pause a DAG                               | dag_id (str)                  | dag_id, is_paused                    |
| unpause_dag         | Unpause a DAG                             | dag_id (str)                  | dag_id, is_paused                    |
| **Cluster Management & Health** |                                   |                               |                                      |
| get_health          | Get health status of webserver            | None                          | metadatabase, scheduler, status      |
| get_version         | Get version information                   | None                          | version, git_version, build_date, api_version |
| **Pool Management** |                                           |                               |                                      |
| list_pools          | List all pools in Airflow                | limit, offset                 | pools, total_entries, slots usage   |
| get_pool            | Get specific pool details                 | pool_name (str)               | name, slots, occupied_slots, running_slots, queued_slots, open_slots, description, utilization_percentage |
| **DAG Analysis & Monitoring** |                                   |                               |                                      |
| dag_details         | Get comprehensive DAG details             | dag_id (str)                  | dag_id, schedule_interval, start_date, owners, tags, description, etc. |
| dag_graph           | Get task dependency graph                 | dag_id (str)                  | dag_id, tasks, dependencies, total_tasks |
| list_tasks          | List all tasks for a specific DAG        | dag_id (str)                  | dag_id, tasks, task_configuration_details |
| dag_code            | Get DAG source code                       | dag_id (str)                  | dag_id, file_token, source_code      |
| list_event_logs     | List event log entries with filtering     | dag_id, task_id, run_id, limit, offset | event_logs, total_entries, limit, offset |
| get_event_log       | Get specific event log entry by ID        | event_log_id (int)            | event_log_id, when, event, dag_id, task_id, run_id, etc. |
| all_dag_event_summary | Get event count summary for all DAGs    | None                          | dag_summaries, total_dags, total_events |
| list_import_errors  | List import errors with filtering         | limit, offset                 | import_errors, total_entries, limit, offset |
| get_import_error    | Get specific import error by ID           | import_error_id (int)         | import_error_id, filename, stacktrace, timestamp |
| all_dag_import_summary | Get import error summary for all DAGs | None                          | import_summaries, total_errors, affected_files |
| dag_run_duration    | Get run duration statistics               | dag_id (str), limit (int)     | dag_id, runs, statistics             |
| dag_task_duration   | Get task duration for a run               | dag_id (str), run_id (str)    | dag_id, run_id, tasks, statistics    |
| dag_calendar        | Get calendar/schedule information         | dag_id (str), start_date, end_date | dag_id, schedule_interval, runs, next_runs |

## 4. Usage Guidelines

- Always use minimal, structured output.
- All tool invocations must use English for internal reasoning.
- For user-facing responses, translate to the user's language if needed.

## 5. Example Queries

### Basic DAG Operations
- "List all DAGs."
- "Show running DAGs."
- "Show failed DAGs."
- "Trigger DAG 'example_dag'."
- "Pause DAG 'etl_job'."
- "Unpause DAG 'etl_job'."

### Cluster Management & Health
- "Check Airflow cluster health."
- "Get Airflow version information."

### Pool Management
- "List all pools."
- "Show pool usage statistics."
- "Get details for pool 'default_pool'."
- "Check pool utilization."

### DAG Analysis & Monitoring
- "Get details for DAG 'my_dag'."
- "Show task graph for DAG 'workflow_dag'."
- "List all tasks in DAG 'data_pipeline'."
- "Get source code for DAG 'data_pipeline'."
- "List event logs for DAG 'etl_process'."
- "Get event log entry with ID 12345."
- "Show event count summary for all DAGs."
- "List import errors."
- "Get import error with ID 67890."
- "Show import error summary for all DAGs."
- "Get run duration stats for DAG 'batch_job'."
- "Show task durations for latest run of 'ml_pipeline'."
- "Get calendar info for DAG 'daily_report' from 2024-01-01 to 2024-01-31."

## 6. Formatting Rules

- Output only the requested fields.
- No extra explanation unless explicitly requested.
- Use JSON objects for tool outputs.

## 7. Logging & Environment

- Control log level via AIRFLOW_LOG_LEVEL env or --log-level CLI flag.
- Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.

## 8. References

- Main MCP tool file: `src/mcp_airflow_api/airflow_api.py`
- Utility functions: `src/mcp_airflow_api/functions.py`
- See README.md for full usage and configuration.
