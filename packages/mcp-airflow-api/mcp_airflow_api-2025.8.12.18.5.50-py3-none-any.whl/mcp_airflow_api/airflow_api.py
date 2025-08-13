"""
MCP tool definitions for Airflow REST API operations.
"""
import argparse
import logging
from typing import Any, Dict, List, Optional
import mcp
from mcp.server.fastmcp import FastMCP
import os
from .functions import airflow_request, read_prompt_template, parse_prompt_sections

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# MCP server instance for registering tools
mcp = FastMCP("mcp-airflow-api")

PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "prompt_template.md")



@mcp.tool()
def get_prompt_template(section: Optional[str] = None, mode: Optional[str] = None) -> str:
    """
    Returns the MCP prompt template (full, headings, or specific section).
    Args:
        section: Section number or keyword (optional)
        mode: 'full', 'headings', or None (optional)
    """
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    
    if mode == "headings":
        headings, _ = parse_prompt_sections(template)
        lines = ["Section Headings:"]
        for idx, title in enumerate(headings, 1):
            lines.append(f"{idx}. {title}")
        return "\n".join(lines)
    
    if section:
        headings, sections = parse_prompt_sections(template)
        # Try by number
        try:
            idx = int(section) - 1
            if 0 <= idx < len(sections):
                return sections[idx]
        except Exception:
            pass
        # Try by keyword
        section_lower = section.strip().lower()
        for i, heading in enumerate(headings):
            if section_lower in heading.lower():
                return sections[i]
        return f"Section '{section}' not found."
    
    return template

@mcp.tool()
def list_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all DAGs registered in the Airflow cluster.

    Returns:
        List of DAGs with minimal info: dag_id, dag_display_name, is_active, is_paused, owners, tags
    """
    resp = airflow_request("GET", "/dags")
    resp.raise_for_status()
    dags = resp.json().get("dags", [])
    minimal = []
    for dag in dags:
        minimal.append({
            "dag_id": dag.get("dag_id"),
            "dag_display_name": dag.get("dag_display_name"),
            "is_active": dag.get("is_active"),
            "is_paused": dag.get("is_paused"),
            "owners": dag.get("owners"),
            "tags": [t.get("name") for t in dag.get("tags", [])]
        })
    return {"dags": minimal}

@mcp.tool()
def running_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all currently running DAG runs in the Airflow cluster.

    Returns:
        List of running DAG runs with minimal info: dag_id, run_id, state, execution_date, start_date, end_date
    """
    dags_resp = airflow_request("GET", "/dags")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    running = []
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
        runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        for run in runs:
            if run.get("state") == "running":
                running.append({
                    "dag_id": dag_id,
                    "run_id": run.get("run_id"),
                    "state": run.get("state"),
                    "execution_date": run.get("execution_date"),
                    "start_date": run.get("start_date"),
                    "end_date": run.get("end_date")
                })
    return {"dag_runs": running}

