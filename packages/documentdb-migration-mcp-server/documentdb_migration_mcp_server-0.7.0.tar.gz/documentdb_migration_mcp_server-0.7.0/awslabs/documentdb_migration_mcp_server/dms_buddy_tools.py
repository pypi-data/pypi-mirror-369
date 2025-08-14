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

"""DMS Buddy tools for DocumentDB Migration MCP Server."""

import os
import sys
import time
import subprocess
import json
import tempfile
import configparser
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
from pydantic import Field
from loguru import logger


async def generate_dms_config(
    config_file: Annotated[
        Optional[str],
        Field(
            description='Path to a configuration file containing all DMS parameters. If provided, no other parameters are required.'
        ),
    ] = None,
    source_uri: Annotated[
        Optional[str],
        Field(
            description='Source URI in MongoDB Connection String format (e.g., mongodb://hostname:port/). Required if config_file is not provided.'
        ),
    ] = None,
    source_host: Annotated[
        Optional[str],
        Field(
            description='Source database host (e.g., mongodb.example.com). Can be used instead of source_uri.'
        ),
    ] = None,
    source_port: Annotated[
        Optional[str],
        Field(
            description='Source database port (default: 27017).'
        ),
    ] = "27017",
    source_database: Annotated[
        Optional[str],
        Field(
            description='Source database name to analyze. Required if config_file is not provided.'
        ),
    ] = None,
    source_username: Annotated[
        Optional[str],
        Field(
            description='Source database username. Required if authentication is enabled.'
        ),
    ] = None,
    source_password: Annotated[
        Optional[str],
        Field(
            description='Source database password. Required if authentication is enabled.'
        ),
    ] = None,
    vpc_id: Annotated[
        Optional[str],
        Field(
            description='VPC ID for DMS resources (e.g., vpc-12345678). If not provided, a placeholder will be used in the template, which you can replace later.'
        ),
    ] = "vpc-placeholder",
    subnet_ids: Annotated[
        Optional[str],
        Field(
            description='Comma-separated list of subnet IDs for DMS resources (e.g., subnet-12345678,subnet-87654321). If not provided, placeholders will be used in the template.'
        ),
    ] = "subnet-placeholder1,subnet-placeholder2",
    target_uri: Annotated[
        Optional[str],
        Field(
            description='Target DocumentDB URI in MongoDB Connection String format (e.g., mongodb://docdb-cluster.region.docdb.amazonaws.com:27017/). If not provided, individual target parameters will be used.'
        ),
    ] = None,
    target_host: Annotated[
        Optional[str],
        Field(
            description='Target DocumentDB host (e.g., docdb-cluster.region.docdb.amazonaws.com). If not provided, a placeholder will be used.'
        ),
    ] = None,
    target_port: Annotated[
        Optional[str],
        Field(
            description='Target DocumentDB port (default: 27017).'
        ),
    ] = "27017",
    target_database: Annotated[
        Optional[str],
        Field(
            description='Target database name where data will be migrated to. If not provided, the source database name will be used.'
        ),
    ] = None,
    target_username: Annotated[
        Optional[str],
        Field(
            description='Target DocumentDB username. If not provided, a placeholder will be used.'
        ),
    ] = None,
    target_password: Annotated[
        Optional[str],
        Field(
            description='Target DocumentDB password. If not provided, a placeholder will be used.'
        ),
    ] = None,
    target_certificate_arn: Annotated[
        Optional[str],
        Field(
            description='Target database SSL certificate ARN for DocumentDB connections (e.g., arn:aws:secretsmanager:region:account:secret:certificate). If not provided, a placeholder will be used.'
        ),
    ] = "arn:aws:secretsmanager:region:account:secret:placeholder",
    collection_name_for_parallel_load: Annotated[
        Optional[str],
        Field(
            description='Specific collection name to analyze and optimize for parallel load. If not provided, all collections with 10K+ documents will be analyzed and optimized.'
        ),
    ] = None,
    migration_type: Annotated[
        str,
        Field(
            description='Migration type: "full-load" (one-time copy), "cdc" (ongoing replication), or "full-load-and-cdc" (both). This determines how DMS will migrate your data.'
        ),
    ] = "full-load-and-cdc",
    monitor_time: Annotated[
        int,
        Field(
            description='Monitoring time in minutes for CDC analysis. Longer times provide more accurate change rate estimates but take longer to complete.'
        ),
    ] = 1,
    multi_az: Annotated[
        bool,
        Field(
            description='Whether to use Multi-AZ for DMS replication instance. Set to true for production workloads requiring high availability.'
        ),
    ] = False,
    security_group_ids: Annotated[
        Optional[str],
        Field(
            description='Comma-separated list of security group IDs for DMS resources (e.g., sg-12345678,sg-87654321). These security groups must allow connectivity to both source and target databases.'
        ),
    ] = None,
    stack_name: Annotated[
        str,
        Field(
            description='CloudFormation stack name for the DMS resources. This will be used when deploying the template.'
        ),
    ] = "DocumentDBMigration",
    verbose: Annotated[
        bool,
        Field(
            description='Enable verbose output for detailed logging and debugging information.'
        ),
    ] = False,
) -> Dict[str, Any]:
    """Generate AWS DMS CloudFormation template for DocumentDB migration.
    
    This tool analyzes your MongoDB/DocumentDB collections and provides optimized configuration 
    recommendations for AWS DMS migrations to Amazon DocumentDB. It generates a CloudFormation 
    template that can be used to deploy the AWS DMS resources.
    
    Required parameters (choose one approach):
    - Option 1: Provide source connection details directly
      * Either source_uri OR (source_host, source_port, source_username, source_password)
      * source_database: Name of the database to analyze and migrate
      
      Useful optional parameters to consider:
      * migration_type: Choose "full-load" for one-time migration, "cdc" for ongoing replication,
        or "full-load-and-cdc" for both (default)
      * collection_name_for_parallel_load: Specify a particular collection to optimize for parallel
        processing (useful for very large collections)
      * multi_az: Set to true for production workloads requiring high availability
      * vpc_id: Your AWS VPC ID where DMS will be deployed
      * subnet_ids: Comma-separated list of subnet IDs for DMS
      * target connection details: Either target_uri OR (target_host, target_port, target_username, target_password)
      * target_database: Name of the target database (defaults to source database name)
      * target_certificate_arn: ARN of the SSL certificate for DocumentDB connections
        
    - Option 2: Provide a config_file path
      * config_file: Path to a configuration file containing all DMS parameters
      * If the file doesn't exist, a template will be created for you to edit
      * All parameters above can be specified in the config file
    
    Returns:
        Dict[str, Any]: Status of the operation and paths to generated files
    """
    logger.info(f"Starting DMS Buddy configuration generation")
    
    # Build command
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "dms_buddy.py")
    
    # Check if config file is provided
    if config_file:
        # Create a temporary config file if it doesn't exist
        if not os.path.exists(config_file):
            logger.info(f"Creating template config file at {config_file}")
            with open(config_file, 'w') as f:
                f.write("""[DMS]
# Source database connection details
SourceDBHost = mongodb.example.com
SourceDBPort = 27017
SourceDatabase = mydb
SourceUsername = myuser
SourcePassword = mypassword

# Target database connection details
TargetHost = docdb.amazonaws.com
TargetPort = 27017
TargetDatabase = mydb
TargetUsername = admin
TargetPassword = password
TargetCertificateArn = arn:aws:secretsmanager:region:account:secret:certificate

# AWS resources
VpcId = vpc-12345678
SubnetIds = subnet-12345678,subnet-87654321
MultiAZ = false

# Migration settings
MigrationType = full-load-and-cdc
MonitorTime = 1
CollectionNameForParallelLoad = mycollection
""")
            
            # Return with instructions to edit the config file
            return {
                "success": False,
                "message": f"Template configuration file created at {config_file}. Please edit this file with your settings and run the tool again.",
                "config_file": config_file,
            }
        
        # Config file exists, use it directly with dms_buddy.py
        # We need to construct a source_uri for dms_buddy.py since it's a required parameter
        try:
            # Parse the config file
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'DMS' in parser:
                dms_section = parser['DMS']
                source_host = dms_section.get('SourceDBHost', '')
                source_port = dms_section.get('SourceDBPort', '27017')
                source_username = dms_section.get('SourceUsername', '')
                source_password = dms_section.get('SourcePassword', '')
                source_database = dms_section.get('SourceDatabase', '')
                
                # Construct source URI with TLS parameters for DocumentDB
                if source_username and source_password:
                    constructed_source_uri = f"mongodb://{source_username}:{source_password}@{source_host}:{source_port}/{source_database}?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"
                else:
                    constructed_source_uri = f"mongodb://{source_host}:{source_port}/{source_database}?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"
                
                logger.info(f"Constructed source URI: {constructed_source_uri}")
                
                cmd = [
                    "python3",
                    script_path,
                    "--source-uri", constructed_source_uri,
                    "--source-host", source_host,
                    "--source-port", source_port,
                    "--source-database", source_database,
                ]
                
                # Add source username and password
                if source_username:
                    cmd.extend(["--source-username", source_username])
                
                if source_password:
                    cmd.extend(["--source-password", source_password])
                
                # Add target parameters
                target_host = dms_section.get('TargetHost', '')
                target_port = dms_section.get('TargetPort', '27017')
                target_database = dms_section.get('TargetDatabase', source_database)
                target_username = dms_section.get('TargetUsername', '')
                target_password = dms_section.get('TargetPassword', '')
                target_certificate_arn = dms_section.get('TargetCertificateArn', '')
                
                if target_host:
                    cmd.extend(["--target-host", target_host])
                
                if target_port:
                    cmd.extend(["--target-port", target_port])
                
                if target_database:
                    cmd.extend(["--target-database", target_database])
                
                if target_username:
                    cmd.extend(["--target-username", target_username])
                
                if target_password:
                    cmd.extend(["--target-password", target_password])
                
                if target_certificate_arn:
                    cmd.extend(["--target-certificate-arn", target_certificate_arn])
                
                # Add AWS resource parameters
                vpc_id = dms_section.get('VpcId', '')
                subnet_ids = dms_section.get('SubnetIds', '')
                multi_az = dms_section.get('MultiAZ', 'false').lower() == 'true'
                
                if vpc_id:
                    cmd.extend(["--vpc-id", vpc_id])
                
                if subnet_ids:
                    cmd.extend(["--subnet-ids", subnet_ids])
                
                cmd.extend(["--multi-az", "true" if multi_az else "false"])
                
                # Add migration settings
                migration_type = dms_section.get('MigrationType', 'full-load-and-cdc')
                monitor_time = int(dms_section.get('MonitorTime', '1'))
                collection_name_for_parallel_load = dms_section.get('CollectionNameForParallelLoad', '')
                
                if migration_type:
                    cmd.extend(["--migration-type", migration_type])
                
                cmd.extend(["--monitor-time", str(monitor_time)])
                
                if collection_name_for_parallel_load:
                    cmd.extend(["--collection-name-for-parallel-load", collection_name_for_parallel_load])
            else:
                logger.error("No DMS section found in config file")
                return {
                    "success": False,
                    "message": "No DMS section found in config file",
                }
        except Exception as e:
            logger.error(f"Error reading config file: {str(e)}")
            return {
                "success": False,
                "message": f"Error reading config file: {str(e)}",
            }
    else:
        # Validate required parameters
        if not source_database:
            return {
                "success": False,
                "message": "Source database name is required. Provide it via source_database parameter.",
            }
        
        if not source_uri and not source_host:
            return {
                "success": False,
                "message": "Either source_uri or source_host must be provided.",
            }
        
        # Construct source_uri if not provided, with TLS parameters for DocumentDB
        if not source_uri and source_host:
            if source_username and source_password:
                source_uri = f"mongodb://{source_username}:{source_password}@{source_host}:{source_port}/{source_database}?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"
            else:
                source_uri = f"mongodb://{source_host}:{source_port}/{source_database}?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"
            
            logger.info(f"Direct parameters source URI: {source_uri}")
        # Extract individual parameters from source_uri if not provided
        elif source_uri and not source_host:
            source_host = extract_host_from_uri(source_uri)
            source_port = extract_port_from_uri(source_uri)
            source_username = extract_username_from_uri(source_uri)
            source_password = extract_password_from_uri(source_uri)
        
        # Use source_database as target_database if not provided
        if not target_database:
            target_database = source_database
            logger.info(f"Using source database '{source_database}' as target database")
        
        # Set default target parameters if not provided
        if not target_host:
            if target_uri:
                target_host = extract_host_from_uri(target_uri)
                target_port = extract_port_from_uri(target_uri)
                target_username = extract_username_from_uri(target_uri)
                target_password = extract_password_from_uri(target_uri)
            else:
                target_host = "target-docdb.cluster.region.docdb.amazonaws.com"
                target_port = "27017"
                target_username = "targetuser"
                target_password = "targetpassword"
        
        # Build command with all parameters
        cmd = [
            "python3",
            script_path,
            "--source-uri", source_uri,
            "--source-database", source_database,
        ]
        
        # Add source parameters
        if source_host:
            cmd.extend(["--source-host", source_host])
        
        if source_port:
            cmd.extend(["--source-port", source_port])
        
        if source_username:
            cmd.extend(["--source-username", source_username])
        
        if source_password:
            cmd.extend(["--source-password", source_password])
        
        # Add target parameters
        if target_host:
            cmd.extend(["--target-host", target_host])
        
        if target_port:
            cmd.extend(["--target-port", target_port])
        
        if target_database:
            cmd.extend(["--target-database", target_database])
        
        if target_username:
            cmd.extend(["--target-username", target_username])
        
        if target_password:
            cmd.extend(["--target-password", target_password])
        
        if target_certificate_arn:
            cmd.extend(["--target-certificate-arn", target_certificate_arn])
        
        # Add AWS resource parameters
        if vpc_id:
            cmd.extend(["--vpc-id", vpc_id])
        
        if subnet_ids:
            cmd.extend(["--subnet-ids", subnet_ids])
        
        cmd.extend(["--multi-az", "true" if multi_az else "false"])
        
        # Add migration settings
        if migration_type:
            cmd.extend(["--migration-type", migration_type])
        
        cmd.extend(["--monitor-time", str(monitor_time)])
        
        if collection_name_for_parallel_load:
            cmd.extend(["--collection-name-for-parallel-load", collection_name_for_parallel_load])
        
        if security_group_ids:
            cmd.extend(["--security-group-ids", security_group_ids])
    
    # Create a temporary directory for output files
    try:
        # Try to use a directory in the user's home directory
        output_dir = os.path.join(os.path.expanduser("~"), ".documentdb-migration", "dms_buddy")
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        # Fall back to a temporary directory if home directory is not accessible
        logger.warning(f"Could not create output directory in home directory: {str(e)}")
        output_dir = tempfile.mkdtemp(prefix="documentdb_migration_dms_buddy_")
        logger.info(f"Using temporary directory for output: {output_dir}")
    
    # Generate timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output_file = os.path.join(output_dir, f"dms_config_{timestamp}.json")
    
    if verbose:
        cmd.append("--verbose")
    
    # Execute command
    try:
        # Format command for logging
        formatted_cmd = []
        for c in cmd:
            if ' ' in c:
                formatted_cmd.append(f'"{c}"')
            else:
                formatted_cmd.append(c)
        logger.info(f"Executing command: {' '.join(formatted_cmd)}")
        
        # Create a log file for the output
        try:
            # Try to use a directory in the user's home directory
            log_dir = os.path.join(os.path.expanduser("~"), ".documentdb-migration", "logs")
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            # Fall back to a temporary directory if home directory is not accessible
            logger.warning(f"Could not create log directory in home directory: {str(e)}")
            log_dir = tempfile.mkdtemp(prefix="documentdb_migration_logs_")
            logger.info(f"Using temporary directory for logs: {log_dir}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_dir, f"dms_buddy_{timestamp}.log")
        
        logger.info(f"Logging output to: {log_file_path}")
        
        # Open the log file
        log_file = open(log_file_path, "w")
        
        # Start the process with stdout and stderr redirected to the log file
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for the process to complete
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"DMS Buddy failed with return code {process.returncode}")
            return {
                "success": False,
                "message": f"DMS Buddy failed with return code {process.returncode}. Check the log file for details.",
                "log_file": log_file_path,
            }
        
        # Copy the parameter.json file to the output file location
        parameter_json_path = os.path.join(os.getcwd(), "parameter.json")
        if os.path.exists(parameter_json_path):
            with open(parameter_json_path, 'r') as src_file:
                with open(final_output_file, 'w') as dst_file:
                    dst_file.write(src_file.read())
            # Remove the original parameter.json file
            os.remove(parameter_json_path)
        else:
            logger.warning(f"parameter.json file not found at {parameter_json_path}")
            return {
                "success": False,
                "message": f"DMS Buddy did not generate parameter.json file. Check the log file for details.",
                "log_file": log_file_path,
            }
        
        # Copy the CloudFormation template to the output directory
        cfn_template_path = os.path.join(os.path.dirname(__file__), "scripts", "dms_buddy.cfn")
        cfn_output_path = os.path.join(output_dir, f"dms_template_{timestamp}.cfn")
        
        with open(cfn_template_path, 'r') as src_file:
            with open(cfn_output_path, 'w') as dst_file:
                dst_file.write(src_file.read())
        
        # Return success with paths to generated files
        return {
            "success": True,
            "message": f"DMS configuration generated successfully",
            "parameter_file": final_output_file,
            "cloudformation_template": cfn_output_path,
            "log_file": log_file_path,
            "stack_name": stack_name,
            "deployment_command": f"aws cloudformation create-stack --stack-name {stack_name} --template-body file://{cfn_output_path} --parameters file://{final_output_file} --capabilities CAPABILITY_IAM",
        }
    except Exception as e:
        logger.error(f"Error generating DMS configuration: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to generate DMS configuration: {str(e)}",
            "log_file": log_file_path if 'log_file_path' in locals() else None,
        }


