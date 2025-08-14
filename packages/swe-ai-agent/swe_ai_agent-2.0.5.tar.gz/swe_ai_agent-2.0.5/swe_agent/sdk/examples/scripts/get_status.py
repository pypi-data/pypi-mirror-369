#!/usr/bin/env python3
"""
Python script for getting SWE Agent status from VS Code extension
"""

import sys
import json
from pathlib import Path

# Add SDK to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sdk import SWEAgentClient
from sdk.exceptions import SWEAgentException


def main():
    try:
        client = SWEAgentClient()
        status = client.get_agent_status()
        
        # Convert status to JSON
        result = {
            'is_running': status.is_running,
            'current_task': status.current_task,
            'uptime': status.uptime,
            'total_tasks': status.total_tasks,
            'successful_tasks': status.successful_tasks,
            'failed_tasks': status.failed_tasks,
            'agents_available': [agent.value for agent in status.agents_available],
            'system_info': status.system_info
        }
        
        print(json.dumps(result, indent=2))
        
    except SWEAgentException as e:
        error_result = {
            'error': str(e),
            'is_running': False,
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'agents_available': []
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            'error': f'Unexpected error: {str(e)}',
            'is_running': False,
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'agents_available': []
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()