# DocumentDB Migration MCP Server

This MCP (Model Context Protocol) server provides tools for migrating data to DocumentDB. It wraps the existing DocumentDB migration tools into an MCP server interface, making them accessible through the MCP protocol.

## Features

- **Easy Migration Workflow**: Complete end-to-end migration workflow that combines index management and full load migration
- **Full Load Migration**: Migrate data from a source database to DocumentDB in a one-time operation
- **Filtered Full Load Migration**: Migrate data with filtering based on TTL
- **Change Data Capture (CDC)**: Continuously replicate changes from a source database to DocumentDB
- **Resume Token Management**: Get change stream resume tokens for CDC operations
- **Automatic Boundary Generation**: Automatically generate optimal boundaries for segmenting collections during migration
- **Index Management**: Export, restore, and check compatibility of indexes between MongoDB and DocumentDB
- **DMS Configuration Generator**: Generate optimized AWS DMS CloudFormation templates for DocumentDB migrations

## Installation

```bash
uvx documentdb-migration-mcp-server@latest
```

## MCP Server Configuration

Add the MCP server to your favorite agentic tools (e.g., for Amazon Q Developer CLI MCP, Claude, etc.) using the following configuration:

```json
{
  "documentdb-migration-mcp-server": {
    "autoApprove": [
      "runEasyMigration",
      "runFullLoad",
      "runFilteredFullLoad",
      "runCDC",
      "getResumeToken",
      "generateBoundaries",
      "dumpIndexes",
      "restoreIndexes",
      "showIndexCompatibilityIssues",
      "showCompatibleIndexes",
      "generateDMSConfig"
    ],
    "disabled": false,
    "timeout": 60,
    "command": "uvx",
    "args": [
      "documentdb-migration-mcp-server@latest"
    ],
    "env": {
      "FASTMCP_LOG_LEVEL": "ERROR",
      "AWS_PROFILE": "default",
      "AWS_REGION": "us-east-1"
    },
    "transportType": "stdio"
  }
}
```

You can customize the AWS profile and region by changing the `AWS_PROFILE` and `AWS_REGION` environment variables.

## MCP Tools

### runEasyMigration

Run a complete end-to-end migration workflow from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `max_inserts_per_batch`: (Optional) Maximum number of inserts to include in a single batch, defaults to 100
- `feedback_seconds`: (Optional) Number of seconds between feedback output, defaults to 60
- `dry_run`: (Optional) Read source changes only, do not apply to target, defaults to false
- `verbose`: (Optional) Enable verbose logging, defaults to false
- `create_cloudwatch_metrics`: (Optional) Create CloudWatch metrics for monitoring, defaults to false
- `cluster_name`: (Optional) Name of cluster for CloudWatch metrics
- `skip_incompatible_indexes`: (Optional) Skip incompatible indexes when restoring metadata, defaults to true
- `support_2dsphere`: (Optional) Support 2dsphere indexes creation, defaults to false
- `skip_id_indexes`: (Optional) Do not create _id indexes, defaults to true

### runFullLoad

Run a full load migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `boundaries`: (Optional) Comma-separated list of boundaries for segmenting. If not provided, boundaries will be auto-generated.
- `boundary_datatype`: (Optional) Datatype of boundaries (objectid, string, int). Auto-detected if boundaries are auto-generated.
- `max_inserts_per_batch`: Maximum number of inserts to include in a single batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging
- `create_cloudwatch_metrics`: Create CloudWatch metrics for monitoring
- `cluster_name`: Name of cluster for CloudWatch metrics

### runFilteredFullLoad

Run a filtered full load migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `boundaries`: (Optional) Comma-separated list of boundaries for segmenting. If not provided, boundaries will be auto-generated.
- `boundary_datatype`: (Optional) Datatype of boundaries (objectid, string, int). Auto-detected if boundaries are auto-generated.
- `max_inserts_per_batch`: Maximum number of inserts to include in a single batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging

### runCDC

Run a CDC (Change Data Capture) migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `start_position`: Starting position - 0 for all available changes, YYYY-MM-DD+HH:MM:SS in UTC, or change stream resume token
- `use_oplog`: Use the oplog as change data capture source (MongoDB only)
- `use_change_stream`: Use change streams as change data capture source (MongoDB or DocumentDB)
- `threads`: Number of threads (parallel processing)
- `duration_seconds`: Number of seconds to run before exiting, 0 = run forever
- `max_operations_per_batch`: Maximum number of operations to include in a single batch
- `max_seconds_between_batches`: Maximum number of seconds to await full batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging
- `create_cloudwatch_metrics`: Create CloudWatch metrics for monitoring
- `cluster_name`: Name of cluster for CloudWatch metrics

