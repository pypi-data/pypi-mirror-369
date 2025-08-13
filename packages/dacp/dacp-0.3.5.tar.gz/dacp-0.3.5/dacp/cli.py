#!/usr/bin/env python3
"""
DACP Command Line Interface

Provides a simple CLI for running workflows and managing agents.
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

import dacp
from dacp.workflow_runtime import WorkflowRuntime


def setup_logging(args):
    """Setup DACP logging based on CLI arguments."""
    log_config = {
        "level": args.log_level or "INFO",
        "format_style": args.log_style or "emoji",
        "include_timestamp": args.timestamp,
    }

    if args.log_file:
        log_config["log_file"] = args.log_file

    dacp.setup_dacp_logging(**log_config)


def load_workflow_config(workflow_path: str) -> Dict[str, Any]:
    """Load workflow configuration from YAML file."""
    workflow_file = Path(workflow_path)
    if not workflow_file.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    with open(workflow_file, "r") as f:
        return yaml.safe_load(f)


def parse_input_data(input_args: list) -> Dict[str, Any]:
    """Parse input data from CLI arguments."""
    input_data = {}

    for arg in input_args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            # Try to parse as JSON, fallback to string
            try:
                input_data[key] = json.loads(value)
            except json.JSONDecodeError:
                input_data[key] = value
        else:
            # Single value, treat as string
            input_data[arg] = ""

    return input_data


def run_workflow(args):
    """Run a workflow with the given configuration."""
    try:
        # Setup logging
        setup_logging(args)

        # Load workflow configuration
        workflow_config = load_workflow_config(args.workflow)

        # Create orchestrator and runtime
        orchestrator = dacp.Orchestrator(session_id=args.session_id)
        runtime = dacp.WorkflowRuntime(orchestrator=orchestrator)

        # Load workflow
        runtime.load_workflow_config(args.workflow)

        # Parse input data
        input_data = parse_input_data(args.input or [])

        # Load and register agents
        agents_config = workflow_config.get("agents", [])
        for agent_config in agents_config:
            agent_id = agent_config.get("id") or agent_config.get(
                "name"
            )  # Support both 'id' and 'name'
            agent_spec = agent_config.get("spec")

            if agent_id and agent_spec:
                print(f"📋 Loading agent: {agent_id} from {agent_spec}")

                # Check if spec is a Python module path (contains :)
                if ":" in agent_spec:
                    # Format: module.path:ClassName
                    try:
                        module_path, class_name = agent_spec.split(":")

                        # Convert module path to file path
                        file_path = module_path.replace(".", "/") + ".py"

                        # Load the agent using importlib
                        import importlib.util

                        spec = importlib.util.spec_from_file_location(
                            f"{agent_id}_module", file_path
                        )
                        agent_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(agent_module)

                        # Get the agent class and instantiate it
                        agent_class = getattr(agent_module, class_name)
                        agent_instance = agent_class(agent_id=agent_id, orchestrator=orchestrator)

                        # Register with runtime
                        runtime.register_agent_from_config(agent_id, agent_instance)
                        print(f"✅ Agent {agent_id} loaded and registered")

                    except Exception as e:
                        print(f"❌ Failed to load agent {agent_id}: {e}")
                        continue

                else:
                    # Legacy YAML file approach
                    agent_path = Path(args.workflow).parent / agent_spec
                    if agent_path.exists():
                        print(f"⚠️  YAML agent specs not yet supported: {agent_spec}")
                    else:
                        print(f"❌ Agent spec file not found: {agent_spec}")

        # Execute workflow
        print(f"🚀 Executing workflow: {args.workflow_name}")
        workflow_id = runtime.execute_workflow(args.workflow_name, input_data)

        # Get results
        status = runtime.get_workflow_status(workflow_id)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(status, f, indent=2)
            print(f"📄 Results saved to: {args.output}")
        else:
            print("📊 Workflow Results:")
            print(json.dumps(status, indent=2))

        return 0

    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return 1


def list_workflows(args):
    """List available workflows in a configuration file."""
    try:
        workflow_config = load_workflow_config(args.workflow)
        workflows = workflow_config.get("workflows", {})

        print(f"📋 Available workflows in {args.workflow}:")
        for name, config in workflows.items():
            description = config.get("description", "No description")
            steps = len(config.get("steps", []))
            print(f"  • {name}: {description} ({steps} steps)")

        return 0

    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DACP - Declarative Agent Communication Protocol CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a workflow
  dacp run workflow examples/github-actions-error-workflow.yaml \\
    --workflow-name quick_error_analysis \\
    --input job_name="build-and-test" \\
    --input raw_logs="npm ERR! code ENOENT..." \\
    --input repository="myorg/myproject"

  # List available workflows
  dacp list workflows examples/github-actions-error-workflow.yaml

  # Run with custom logging
  dacp run workflow workflow.yaml \\
    --log-level DEBUG \\
    --log-style detailed \\
    --output results.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run workflow command
    run_parser = subparsers.add_parser("run", help="Run workflows and agents")
    run_subparsers = run_parser.add_subparsers(dest="run_command", help="Run commands")

    workflow_parser = run_subparsers.add_parser("workflow", help="Run a workflow")
    workflow_parser.add_argument("workflow", help="Path to workflow YAML file")
    workflow_parser.add_argument(
        "--workflow-name", required=True, help="Name of workflow to execute"
    )
    workflow_parser.add_argument(
        "--input", action="append", help="Input data (key=value or just value)"
    )
    workflow_parser.add_argument("--output", help="Output file for results (JSON)")
    workflow_parser.add_argument("--session-id", help="Custom session ID")

    # Logging options
    workflow_parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level"
    )
    workflow_parser.add_argument(
        "--log-style", choices=["emoji", "detailed", "simple"], help="Log style"
    )
    workflow_parser.add_argument("--log-file", help="Log file path")
    workflow_parser.add_argument(
        "--timestamp", action="store_true", help="Include timestamps in logs"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available resources")
    list_subparsers = list_parser.add_subparsers(dest="list_command", help="List commands")

    workflows_parser = list_subparsers.add_parser("workflows", help="List workflows in a file")
    workflows_parser.add_argument("workflow", help="Path to workflow YAML file")

    # Version command
    subparsers.add_parser("version", help="Show DACP version")

    # Serve command for REST API
    serve_parser = subparsers.add_parser("serve", help="Start REST API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    if args.command == "run" and args.run_command == "workflow":
        return run_workflow(args)
    elif args.command == "list" and args.list_command == "workflows":
        return list_workflows(args)
    elif args.command == "version":
        print(f"DACP version {dacp.__version__}")
        return 0
    elif args.command == "serve":
        try:
            from dacp.api import start_server

            start_server(args.host, args.port, args.reload)
            return 0
        except ImportError:
            print("❌ REST API dependencies not installed. Run: pip install dacp[api]")
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