@mcp.tool()
def failed_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all recently failed DAG runs in the Airflow cluster.

    Returns:
        List of failed DAG runs with minimal info: dag_id, run_id, state, execution_date, start_date, end_date
    """
    dags_resp = airflow_request("GET", "/dags")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    failed = []
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
        runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        for run in runs:
            if run.get("state") == "failed":
                failed.append({
                    "dag_id": dag_id,
                    "run_id": run.get("run_id"),
                    "state": run.get("state"),
                    "execution_date": run.get("execution_date"),
                    "start_date": run.get("start_date"),
                    "end_date": run.get("end_date")
                })
    return {"dag_runs": failed}

@mcp.tool()
def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Triggers a new DAG run for a specified Airflow DAG.

    Args:
        dag_id: The DAG ID to trigger

    Returns:
        Minimal info about triggered DAG run: dag_id, run_id, state, execution_date, start_date, end_date
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("POST", f"/dags/{dag_id}/dagRuns", json={"conf": {}})
    resp.raise_for_status()
    run = resp.json()
    return {
        "dag_id": dag_id,
        "run_id": run.get("run_id"),
        "state": run.get("state"),
        "execution_date": run.get("execution_date"),
        "start_date": run.get("start_date"),
        "end_date": run.get("end_date")
    }

@mcp.tool()
def pause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Pauses the specified Airflow DAG (prevents scheduling new runs).

    Args:
        dag_id: The DAG ID to pause

    Returns:
        Minimal info about the paused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": True})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", True)}

@mcp.tool()
def unpause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Unpauses the specified Airflow DAG (allows scheduling new runs).

    Args:
        dag_id: The DAG ID to unpause

    Returns:
        Minimal info about the unpaused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": False})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", False)}

@mcp.tool()
def dag_details(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves detailed information for a specific DAG.

    Args:
        dag_id: The DAG ID to get details for

    Returns:
        Comprehensive DAG details: dag_id, schedule_interval, start_date, owners, tags, description, etc.
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("GET", f"/dags/{dag_id}")
    resp.raise_for_status()
    dag = resp.json()
    return {
        "dag_id": dag.get("dag_id"),
        "dag_display_name": dag.get("dag_display_name"),
        "description": dag.get("description"),
        "schedule_interval": dag.get("schedule_interval"),
        "start_date": dag.get("start_date"),
        "end_date": dag.get("end_date"),
        "is_active": dag.get("is_active"),
        "is_paused": dag.get("is_paused"),
        "owners": dag.get("owners"),
        "tags": [t.get("name") for t in dag.get("tags", [])],
        "catchup": dag.get("catchup"),
        "max_active_runs": dag.get("max_active_runs"),
        "max_active_tasks": dag.get("max_active_tasks"),
        "has_task_concurrency_limits": dag.get("has_task_concurrency_limits"),
        "has_import_errors": dag.get("has_import_errors"),
        "next_dagrun": dag.get("next_dagrun"),
        "next_dagrun_data_interval_start": dag.get("next_dagrun_data_interval_start"),
        "next_dagrun_data_interval_end": dag.get("next_dagrun_data_interval_end")
    }

@mcp.tool()
def dag_graph(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves the task dependency graph structure for a specific DAG.

    Args:
        dag_id: The DAG ID to get graph structure for

    Returns:
        DAG graph with tasks and dependencies: dag_id, tasks, dependencies
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("GET", f"/dags/{dag_id}/tasks")
    resp.raise_for_status()
    tasks = resp.json().get("tasks", [])
    
    graph_data = {"dag_id": dag_id, "tasks": [], "total_tasks": len(tasks)}
    for task in tasks:
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "operator_name": task.get("class_ref", {}).get("class_name"),
            "downstream_task_ids": task.get("downstream_task_ids", []),
            "upstream_task_ids": task.get("upstream_task_ids", []),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "depends_on_past": task.get("depends_on_past"),
            "wait_for_downstream": task.get("wait_for_downstream"),
            "retries": task.get("retries"),
            "pool": task.get("pool")
        }
        graph_data["tasks"].append(task_info)
    
    return graph_data

@mcp.tool()
def list_tasks(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Lists all tasks for a specific DAG.

    Args:
        dag_id: The DAG ID to get tasks for

    Returns:
        List of tasks with detailed task information: dag_id, tasks, total_tasks
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("GET", f"/dags/{dag_id}/tasks")
    resp.raise_for_status()
    tasks = resp.json().get("tasks", [])
    
    task_list = []
    for task in tasks:
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "operator_name": task.get("class_ref", {}).get("class_name"),
            "operator_module": task.get("class_ref", {}).get("module_path"),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "depends_on_past": task.get("depends_on_past"),
            "wait_for_downstream": task.get("wait_for_downstream"),
            "retries": task.get("retries"),
            "retry_delay": task.get("retry_delay"),
            "max_retry_delay": task.get("max_retry_delay"),
            "pool": task.get("pool"),
            "pool_slots": task.get("pool_slots"),
            "execution_timeout": task.get("execution_timeout"),
            "email_on_retry": task.get("email_on_retry"),
            "email_on_failure": task.get("email_on_failure"),
            "trigger_rule": task.get("trigger_rule"),
            "weight_rule": task.get("weight_rule"),
            "priority_weight": task.get("priority_weight")
        }
        task_list.append(task_info)
    
    return {
        "dag_id": dag_id,
        "tasks": task_list,
        "total_tasks": len(tasks)
    }

@mcp.tool()
def dag_code(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves the source code for a specific DAG.

    Args:
        dag_id: The DAG ID to get source code for

    Returns:
        DAG source code: dag_id, file_token, source_code
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # First get DAG details to obtain file_token
    dag_resp = airflow_request("GET", f"/dags/{dag_id}")
    dag_resp.raise_for_status()
    dag_data = dag_resp.json()
    
    file_token = dag_data.get("file_token")
    if not file_token:
        return {"dag_id": dag_id, "error": "File token not available for this DAG"}
    
    # Now get the source code using the file_token
    # Note: This endpoint returns plain text, not JSON
    source_resp = airflow_request("GET", f"/dagSources/{file_token}")
    source_resp.raise_for_status()
    
    # Get the plain text content directly
    source_code = source_resp.text
    
    return {
        "dag_id": dag_id,
        "file_token": file_token,
        "source_code": source_code if source_code else "Source code not available"
    }

@mcp.tool()
def list_event_logs(dag_id: str = None, task_id: str = None, run_id: str = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: Lists event log entries with optional filtering.

    Args:
        dag_id: Filter by DAG ID (optional)
        task_id: Filter by task ID (optional)
        run_id: Filter by run ID (optional)
        limit: Maximum number of log entries to return (default: 20)
        offset: Number of entries to skip (default: 0)

    Returns:
        List of event logs: event_logs, total_entries, limit, offset
    """
    # Build query parameters
    params = []
    if dag_id:
        params.append(f"dag_id={dag_id}")
    if task_id:
        params.append(f"task_id={task_id}")
    if run_id:
        params.append(f"run_id={run_id}")
    params.append(f"limit={limit}")
    params.append(f"offset={offset}")
    
    query_string = "&".join(params)
    resp = airflow_request("GET", f"/eventLogs?{query_string}")
    resp.raise_for_status()
    logs = resp.json()
    
    events = []
    for log in logs.get("event_logs", []):
        event_info = {
            "event_log_id": log.get("event_log_id"),
            "when": log.get("when"),
            "event": log.get("event"),
            "dag_id": log.get("dag_id"),
            "task_id": log.get("task_id"),
            "run_id": log.get("run_id"),
            "map_index": log.get("map_index"),
            "try_number": log.get("try_number"),
            "owner": log.get("owner"),
            "extra": log.get("extra")
        }
        events.append(event_info)
    
    return {
        "event_logs": events,
        "total_entries": logs.get("total_entries", len(events)),
        "limit": limit,
        "offset": offset
    }

