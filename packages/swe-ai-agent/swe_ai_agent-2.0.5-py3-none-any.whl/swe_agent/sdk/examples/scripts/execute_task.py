#!/usr/bin/env python3
"""
Python script for executing SWE Agent tasks from VS Code extension
"""

import sys
import json
import argparse
from pathlib import Path

# Add SDK to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sdk import SWEAgentClient, TaskRequest, TaskStatus
from sdk.exceptions import SWEAgentException


def main():
    parser = argparse.ArgumentParser(description='Execute SWE Agent task')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--working-directory', default='.', help='Working directory')
    parser.add_argument('--context-files', default='', help='Comma-separated context files')
    parser.add_argument('--use-planner', action='store_true', help='Use planner agent')
    parser.add_argument('--timeout', type=int, default=300, help='Task timeout in seconds')
    
    args = parser.parse_args()
    
    try:
        # Parse context files
        context_files = []
        if args.context_files:
            context_files = [f.strip() for f in args.context_files.split(',') if f.strip()]
        
        # Create task request
        request = TaskRequest(
            task=args.task,
            use_planner=args.use_planner,
            context_files=context_files,
            working_directory=args.working_directory,
            timeout=args.timeout
        )
        
        # Create client and execute task
        client = SWEAgentClient(
            working_directory=args.working_directory,
            log_level="INFO",
            timeout=args.timeout
        )
        
        response = client.execute_task(request)
        
        # Convert response to JSON
        result = {
            'task_id': response.task_id,
            'status': response.status.value,
            'result': response.result,
            'error': response.error,
            'execution_time': response.execution_time,
            'agent_visits': response.agent_visits,
            'tools_used': response.tools_used,
            'files_modified': response.files_modified,
            'timestamp': response.timestamp.isoformat()
        }
        
        print(json.dumps(result, indent=2))
        
    except SWEAgentException as e:
        error_result = {
            'task_id': '',
            'status': 'failed',
            'error': str(e),
            'execution_time': 0.0,
            'agent_visits': {},
            'tools_used': [],
            'files_modified': []
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            'task_id': '',
            'status': 'failed',
            'error': f'Unexpected error: {str(e)}',
            'execution_time': 0.0,
            'agent_visits': {},
            'tools_used': [],
            'files_modified': []
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()