def extract_host_from_uri(uri):
    """Extract host from MongoDB URI."""
    if uri is None:
        return "target-docdb.cluster.region.docdb.amazonaws.com"
    
    try:
        # Remove the protocol part
        if uri.startswith('mongodb://'):
            uri = uri[len('mongodb://'):]
        elif uri.startswith('mongodb+srv://'):
            uri = uri[len('mongodb+srv://'):]
        
        # Remove auth part if present
        if '@' in uri:
            uri = uri.split('@', 1)[1]
        
        # Extract host
        if '/' in uri:
            host_port = uri.split('/', 1)[0]
        else:
            host_port = uri
        
        # Extract host from host:port
        if ':' in host_port:
            return host_port.split(':', 1)[0]
        else:
            return host_port
    except Exception as e:
        logger.warning(f"Error extracting host from URI: {str(e)}")
        return "target-docdb.cluster.region.docdb.amazonaws.com"


def extract_port_from_uri(uri):
    """Extract port from MongoDB URI."""
    if uri is None:
        return "27017"
    
    try:
        # Remove the protocol part
        if uri.startswith('mongodb://'):
            uri = uri[len('mongodb://'):]
        elif uri.startswith('mongodb+srv://'):
            uri = uri[len('mongodb+srv://'):]
            return "27017"  # mongodb+srv always uses port 27017
        
        # Remove auth part if present
        if '@' in uri:
            uri = uri.split('@', 1)[1]
        
        # Extract host:port
        if '/' in uri:
            host_port = uri.split('/', 1)[0]
        else:
            host_port = uri
        
        # Extract port from host:port
        if ':' in host_port:
            return host_port.split(':', 1)[1]
        else:
            return "27017"  # Default MongoDB port
    except Exception as e:
        logger.warning(f"Error extracting port from URI: {str(e)}")
        return "27017"