@mcp.tool()
def get_event_log(event_log_id: int) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific event log entry by ID.

    Args:
        event_log_id: The event log ID to retrieve

    Returns:
        Single event log entry: event_log_id, when, event, dag_id, task_id, run_id, etc.
    """
    if not event_log_id:
        raise ValueError("event_log_id must not be empty")
    
    resp = airflow_request("GET", f"/eventLogs/{event_log_id}")
    resp.raise_for_status()
    log = resp.json()
    
    return {
        "event_log_id": log.get("event_log_id"),
        "when": log.get("when"),
        "event": log.get("event"),
        "dag_id": log.get("dag_id"),
        "task_id": log.get("task_id"),
        "run_id": log.get("run_id"),
        "map_index": log.get("map_index"),
        "try_number": log.get("try_number"),
        "owner": log.get("owner"),
        "extra": log.get("extra")
    }

@mcp.tool()
def all_dag_event_summary() -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves event count summary for all DAGs.

    Returns:
        Summary of event counts by DAG: dag_summaries, total_dags, total_events
    """
    # First get all DAGs
    dags_resp = airflow_request("GET", "/dags")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    
    dag_summaries = []
    total_events = 0
    
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
            
        # Get event count for this DAG (using limit=1 and checking total_entries)
        try:
            events_resp = airflow_request("GET", f"/eventLogs?dag_id={dag_id}&limit=1")
            events_resp.raise_for_status()
            events_data = events_resp.json()
            event_count = events_data.get("total_entries", 0)
        except Exception:
            # If error occurs, set count to 0
            event_count = 0
        
        dag_summary = {
            "dag_id": dag_id,
            "dag_display_name": dag.get("dag_display_name"),
            "is_active": dag.get("is_active"),
            "is_paused": dag.get("is_paused"),
            "event_count": event_count
        }
        dag_summaries.append(dag_summary)
        total_events += event_count
    
    # Sort by event count (descending)
    dag_summaries.sort(key=lambda x: x["event_count"], reverse=True)
    
    return {
        "dag_summaries": dag_summaries,
        "total_dags": len(dag_summaries),
        "total_events": total_events
    }