### getResumeToken

Get the current change stream resume token.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>

### generateBoundaries

Generate boundaries for segmenting a collection during migration.

**Parameters:**
- `uri`: MongoDB Connection String format URI
- `database`: Database name
- `collection`: Collection name
- `num_segments`: Number of segments to divide the collection into
- `use_single_cursor`: (Optional) Use a single cursor to scan the collection (slower but more reliable), defaults to false

### dumpIndexes

Dump indexes from a MongoDB or DocumentDB instance.

**Parameters:**
- `uri`: URI to connect to MongoDB or Amazon DocumentDB
- `output_dir`: (Optional) Directory to export indexes to. If not provided, a temporary directory will be created.
- `dry_run`: (Optional) Perform processing, but do not actually export indexes
- `debug`: (Optional) Output debugging information

### restoreIndexes

Restore indexes to an Amazon DocumentDB instance.

**Parameters:**
- `uri`: URI to connect to Amazon DocumentDB
- `index_dir`: Directory containing index metadata to restore from
- `skip_incompatible`: (Optional) Skip incompatible indexes when restoring metadata, defaults to true
- `support_2dsphere`: (Optional) Support 2dsphere indexes creation, defaults to false
- `dry_run`: (Optional) Perform processing, but do not actually restore indexes
- `debug`: (Optional) Output debugging information
- `shorten_index_name`: (Optional) Shorten long index name to compatible length, defaults to true
- `skip_id_indexes`: (Optional) Do not create _id indexes, defaults to true

### showIndexCompatibilityIssues

Show compatibility issues with Amazon DocumentDB.

**Parameters:**
- `index_dir`: Directory containing index metadata to check
- `debug`: (Optional) Output debugging information

### showCompatibleIndexes

Show compatible indexes with Amazon DocumentDB.

**Parameters:**
- `index_dir`: Directory containing index metadata to check
- `debug`: (Optional) Output debugging information

### generateDMSConfig

Generate AWS DMS CloudFormation template for DocumentDB migration.

**Parameters:**
- `config_file`: (Optional) Path to a configuration file containing all DMS parameters. If provided, no other parameters are required.
- `source_uri`: (Optional) Source URI in MongoDB Connection String format (supports both mongodb:// and mongodb+srv:// protocols)
- `source_host`: (Optional) Source database host (e.g., mongodb.example.com). Can be used instead of source_uri.
- `source_port`: (Optional) Source database port (default: 27017).
- `source_database`: (Optional) Source database name to analyze. Required if config_file is not provided.
- `source_username`: (Optional) Source database username. Required if authentication is enabled.
- `source_password`: (Optional) Source database password. Required if authentication is enabled.
- `vpc_id`: (Optional) VPC ID for DMS resources (e.g., vpc-12345678). If not provided, a placeholder will be used in the template.
- `subnet_ids`: (Optional) Comma-separated list of subnet IDs for DMS resources.
- `target_uri`: (Optional) Target DocumentDB URI in MongoDB Connection String format.
- `target_host`: (Optional) Target DocumentDB host. If not provided, a placeholder will be used.
- `target_port`: (Optional) Target DocumentDB port (default: 27017).
- `target_database`: (Optional) Target database name. If not provided, the source database name will be used.
- `target_username`: (Optional) Target DocumentDB username. If not provided, a placeholder will be used.
- `target_password`: (Optional) Target DocumentDB password. If not provided, a placeholder will be used.
- `target_certificate_arn`: (Optional) Target database SSL certificate ARN for DocumentDB connections.
- `collection_name_for_parallel_load`: (Optional) Collection name to analyze and optimize for parallel load.
- `migration_type`: (Optional) Migration type: full-load, cdc, or full-load-and-cdc (default: full-load-and-cdc)
- `monitor_time`: (Optional) Monitoring time in minutes for CDC analysis (default: 1)
- `multi_az`: (Optional) Whether to use Multi-AZ for DMS replication instance (default: false)
- `security_group_ids`: (Optional) Comma-separated list of security group IDs for DMS resources
- `stack_name`: (Optional) CloudFormation stack name (default: DocumentDBMigration)
- `verbose`: (Optional) Enable verbose output (default: false)

## Requirements

- Python 3.10+
- PyMongo
- Boto3 (for CloudWatch metrics)
- Humanize (for DMS Buddy)
- MCP Server

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
