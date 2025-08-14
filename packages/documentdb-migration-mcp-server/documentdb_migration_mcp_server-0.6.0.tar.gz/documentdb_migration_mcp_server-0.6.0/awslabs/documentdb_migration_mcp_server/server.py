# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""AWS Labs DocumentDB Migration MCP Server implementation for migrating data to AWS DocumentDB."""

import argparse
import os
import sys
from awslabs.documentdb_migration_mcp_server.full_load_tools import run_full_load, run_filtered_full_load
from awslabs.documentdb_migration_mcp_server.cdc_tools import run_cdc, get_resume_token
from awslabs.documentdb_migration_mcp_server.boundary_tools import generate_boundaries
from awslabs.documentdb_migration_mcp_server.index_tools import (
    dump_indexes, restore_indexes, show_compatibility_issues, show_compatible_indexes
)
from awslabs.documentdb_migration_mcp_server.migration_workflow import run_easy_migration
from awslabs.documentdb_migration_mcp_server.dms_buddy_tools import generate_dms_config
from loguru import logger
from mcp.server.fastmcp import FastMCP


# Create the FastMCP server
mcp = FastMCP(
    'awslabs.documentdb-migration-mcp-server',
    log_level="ERROR",
    instructions="""DocumentDB Migration MCP Server provides tools to migrate data to AWS DocumentDB.

    Usage pattern:
    1. For a complete end-to-end migration workflow, use the `runEasyMigration` tool
       - This tool combines index management and full load migration in a single workflow
       - It handles index compatibility checking, dumping, and restoring
       - It runs a full load migration with auto-generated boundaries
       - After migration is complete, you can use getResumeToken and runCDC tools for CDC
    
    2. For full load migrations, use the `runFullLoad` or `runFilteredFullLoad` tools
       - Boundaries will be auto-generated if not provided
    3. For CDC (Change Data Capture) migrations, use the `runCDC` tool
    4. To get a change stream resume token for CDC, use the `getResumeToken` tool
    5. To generate boundaries for segmenting collections, use the `generateBoundaries` tool
    6. For index management:
       - To dump indexes from a source database, use the `dumpIndexes` tool
       - To restore indexes to a target database, use the `restoreIndexes` tool
       - To check index compatibility with DocumentDB, use the `showIndexCompatibilityIssues` tool
       - To show compatible indexes, use the `showCompatibleIndexes` tool
    7. For AWS DMS (Database Migration Service) configuration:
       - To generate a CloudFormation template for DMS migration, use the `generateDMSConfig` tool
       - This tool analyzes your MongoDB/DocumentDB collections and provides optimized DMS settings
       - It generates a CloudFormation template and parameter file for deploying DMS resources
       - Required parameters (choose one approach):
         * Option 1: Provide source connection details directly
           - Either source_uri OR (source_host, source_port, source_username, source_password)
           - source_database: Name of the database to analyze and migrate
           - source_uri: MongoDB connection string for your source database (supports both mongodb:// and mongodb+srv:// protocols)
           
           Useful optional parameters to consider:
           - migration_type: Choose "full-load" for one-time migration, "cdc" for ongoing replication,
             or "full-load-and-cdc" for both (default)
           - collection_name_for_parallel_load: Specify a particular collection to optimize for parallel
             processing (useful for very large collections)
           - multi_az: Set to true for production workloads requiring high availability
           - vpc_id: Your AWS VPC ID where DMS will be deployed
           - subnet_ids: Comma-separated list of subnet IDs for DMS
           - target_uri: Connection string for your target DocumentDB cluster
           - target_database: Name of the target database (defaults to source database name)
           - target_certificate_arn: ARN of the SSL certificate for DocumentDB connections
           
         * Option 2: Provide a config_file path
           - config_file: Path to a configuration file containing all DMS parameters
           - If the file doesn't exist, a template will be created for you to edit
           - All parameters above can be specified in the config file


    Server Configuration:
    - The server requires access to the migration scripts in the scripts directory.""",
    dependencies=[
        'pydantic',
        'loguru',
        'pymongo',
        'boto3',
        'humanize',
    ],
)


# Register all tools

# Full Load tools
mcp.tool(name='runFullLoad')(run_full_load)
mcp.tool(name='runFilteredFullLoad')(run_filtered_full_load)

# CDC tools
mcp.tool(name='runCDC')(run_cdc)
mcp.tool(name='getResumeToken')(get_resume_token)

# Boundary tools
mcp.tool(name='generateBoundaries')(generate_boundaries)

# Index tools
mcp.tool(name='dumpIndexes')(dump_indexes)
mcp.tool(name='restoreIndexes')(restore_indexes)
mcp.tool(name='showIndexCompatibilityIssues')(show_compatibility_issues)
mcp.tool(name='showCompatibleIndexes')(show_compatible_indexes)

# Workflow tools
mcp.tool(name='runEasyMigration')(run_easy_migration)

# DMS tools
mcp.tool(name='generateDMSConfig')(generate_dms_config)


def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description='An AWS Labs Model Context Protocol (MCP) server for DocumentDB Migration'
    )
    parser.add_argument('--sse', action='store_true', help='Use SSE transport')
    parser.add_argument('--port', type=int, default=8889, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument(
        '--log-level',
        type=str,
        default='ERROR',
        choices=['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level',
    )
    parser.add_argument(
        '--scripts-dir',
        type=str,
        default=None,
        help='Directory containing the migration scripts (default: scripts subdirectory)',
    )
    parser.add_argument(
        '--aws-profile',
        type=str,
        default=None,
        help='AWS profile to use for AWS services including DocumentDB and CloudWatch',
    )
    parser.add_argument(
        '--aws-region',
        type=str,
        default=None,
        help='AWS region to use for AWS services including DocumentDB and CloudWatch',
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg),
        level=args.log_level,
        format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
    )

    logger.info(f'Starting DocumentDB Migration MCP Server on {args.host}:{args.port}')
    logger.info(f'Log level: {args.log_level}')

    # Set up scripts directory
    if args.scripts_dir:
        scripts_dir = args.scripts_dir
    else:
        scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    
    # Create scripts directory if it doesn't exist
    os.makedirs(scripts_dir, exist_ok=True)
    logger.info(f'Scripts directory: {scripts_dir}')

    # Set AWS profile and region if provided
    if args.aws_profile:
        os.environ['AWS_PROFILE'] = args.aws_profile
        logger.info(f'Using AWS profile: {args.aws_profile}')
    
    if args.aws_region:
        os.environ['AWS_REGION'] = args.aws_region
        logger.info(f'Using AWS region: {args.aws_region}')

    try:
        # Run server with appropriate transport
        if args.sse:
            mcp.settings.port = args.port
            mcp.settings.host = args.host
            mcp.run(transport='sse')
        else:
            mcp.settings.port = args.port
            mcp.settings.host = args.host
            mcp.run()
    except Exception as e:
        logger.critical(f'Failed to start server: {str(e)}')


if __name__ == '__main__':
    main()