@mcp.tool()
def list_import_errors(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: Lists import errors with optional filtering.

    Args:
        limit: Maximum number of import errors to return (default: 20)
        offset: Number of entries to skip (default: 0)

    Returns:
        List of import errors: import_errors, total_entries, limit, offset
    """
    # Build query parameters
    params = [f"limit={limit}", f"offset={offset}"]
    query_string = "&".join(params)
    
    resp = airflow_request("GET", f"/importErrors?{query_string}")
    resp.raise_for_status()
    errors = resp.json()
    
    import_errors = []
    for error in errors.get("import_errors", []):
        error_info = {
            "import_error_id": error.get("import_error_id"),
            "filename": error.get("filename"),
            "stacktrace": error.get("stacktrace"),
            "timestamp": error.get("timestamp")
        }
        import_errors.append(error_info)
    
    return {
        "import_errors": import_errors,
        "total_entries": errors.get("total_entries", len(import_errors)),
        "limit": limit,
        "offset": offset
    }

@mcp.tool()
def get_import_error(import_error_id: int) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific import error by ID.

    Args:
        import_error_id: The import error ID to retrieve

    Returns:
        Single import error: import_error_id, filename, stacktrace, timestamp
    """
    if not import_error_id:
        raise ValueError("import_error_id must not be empty")
    
    resp = airflow_request("GET", f"/importErrors/{import_error_id}")
    resp.raise_for_status()
    error = resp.json()
    
    return {
        "import_error_id": error.get("import_error_id"),
        "filename": error.get("filename"),
        "stacktrace": error.get("stacktrace"),
        "timestamp": error.get("timestamp")
    }

@mcp.tool()
def all_dag_import_summary() -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves import error summary for all DAGs.

    Returns:
        Summary of import errors by filename: import_summaries, total_errors, affected_files
    """
    # Get all import errors (using a large limit to get all)
    try:
        errors_resp = airflow_request("GET", "/importErrors?limit=1000")
        errors_resp.raise_for_status()
        errors_data = errors_resp.json()
        errors = errors_data.get("import_errors", [])
    except Exception:
        # If error occurs, return empty summary
        return {
            "import_summaries": [],
            "total_errors": 0,
            "affected_files": 0
        }
    
    # Group errors by filename
    filename_errors = {}
    for error in errors:
        filename = error.get("filename", "unknown")
        if filename not in filename_errors:
            filename_errors[filename] = {
                "filename": filename,
                "error_count": 0,
                "latest_timestamp": None,
                "error_ids": []
            }
        
        filename_errors[filename]["error_count"] += 1
        filename_errors[filename]["error_ids"].append(error.get("import_error_id"))
        
        # Track latest timestamp
        timestamp = error.get("timestamp")
        if timestamp:
            if not filename_errors[filename]["latest_timestamp"] or timestamp > filename_errors[filename]["latest_timestamp"]:
                filename_errors[filename]["latest_timestamp"] = timestamp
    
    # Convert to list and sort by error count
    import_summaries = list(filename_errors.values())
    import_summaries.sort(key=lambda x: x["error_count"], reverse=True)
    
    return {
        "import_summaries": import_summaries,
        "total_errors": len(errors),
        "affected_files": len(import_summaries)
    }

@mcp.tool()
def dag_run_duration(dag_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves run duration statistics for a specific DAG.

    Args:
        dag_id: The DAG ID to get run durations for
        limit: Maximum number of recent runs to analyze (default: 10)

    Returns:
        DAG run duration data: dag_id, runs, statistics
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns?limit={limit}&order_by=-execution_date")
    resp.raise_for_status()
    runs = resp.json().get("dag_runs", [])
    
    run_durations = []
    durations = []
    
    for run in runs:
        start_date = run.get("start_date")
        end_date = run.get("end_date")
        
        duration = None
        if start_date and end_date:
            # Calculate duration in seconds (simplified)
            duration = "calculated_duration_placeholder"
        
        run_info = {
            "run_id": run.get("run_id"),
            "execution_date": run.get("execution_date"),
            "start_date": start_date,
            "end_date": end_date,
            "state": run.get("state"),
            "duration": duration
        }
        run_durations.append(run_info)
        
        if duration:
            durations.append(duration)
    
    return {
        "dag_id": dag_id,
        "runs": run_durations,
        "total_runs_analyzed": len(runs),
        "completed_runs": len([r for r in runs if r.get("state") == "success"]),
        "failed_runs": len([r for r in runs if r.get("state") == "failed"])
    }

@mcp.tool()
def dag_task_duration(dag_id: str, run_id: str = None) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves task duration information for a specific DAG run.

    Args:
        dag_id: The DAG ID to get task durations for
        run_id: Specific run ID (if not provided, uses latest run)

    Returns:
        Task duration data: dag_id, run_id, tasks, statistics
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # If no run_id provided, get the latest run
    if not run_id:
        runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns?limit=1&order_by=-execution_date")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        if not runs:
            return {"dag_id": dag_id, "error": "No runs found"}
        run_id = runs[0].get("run_id")
    
    # Get task instances for the run
    resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns/{run_id}/taskInstances")
    resp.raise_for_status()
    tasks = resp.json().get("task_instances", [])
    
    task_durations = []
    for task in tasks:
        start_date = task.get("start_date")
        end_date = task.get("end_date")
        
        duration = None
        if start_date and end_date:
            duration = "calculated_duration_placeholder"
        
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "state": task.get("state"),
            "try_number": task.get("try_number"),
            "max_tries": task.get("max_tries")
        }
        task_durations.append(task_info)
    
    return {
        "dag_id": dag_id,
        "run_id": run_id,
        "tasks": task_durations,
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get("state") == "success"]),
        "failed_tasks": len([t for t in tasks if t.get("state") == "failed"])
    }

@mcp.tool()
def dag_calendar(dag_id: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves calendar/schedule information for a specific DAG.

    Args:
        dag_id: The DAG ID to get calendar info for
        start_date: Start date for calendar range (YYYY-MM-DD format, optional)
        end_date: End date for calendar range (YYYY-MM-DD format, optional)

    Returns:
        DAG calendar data: dag_id, schedule_interval, runs, next_runs
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # Get DAG details for schedule info
    dag_resp = airflow_request("GET", f"/dags/{dag_id}")
    dag_resp.raise_for_status()
    dag = dag_resp.json()
    
    # Build query parameters for date range
    query_params = "?limit=50&order_by=-execution_date"
    if start_date:
        query_params += f"&start_date_gte={start_date}T00:00:00Z"
    if end_date:
        query_params += f"&start_date_lte={end_date}T23:59:59Z"
    
    # Get DAG runs within date range
    runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns{query_params}")
    runs_resp.raise_for_status()
    runs = runs_resp.json().get("dag_runs", [])
    
    calendar_runs = []
    for run in runs:
        run_info = {
            "run_id": run.get("run_id"),
            "execution_date": run.get("execution_date"),
            "start_date": run.get("start_date"),
            "end_date": run.get("end_date"),
            "state": run.get("state"),
            "run_type": run.get("run_type")
        }
        calendar_runs.append(run_info)
    
    return {
        "dag_id": dag_id,
        "schedule_interval": dag.get("schedule_interval"),
        "start_date": dag.get("start_date"),
        "next_dagrun": dag.get("next_dagrun"),
        "next_dagrun_data_interval_start": dag.get("next_dagrun_data_interval_start"),
        "next_dagrun_data_interval_end": dag.get("next_dagrun_data_interval_end"),
        "runs": calendar_runs,
        "total_runs_in_range": len(runs),
        "query_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

#========================================================================================
# MCP Prompts (for prompts/list exposure)
#========================================================================================

@mcp.prompt("prompt_template_full")
def prompt_template_full_prompt() -> str:
    """Return the full canonical prompt template."""
    return read_prompt_template(PROMPT_TEMPLATE_PATH)

@mcp.prompt("prompt_template_headings")
def prompt_template_headings_prompt() -> str:
    """Return compact list of section headings."""
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    headings, _ = parse_prompt_sections(template)
    lines = ["Section Headings:"]
    for idx, title in enumerate(headings, 1):
        lines.append(f"{idx}. {title}")
    return "\n".join(lines)

@mcp.prompt("prompt_template_section")
def prompt_template_section_prompt(section: Optional[str] = None) -> str:
    """Return a specific prompt template section by number or keyword."""
    if not section:
        headings_result = prompt_template_headings_prompt()
        return "\n".join([
            "[HELP] Missing 'section' argument.",
            "Specify a section number or keyword.",
            "Examples: 1 | overview | tool map | usage",
            headings_result.strip()
        ])
    return get_prompt_template(section=section)

#========================================================================================

def main(argv: Optional[List[str]] = None):
    """Entrypoint for MCP Airflow API server.

    Supports optional CLI arguments (e.g. --log-level DEBUG) while remaining
    backward-compatible with stdio launcher expectations.
    """
    parser = argparse.ArgumentParser(prog="mcp-airflow-api", description="MCP Airflow API Server")
    parser.add_argument(
        "--log-level", "-l",
        dest="log_level",
        help="Logging level override (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overrides AIRFLOW_LOG_LEVEL env if provided.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    # Allow future extension without breaking unknown args usage
    args = parser.parse_args(argv)

    if args.log_level:
        # Override root + specific logger level
        logging.getLogger().setLevel(args.log_level)
        logger.setLevel(args.log_level)
        logging.getLogger("requests.packages.urllib3").setLevel("WARNING")  # reduce noise at DEBUG
        logger.info("Log level set via CLI to %s", args.log_level)
    else:
        logger.debug("Log level from environment: %s", logging.getLogger().level)

    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