def extract_username_from_uri(uri):
    """Extract username from MongoDB URI."""
    if uri is None:
        return "targetuser"
    
    try:
        # Check if URI has auth part
        if not uri.startswith('mongodb://') and not uri.startswith('mongodb+srv://'):
            return "targetuser"
        
        # Remove the protocol part
        if uri.startswith('mongodb://'):
            uri = uri[len('mongodb://'):]
        elif uri.startswith('mongodb+srv://'):
            uri = uri[len('mongodb+srv://'):]
        
        # Check if auth part exists
        if '@' not in uri:
            return "targetuser"
        
        # Extract auth part
        auth = uri.split('@', 1)[0]
        
        # Extract username from auth
        if ':' in auth:
            return auth.split(':', 1)[0]
        else:
            return auth
    except Exception as e:
        logger.warning(f"Error extracting username from URI: {str(e)}")
        return "targetuser"


def extract_password_from_uri(uri):
    """Extract password from MongoDB URI."""
    if uri is None:
        return "targetpassword"
    
    try:
        # Check if URI has auth part
        if not uri.startswith('mongodb://') and not uri.startswith('mongodb+srv://'):
            return "targetpassword"
        
        # Remove the protocol part
        if uri.startswith('mongodb://'):
            uri = uri[len('mongodb://'):]
        elif uri.startswith('mongodb+srv://'):
            uri = uri[len('mongodb+srv://'):]
        
        # Check if auth part exists
        if '@' not in uri:
            return "targetpassword"
        
        # Extract auth part
        auth = uri.split('@', 1)[0]
        
        # Extract password from auth
        if ':' in auth:
            return auth.split(':', 1)[1]
        else:
            return "targetpassword"
    except Exception as e:
        logger.warning(f"Error extracting password from URI: {str(e)}")
        return "targetpassword"
