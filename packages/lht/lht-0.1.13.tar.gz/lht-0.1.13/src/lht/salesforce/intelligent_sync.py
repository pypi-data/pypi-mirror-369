import pandas as pd
import time
import requests
import numpy as np
import logging
from typing import Optional, Dict, Any, Tuple
from . import query_bapi20, sobjects, sobject_query
from lht.util import merge, field_types, data_writer

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global debug flag - can be set by applications using the package
SQL_DEBUG_MODE = False

def set_sql_debug_mode(debug: bool):
    """Set global SQL debug mode for all SQL operations."""
    global SQL_DEBUG_MODE
    SQL_DEBUG_MODE = debug
    if debug:
        print("🔍 SQL Debug Mode: ENABLED")
    else:
        print("🔍 SQL Debug Mode: DISABLED")

def get_sql_debug_mode() -> bool:
    """Get current SQL debug mode setting."""
    return SQL_DEBUG_MODE


def sql_execution(session, query, context="", debug=None):
    """SQL execution with optional debug output."""
    # Use global flag if debug not specified
    if debug is None:
        debug = SQL_DEBUG_MODE
    
    if debug:
        # Full debug output
        print(f"\n{'='*80}")
        print(f"🔍 EXECUTING SQL [{context}]:")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        # Check for common issues
        if not query or query.strip() == "":
            print(f"❌ ERROR: Empty SQL query in {context}")
            return None
        
        if query.strip().upper().startswith('FROM'):
            print(f"❌ ERROR: SQL query starts with FROM in {context}: {query}")
            return None
        
        # Additional checks for malformed queries
        query_upper = query.strip().upper()
        if query_upper.startswith('FROM ') or query_upper.startswith('FROM\n') or query_upper.startswith('FROM\t'):
            print(f"❌ ERROR: SQL query starts with FROM in {context}: {query}")
            print(f"❌ Query length: {len(query)}")
            print(f"❌ Query stripped: '{query.strip()}'")
            return None
        
        try:
            print(f"🚀 Executing query...")
            result = session.sql(query).collect()
            print(f"✅ SUCCESS: {len(result)} rows returned")
            print(f"Result: {result}")
            return result
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print(f"❌ Query was: {query}")
            print(f"❌ Query type: {type(query)}")
            print(f"❌ Query length: {len(query)}")
            print(f"❌ Query stripped: '{query.strip()}'")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    else:
        # Silent execution with minimal error info
        try:
            return session.sql(query).collect()
        except Exception as e:
            print(f"❌ SQL Error in {context}: {e}")
            raise

# Keep the old function name for backward compatibility
def debug_sql_execution(session, query, context=""):
    """Backward compatibility wrapper for debug_sql_execution."""
    return sql_execution(session, query, context, debug=True)


class IntelligentSync:
    """
    Intelligent synchronization system that determines the best method to sync Salesforce data
    based on volume and previous sync status.
    """
    
    def __init__(self, session, access_info: Dict[str, str]):
        """
        Initialize the intelligent sync system.
        
        Args:
            session: Snowflake Snowpark session
            access_info: Dictionary containing Salesforce access details
        """
        self.session = session
        self.access_info = access_info
        
        # Configuration thresholds
        self.BULK_API_THRESHOLD = 10000  # Use Bulk API for records >= this number
        self.REGULAR_API_THRESHOLD = 1000  # Use regular API for records < this number
        self.STAGE_THRESHOLD = 50000  # Use stage for records >= this number
        
    def sync_sobject(self, 
                    sobject: str, 
                    schema: str, 
                    table: str, 
                    match_field: str = 'ID',
                    use_stage: bool = False,
                    stage_name: Optional[str] = None,
                    force_full_sync: bool = False) -> Dict[str, Any]:
        """
        Intelligently sync a Salesforce SObject to Snowflake.
        
        Args:
            sobject: Salesforce SObject name (e.g., 'Account', 'Contact')
            schema: Snowflake schema name
            table: Snowflake table name
            match_field: Field to use for matching records (default: 'ID')
            use_stage: Whether to use Snowflake stage for large datasets
            stage_name: Snowflake stage name (required if use_stage=True)
            force_full_sync: Force a full sync regardless of previous sync status
            
        Returns:
            Dictionary containing sync results and metadata
        """
        logger.debug(f"🔄 Starting intelligent sync for {sobject} -> {schema}.{table}")
        print(f"🔄 Starting intelligent sync for {sobject} -> {schema}.{table}")
        
        # Ensure schema exists before proceeding
        logger.debug(f"🔍 Ensuring schema {schema} exists...")
        if not self._ensure_schema_exists(schema):
            error_msg = f"Failed to ensure schema {schema} exists"
            logger.error(f"❌ {error_msg}")
            return {
                'sobject': sobject,
                'target_table': f"{schema}.{table}",
                'sync_method': 'failed',
                'estimated_records': 0,
                'actual_records': 0,
                'sync_duration_seconds': 0,
                'last_modified_date': None,
                'sync_timestamp': pd.Timestamp.now(),
                'success': False,
                'error': error_msg
            }
        
        # Check if table exists and get sync status
        logger.debug(f"🔍 Checking if table {schema}.{table} exists...")
        print(f"🔍 Checking if table {schema}.{table} exists...")
        table_exists = self._table_exists(schema, table)
        print(f"📋 Table exists: {table_exists}")
        last_modified_date = None
        
        if table_exists and not force_full_sync:
            logger.debug("🔍 Getting last modified date for incremental sync...")
            print("🔍 Getting last modified date for incremental sync...")
            last_modified_date = self._get_last_modified_date(schema, table)
            print(f"📅 Last sync date: {last_modified_date}")
            
            # Debug: Check why incremental sync might be failing
            if last_modified_date is None:
                print(f"⚠️ WARNING: last_modified_date is None - this will force a FULL sync!")
                print(f"⚠️ Check if the table has LASTMODIFIEDDATE field or if the query is failing")
        else:
            print(f"📋 Skipping last modified date check - table_exists: {table_exists}, force_full_sync: {force_full_sync}")
        
        # Determine sync strategy
        logger.debug("🎯 Determining sync strategy...")
        print("🎯 Determining sync strategy...")
        sync_strategy = self._determine_sync_strategy(
            sobject, table_exists, last_modified_date, use_stage, stage_name
        )
        
        logger.debug(f"🎯 Sync strategy determined: {sync_strategy}")
        print(f"🎯 Sync strategy: {sync_strategy['method']}")
        print(f"📊 Estimated records: {sync_strategy['estimated_records']}")
        
        # Execute sync based on strategy
        start_time = time.time()
        result = self._execute_sync_strategy(sync_strategy, sobject, schema, table, match_field)
        end_time = time.time()
        
        # Compile results
        sync_result = {
            'sobject': sobject,
            'target_table': f"{schema}.{table}",
            'sync_method': sync_strategy['method'],
            'estimated_records': sync_strategy['estimated_records'],
            'actual_records': result.get('records_processed', 0),
            'sync_duration_seconds': end_time - start_time,
            'last_modified_date': last_modified_date,
            'sync_timestamp': pd.Timestamp.now(),
            'success': result.get('success', False),
            'error': result.get('error', None)
        }
        
        print(f"✅ Sync completed: {sync_result['actual_records']} records in {sync_result['sync_duration_seconds']:.2f}s")
        return sync_result
    
    def _table_exists(self, schema: str, table: str) -> bool:
        """Check if the target table exists in Snowflake."""
        try:
            # First check if schema exists
            schema_query = f"SHOW SCHEMAS LIKE '{schema}'"
            logger.debug(f"🔍 Checking if schema exists: {schema_query}")
            print(f"🔍 Checking if schema exists: {schema_query}")
            schema_result = debug_sql_execution(self.session, schema_query, "schema_check")
            print(f"📋 Schema result: {schema_result}")
            if not schema_result or len(schema_result) == 0:
                logger.debug(f"📋 Schema {schema} does not exist")
                print(f"📋 Schema {schema} does not exist")
                return False
            
            # Then check if table exists in schema - use more specific query
            current_db = self.session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
            query = f"SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}' AND table_type = 'BASE TABLE'"
            logger.debug(f"🔍 Executing table existence check: {query}")
            print(f"🔍 Executing table existence check: {query}")
            result = debug_sql_execution(self.session, query, "table_check")
            print(f"📋 Table result: {result}")
            
            # More robust result checking
            if result is not None and len(result) > 0:
                # Check if result has the expected structure
                if 'table_count' in result[0]:
                    exists = result[0]['table_count'] > 0
                else:
                    # Fallback: check if any result was returned
                    exists = len(result) > 0
            else:
                exists = False
                
            logger.debug(f"📋 Table {schema}.{table} exists: {exists}")
            print(f"📋 Table {schema}.{table} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"❌ Error checking table existence: {e}")
            print(f"❌ Error checking table existence: {e}")
            return False
    
    def _ensure_schema_exists(self, schema: str) -> bool:
        """Ensure the schema exists in Snowflake, create it if it doesn't."""
        try:
            schema_query = f"SHOW SCHEMAS LIKE '{schema}'"
            logger.debug(f"🔍 Checking if schema exists: {schema_query}")
            schema_result = debug_sql_execution(self.session, schema_query, "schema_exists_check")
            
            if not schema_result or len(schema_result) == 0:
                logger.debug(f"📋 Schema {schema} does not exist, creating it...")
                create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema}"
                logger.debug(f"🔍 Creating schema: {create_schema_query}")
                debug_sql_execution(self.session, create_schema_query, "create_schema")
                logger.debug(f"✅ Schema {schema} created successfully")
                return True
            else:
                logger.debug(f"📋 Schema {schema} already exists")
                return True
        except Exception as e:
            logger.error(f"❌ Error ensuring schema exists: {e}")
            return False
    
    def _get_last_modified_date(self, schema: str, table: str) -> Optional[pd.Timestamp]:
        """Get the most recent LastModifiedDate from the target table."""
        print(f"🔍 DEBUG: _get_last_modified_date called with schema='{schema}', table='{table}'")
        try:
            # Double-check that table exists before querying
            print(f"🔍 DEBUG: Checking if table {schema}.{table} exists...")
            if not self._table_exists(schema, table):
                logger.debug(f"📋 Table {schema}.{table} does not exist, skipping last modified date check")
                print(f"🔍 DEBUG: Table {schema}.{table} does not exist")
                return None
            else:
                print(f"🔍 DEBUG: Table {schema}.{table} exists, proceeding with query")
            
            # Get current database for fully qualified table name
            current_db = self.session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
            
            # Try a more robust approach to get the last modified date
            try:
                # First, try to get the last modified date with error handling
                query = f"SELECT MAX(TRY_CAST(LASTMODIFIEDDATE AS TIMESTAMP_NTZ)) as LAST_MODIFIED FROM {current_db}.{schema}.{table}"
                logger.debug(f"🔍 Executing last modified date query: {query}")
                print(f"🔍 Executing SQL: {query}")
                
                result = debug_sql_execution(self.session, query, "last_modified_date")
                logger.debug(f"📋 Query result: {result}")
                print(f"🔍 DEBUG: Query result type: {type(result)}")
                print(f"🔍 DEBUG: Query result length: {len(result) if result else 'None'}")
                
                if result and len(result) > 0:
                    print(f"🔍 DEBUG: First result item type: {type(result[0])}")
                    print(f"🔍 DEBUG: First result item: {result[0]}")
                    print(f"🔍 DEBUG: First result item dir: {dir(result[0])}")
                    
                    # Handle Snowflake Row objects properly
                    row = result[0]
                    print(f"🔍 DEBUG: Row object type: {type(row)}")
                    print(f"🔍 DEBUG: Row object attributes: {[attr for attr in dir(row) if not attr.startswith('_')]}")
                    
                    if hasattr(row, 'LAST_MODIFIED') and row.LAST_MODIFIED:
                        print(f"🔍 DEBUG: Found LAST_MODIFIED attribute: {row.LAST_MODIFIED}")
                        last_modified = pd.to_datetime(row.LAST_MODIFIED)
                        logger.debug(f"📅 Last modified date: {last_modified}")
                        return last_modified
                    elif hasattr(row, '__getitem__'):
                        print(f"🔍 DEBUG: Row supports __getitem__, trying dictionary access")
                        # Fallback to dictionary-style access
                        try:
                            last_modified_value = row['LAST_MODIFIED']
                            print(f"🔍 DEBUG: Dictionary access successful: {last_modified_value}")
                            if last_modified_value:
                                last_modified = pd.to_datetime(last_modified_value)
                                logger.debug(f"📅 Last modified date: {last_modified}")
                                return last_modified
                        except (KeyError, TypeError) as e:
                            print(f"🔍 DEBUG: Dictionary access failed: {e}")
                            pass
                    
                    print(f"🔍 DEBUG: No valid LAST_MODIFIED found in row")
                else:
                    print(f"🔍 DEBUG: No results returned from query")
                    
            except Exception as e:
                logger.warning(f"⚠️ First attempt failed, trying alternative approach: {e}")
                print(f"⚠️ First attempt failed, trying alternative approach: {e}")
                
                try:
                    # Alternative: try to get the last modified date without casting
                    query = f"SELECT MAX(LASTMODIFIEDDATE) as LAST_MODIFIED FROM {current_db}.{schema}.{table}"
                    logger.debug(f"🔍 Executing alternative query: {query}")
                    print(f"🔍 Executing alternative query: {query}")
                    
                    result = debug_sql_execution(self.session, query, "last_modified_date_alt")
                    logger.debug(f"📋 Alternative query result: {result}")
                    print(f"🔍 DEBUG: Alternative query result type: {type(result)}")
                    print(f"🔍 DEBUG: Alternative query result length: {len(result) if result else 'None'}")
                    
                    if result and len(result) > 0:
                        print(f"🔍 DEBUG: Alternative first result item type: {type(result[0])}")
                        print(f"🔍 DEBUG: Alternative first result item: {result[0]}")
                        
                        # Handle Snowflake Row objects properly
                        row = result[0]
                        raw_value = None
                        
                        print(f"🔍 DEBUG: Alternative row object type: {type(row)}")
                        print(f"🔍 DEBUG: Alternative row object attributes: {[attr for attr in dir(row) if not attr.startswith('_')]}")
                        
                        if hasattr(row, 'LAST_MODIFIED') and row.LAST_MODIFIED:
                            raw_value = row.LAST_MODIFIED
                            print(f"🔍 DEBUG: Alternative found LAST_MODIFIED attribute: {raw_value}")
                        elif hasattr(row, '__getitem__'):
                            print(f"🔍 DEBUG: Alternative row supports __getitem__, trying dictionary access")
                            # Fallback to dictionary-style access
                            try:
                                raw_value = row['LAST_MODIFIED']
                                print(f"🔍 DEBUG: Alternative dictionary access successful: {raw_value}")
                            except (KeyError, TypeError) as e:
                                print(f"🔍 DEBUG: Alternative dictionary access failed: {e}")
                                pass
                        
                        if raw_value:
                            logger.debug(f"📅 Raw LAST_MODIFIED value: {raw_value} (type: {type(raw_value)})")
                        else:
                            print(f"🔍 DEBUG: Alternative no valid LAST_MODIFIED found in row")
                    else:
                        print(f"🔍 DEBUG: Alternative no results returned from query")
                        
                        if isinstance(raw_value, str):
                            # Handle Salesforce ISO 8601 format: 2023-09-08T02:00:39.000Z
                            logger.debug(f"📅 Processing Salesforce timestamp: {raw_value}")
                            
                            try:
                                # Let pandas handle the ISO 8601 format directly
                                last_modified = pd.to_datetime(raw_value, errors='coerce')
                                logger.debug(f"📅 Converted timestamp: {raw_value} -> {last_modified}")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to parse timestamp {raw_value}: {e}")
                                last_modified = None
                        else:
                            # Handle numeric dates (Unix timestamps)
                            # Try milliseconds first (Salesforce often uses millisecond timestamps)
                            try:
                                last_modified = pd.to_datetime(raw_value, unit='ms', errors='coerce')
                                logger.debug(f"📅 Converted from milliseconds: {raw_value} -> {last_modified}")
                            except:
                                # Fallback to seconds
                                last_modified = pd.to_datetime(raw_value, unit='s', errors='coerce')
                                logger.debug(f"📅 Converted from seconds: {raw_value} -> {last_modified}")
                        
                        if pd.notna(last_modified):
                            logger.debug(f"📅 Converted last modified date: {last_modified}")
                            return last_modified
                            
                except Exception as e2:
                    logger.warning(f"⚠️ Alternative approach also failed: {e2}")
                    print(f"⚠️ Alternative approach also failed: {e2}")
            
            logger.debug("📅 No valid last modified date found (table empty, no LASTMODIFIEDDATE field, or conversion failed)")
            print(f"📅 No valid last modified date found - will use full sync")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting last modified date: {e}")
            print(f"❌ SQL Error in _get_last_modified_date: {e}")
            return None
    
    def _determine_sync_strategy(self, 
                               sobject: str, 
                               table_exists: bool, 
                               last_modified_date: Optional[pd.Timestamp],
                               use_stage: bool,
                               stage_name: Optional[str]) -> Dict[str, Any]:
        """
        Determine the best synchronization strategy based on data volume and previous sync status.
        """
        
        logger.debug(f"🎯 Determining sync strategy for {sobject}")
        logger.debug(f"📋 Table exists: {table_exists}")
        logger.debug(f"📅 Last modified date: {last_modified_date}")
        logger.debug(f"📦 Use stage: {use_stage}")
        logger.debug(f"📦 Stage name: {stage_name}")
        logger.debug(f"📊 Thresholds - Bulk API: {self.BULK_API_THRESHOLD}, Stage: {self.STAGE_THRESHOLD}")
        
        # Get estimated record count
        estimated_records = self._estimate_record_count(sobject, last_modified_date)
        print(f"📊 Estimated records: {estimated_records}")
        
        # Determine sync method
        if not table_exists or last_modified_date is None:
            # First-time sync
            logger.debug("🆕 First-time sync detected")
            print("🆕 First-time sync detected")
            logger.debug(f"📊 Record count: {estimated_records}, Bulk API threshold: {self.BULK_API_THRESHOLD}")
            print(f"📊 Record count: {estimated_records}, Bulk API threshold: {self.BULK_API_THRESHOLD}")
            
            # Force Bulk API for large datasets (1M+ records)
            if estimated_records >= 1000000:
                method = "bulk_api_stage_full" if use_stage and stage_name else "bulk_api_full"
                logger.debug(f"📊 Forcing bulk API for large dataset (records: {estimated_records} >= 1,000,000)")
                print(f"📊 Forcing bulk API for large dataset (records: {estimated_records} >= 1,000,000)")
            elif estimated_records >= self.BULK_API_THRESHOLD:
                method = "bulk_api_full"
                logger.debug(f"📊 Using bulk API (records: {estimated_records} >= {self.BULK_API_THRESHOLD})")
                print(f"📊 Using bulk API (records: {estimated_records} >= {self.BULK_API_THRESHOLD})")
                if use_stage and stage_name and estimated_records >= self.STAGE_THRESHOLD:
                    method = "bulk_api_stage_full"
                    logger.debug(f"📦 Using stage-based bulk API (records: {estimated_records} >= {self.STAGE_THRESHOLD})")
                    print(f"📦 Using stage-based bulk API (records: {estimated_records} >= {self.STAGE_THRESHOLD})")
            else:
                method = "regular_api_full"
                logger.debug(f"📊 Using regular API (records: {estimated_records} < {self.BULK_API_THRESHOLD})")
                print(f"📊 Using regular API (records: {estimated_records} < {self.BULK_API_THRESHOLD})")
        else:
            # Incremental sync - prefer REST API for better performance with small changes
            logger.debug("🔄 Incremental sync detected")
            print("🔄 Incremental sync detected")
            
            # For incremental syncs, prefer REST API unless there are a very large number of changes
            if estimated_records >= 100000:  # Only use Bulk API for very large incremental changes
                method = "bulk_api_incremental"
                logger.debug(f"📊 Using bulk API incremental (large changes: {estimated_records} >= 100,000)")
                print(f"📊 Using bulk API incremental (large changes: {estimated_records} >= 100,000)")
                if use_stage and stage_name and estimated_records >= self.STAGE_THRESHOLD:
                    method = "bulk_api_stage_incremental"
                    logger.debug(f"📦 Using stage-based bulk API incremental (records: {estimated_records} >= {self.STAGE_THRESHOLD})")
                    print(f"📦 Using stage-based bulk API incremental (records: {estimated_records} >= {self.STAGE_THRESHOLD})")
            else:
                method = "regular_api_incremental"
                logger.debug(f"📊 Using regular API incremental (optimal for small changes: {estimated_records} < 100,000)")
                print(f"📊 Using regular API incremental (optimal for small changes: {estimated_records} < 100,000)")
        
        strategy = {
            'method': method,
            'estimated_records': estimated_records,
            'is_incremental': table_exists and last_modified_date is not None,
            'use_stage': use_stage and stage_name and estimated_records >= self.STAGE_THRESHOLD,
            'stage_name': stage_name if use_stage and stage_name and estimated_records >= self.STAGE_THRESHOLD else None
        }
        
        logger.debug(f"🎯 Final strategy: {strategy}")
        
        # Additional validation for first-time syncs
        if not table_exists and strategy['method'].startswith('regular_api'):
            logger.warning(f"⚠️ Warning: First-time sync with large dataset using regular API. This may be inefficient.")
            logger.warning(f"⚠️ Consider using Bulk API for datasets with {estimated_records} records.")
        
        return strategy
    
    def _estimate_record_count(self, sobject: str, last_modified_date: Optional[pd.Timestamp]) -> int:
        """Estimate the number of records to be synced."""
        try:
            # Build query to count records
            if last_modified_date:
                # Incremental sync - count records modified since last sync
                lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
                query = f"SELECT COUNT(Id) FROM {sobject} WHERE LastModifiedDate > {lmd_sf}"
            else:
                # Full sync - count all records
                query = f"SELECT COUNT(Id) FROM {sobject}"
            
            logger.debug(f"🔍 Executing record count query: {query}")
            print(f"🔍 Executing Salesforce record count query: {query}")
            
            # Use regular API for count (faster than Bulk API for counts)
            headers = {
                "Authorization": f"Bearer {self.access_info['access_token']}",
                "Content-Type": "application/json"
            }
            url = f"{self.access_info['instance_url']}/services/data/v58.0/query?q={query}"
            
            logger.debug(f"🌐 Making API request to: {url}")
            print(f"🌐 Making Salesforce API request to: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            print(f"📊 Salesforce API response: {result}")
            print(f"🔍 DEBUG: Response type: {type(result)}")
            print(f"🔍 DEBUG: Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Handle different response structures for COUNT queries
            if isinstance(result, dict):
                print(f"🔍 DEBUG: Response is a dictionary")
                # For COUNT queries, check records array first (totalSize is always 1 for COUNT queries)
                if 'records' in result and len(result['records']) > 0:
                    print(f"🔍 DEBUG: Found records array with {len(result['records'])} items")
                    first_record = result['records'][0]
                    print(f"🔍 DEBUG: First record type: {type(first_record)}")
                    print(f"🔍 DEBUG: First record: {first_record}")
                    print(f"🔍 DEBUG: First record keys: {list(first_record.keys()) if isinstance(first_record, dict) else 'Not a dict'}")
                    
                    # Try different possible field names for count
                    count_fields = ['expr0', 'count', 'COUNT', 'count__c', 'Id']
                    for field in count_fields:
                        if field in first_record:
                            count = first_record[field]
                            logger.debug(f"📊 Estimated record count from {field}: {count}")
                            print(f"📊 Estimated record count from {field}: {count}")
                            return count
                    
                    # If no expected field found, log the structure
                    logger.warning(f"📊 Unexpected record structure: {first_record}")
                    print(f"📊 Unexpected record structure: {first_record}")
                    print(f"📊 Available fields: {list(first_record.keys())}")
                
                # Fallback to totalSize (though this should not be used for COUNT queries)
                print(f"🔍 DEBUG: Checking totalSize fallback")
                if 'totalSize' in result:
                    print(f"🔍 DEBUG: totalSize found: {result['totalSize']}")
                    if 'records' in result and len(result['records']) > 0:
                        print(f"🔍 DEBUG: Checking records[0]['expr0']")
                        try:
                            if result['records'][0]['expr0'] > 0:
                                count = result['records'][0]['expr0']
                                logger.debug(f"📊 Estimated record count from totalSize: {count}")
                                print(f"📊 Estimated record count from totalSize: {count}")
                                return count
                        except (KeyError, IndexError, TypeError) as e:
                            print(f"🔍 DEBUG: Error accessing records[0]['expr0']: {e}")
                            print(f"🔍 DEBUG: records[0] type: {type(result['records'][0])}")
                            print(f"🔍 DEBUG: records[0] content: {result['records'][0]}")
                else:
                    print(f"🔍 DEBUG: No totalSize found in response")
            else:
                logger.warning(f"📊 Unexpected response type: {type(result)}")
                print(f"📊 Unexpected response type: {type(result)}")
                print(f"📊 Response: {result}")
                
                # Log all available keys for debugging
                logger.warning("📊 No count found in response, using conservative estimate")
                print("📊 No count found in response, using conservative estimate")
                print(f"📊 Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            return 1000 if last_modified_date else 100000
            
        except Exception as e:
            print(f"❌ Error estimating record count: {e}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            
            # Try to get more information about the response if available
            try:
                if 'response' in locals():
                    print(f"📊 Response status: {response.status_code}")
                    print(f"📊 Response headers: {dict(response.headers)}")
                    print(f"📊 Response content: {response.text[:500]}...")
                    
                    # Try to parse the response if possible
                    try:
                        if 'result' in locals():
                            logger.error(f"❌ Error in result: {result}")
                        else:
                            logger.error(f"❌ Response content: {response.text}")
                    except:
                        logger.error(f"❌ Could not log response content")
            except:
                pass
            
            # Return a conservative estimate
            estimate = 1000 if last_modified_date else 100000
            logger.debug(f"📊 Using conservative estimate: {estimate}")
            print(f"📊 Using conservative estimate: {estimate}")
            return estimate
    
    def _execute_sync_strategy(self, 
                             strategy: Dict[str, Any], 
                             sobject: str, 
                             schema: str, 
                             table: str,
                             match_field: str) -> Dict[str, Any]:
        """Execute the determined sync strategy."""
        
        method = strategy['method']
        print(f"🚀 Executing sync strategy: {method}")
        logger.debug(f"🚀 Executing sync strategy: {method}")
        
        try:
            if method.startswith('bulk_api'):
                print(f"📦 Using Bulk API sync method: {method}")
                print("{}- {} - {} - {}".format(sobject, schema, table, method))
                return self._execute_bulk_api_sync(strategy, sobject, schema, table)
            elif method.startswith('regular_api'):
                print(f"📡 Using Regular API sync method: {method}")
                return self._execute_regular_api_sync(strategy, sobject, schema, table, match_field)
            else:
                error_msg = f"Unknown sync method: {method}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Error executing sync strategy: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"🔍 DEBUG: Exception type: {type(e)}")
            print(f"🔍 DEBUG: Exception args: {e.args}")
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'error': str(e),
                'records_processed': 0
            }
    
    def _execute_bulk_api_sync(self, 
                              strategy: Dict[str, Any], 
                              sobject: str, 
                              schema: str, 
                              table: str) -> Dict[str, Any]:
        """Execute Bulk API 2.0 sync."""
        
        logger.debug(f"🚀 Starting Bulk API sync for {sobject}")
        
        # Get query string and field descriptions
        last_modified_date = None
        
        # Debug: Print the parameters being used
        print(f"🔍 DEBUG: Bulk API sync parameters:")
        print(f"  - sobject: {sobject}")
        print(f"  - schema: {schema}")
        print(f"  - table: {table}")
        print(f"  - strategy: {strategy}")
        
        if strategy['is_incremental']:
            print(f"🔍 DEBUG: Checking for incremental sync...")
            # Get the last modified date from the existing table
            last_modified_date = self._get_last_modified_date(schema, table)
            print(f"🔍 DEBUG: Last modified date result: {last_modified_date}")
            if last_modified_date:
                lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
                logger.debug(f"📅 Using last modified date for incremental sync: {lmd_sf}")
                print(f"🔍 DEBUG: Formatted last modified date: {lmd_sf}")
        
        logger.debug(f"🔍 Getting field descriptions for {sobject}")
        print(f"🔍 DEBUG: Getting field descriptions for sobject: {sobject}")
        try:
            query_string, df_fields = sobjects.describe(self.access_info, sobject, lmd_sf if last_modified_date else None)
            logger.debug(f"📋 Raw query string from sobjects.describe: {query_string}")
            logger.debug(f"📋 Field descriptions: {df_fields}")
            print(f"🔍 DEBUG: Query string: {query_string}")
            print(f"🔍 DEBUG: Field descriptions keys: {list(df_fields.keys()) if df_fields else 'None'}")
            
            # Debug: Check for problematic field names
            if df_fields:
                print(f"🔍 DEBUG: Checking for invalid field names...")
                print(f"🔍 DEBUG: Total fields returned: {len(df_fields)}")
                
                # Show all field names for debugging
                all_fields = list(df_fields.keys())
                print(f"🔍 DEBUG: All field names: {all_fields}")
                
                problematic_fields = []
                for field_name in df_fields.keys():
                    if 'LargeLanguageModel' in field_name or 'LargeLanguage' in field_name:
                        problematic_fields.append(field_name)
                        print(f"⚠️  WARNING: Found potentially problematic field: {field_name}")
                
                if problematic_fields:
                    print(f"🔍 DEBUG: Problematic fields found: {problematic_fields}")
                    print(f"🔍 DEBUG: These fields may not exist on the Knowledge__kav object")
                
                # Check if we're getting fields from the wrong object
                print(f"🔍 DEBUG: First few field names: {all_fields[:10]}")
                print(f"🔍 DEBUG: Last few field names: {all_fields[-10:]}")
                
                # Look for Knowledge-specific fields
                knowledge_fields = [f for f in all_fields if 'knowledge' in f.lower() or 'article' in f.lower()]
                print(f"🔍 DEBUG: Knowledge-related fields: {knowledge_fields}")
                
                # Filter out problematic fields that commonly cause issues
                print(f"🔍 DEBUG: Filtering out problematic fields...")
                fields_to_remove = []
                
                # Common problematic fields that might not exist on all objects
                problematic_field_patterns = [
                    'LargeLanguageModel',
                    'LargeLanguage',
                    'NextReviewDate',  # This was also in your error
                    'ArchivedDate',    # This might not exist on all Knowledge objects
                    'ArchivedById',    # This might not exist on all Knowledge objects
                    'ArticleArchivedDate',
                    'ArticleArchivedById',
                    'ArticleCaseAttachCount',
                    'ArticleCreatedById',
                    'ArticleCreatedDate',
                    'ArticleMasterLanguage',
                    'ArticleTotalViewCount',
                    'Center_Appointment__c',
                    'Center_Referral__c',
                    'Confluence_id__c',
                    'Definition__c',
                    'Physician_Referral__c',
                    'Protocol__c',
                    'Synonyms__c',
                    'CS_Link_Notes_Documentation__c',
                    'Contracted__c',
                    'KB_Knowledge_Article_Name_And_Link__c',
                    'Notes__c',
                    'Payment_For_Matching__c',
                    'Required_Verification__c',
                    'Salesforce_Notes_Documentation__c',
                    'Record_Type_Report__c',
                    'Verified__c',
                    'Email__c',
                    'Hours_of_Operation__c',
                    'Location__c',
                    'Phone_Fax_Numbers__c',
                    'Website__c'
                ]
                
                for field_name in all_fields:
                    for pattern in problematic_field_patterns:
                        if pattern in field_name:
                            fields_to_remove.append(field_name)
                            print(f"🔍 DEBUG: Marking field for removal: {field_name} (matches pattern: {pattern})")
                            break
                
                # Remove problematic fields from df_fields
                if fields_to_remove:
                    print(f"🔍 DEBUG: Removing {len(fields_to_remove)} problematic fields: {fields_to_remove}")
                    for field in fields_to_remove:
                        if field in df_fields:
                            del df_fields[field]
                            print(f"🔍 DEBUG: Removed field: {field}")
                    
                    print(f"🔍 DEBUG: Remaining fields after filtering: {len(df_fields)}")
                    print(f"🔍 DEBUG: Remaining field names: {list(df_fields.keys())}")
                    
                    # Rebuild the query string with only valid fields
                    print(f"🔍 DEBUG: Rebuilding query string with filtered fields...")
                    valid_fields = list(df_fields.keys())
                    if valid_fields:
                        # Build a clean SELECT statement with only valid fields
                        clean_query = f"SELECT {', '.join(valid_fields)} FROM {sobject}"
                        if last_modified_date:
                            clean_query += f" WHERE LastModifiedDate > {lmd_sf}"
                        
                        query_string = clean_query
                        print(f"🔍 DEBUG: New clean query string: {query_string}")
                    else:
                        print(f"🔍 DEBUG: No valid fields remaining after filtering!")
                else:
                    print(f"🔍 DEBUG: No problematic fields found, keeping all fields")
            
            if not query_string or not df_fields:
                error_msg = f"Failed to get field descriptions for {sobject}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error getting field descriptions for {sobject}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Convert query string to proper SOQL
        soql_query = query_string.replace('+', ' ').replace('select', 'SELECT').replace('from', 'FROM')
        if last_modified_date:
            soql_query = soql_query.replace('where', 'WHERE').replace('LastModifiedDate>', 'LastModifiedDate > ')
        
        logger.debug(f"🔍 Final SOQL query: {soql_query}")
        print(f"🔍 Executing Bulk API query: {soql_query}")
        
        # Create bulk query job
        logger.debug("📋 Creating Bulk API job...")
        job_response = query_bapi20.create_batch_query(self.access_info, soql_query)
        
        # Debug: Print the full job_response
        print(f"🔍 DEBUG: job_response type: {type(job_response)}")
        print(f"🔍 DEBUG: job_response content: {job_response}")
        print(f"🔍 DEBUG: job_response keys: {list(job_response.keys()) if isinstance(job_response, dict) else 'Not a dict'}")
        
        # Check if job_response indicates an error
        if isinstance(job_response, list) and len(job_response) > 0:
            # This is an error response
            error_info = job_response[0]
            error_message = error_info.get('message', 'Unknown error')
            error_code = error_info.get('errorCode', 'UNKNOWN_ERROR')
            
            print(f"❌ Bulk API job creation failed:")
            print(f"  - Error Code: {error_code}")
            print(f"  - Error Message: {error_message}")
            
            raise Exception(f"Bulk API job creation failed: {error_code} - {error_message}")
        
        # Check if job_response is a valid success response
        if not isinstance(job_response, dict) or 'id' not in job_response:
            print(f"❌ Unexpected job_response format: {type(job_response)}")
            print(f"❌ Expected dict with 'id' key, got: {job_response}")
            raise Exception(f"Invalid job_response format: expected dict with 'id' key, got {type(job_response)}")
        
        job_id = job_response['id']
        
        logger.debug(f"📋 Created Bulk API job: {job_id}")
        print(f"📋 Created Bulk API job: {job_id}")
        
        # Monitor job status
        logger.debug("📊 Monitoring job status...")
        while True:
            status_response = query_bapi20.query_status(self.access_info, 'QueryAll', job_id)
            if isinstance(status_response, list) and len(status_response) > 0:
                job_status = status_response[0]
            else:
                job_status = status_response
            
            state = job_status['state']
            logger.debug(f"📊 Job status: {state}")
            print(f"📊 Job status: {state}")
            
            if state == 'JobComplete':
                break
            elif state in ['Failed', 'Aborted']:
                error_msg = f"Bulk API job failed with state: {state}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            time.sleep(10)
        
        # Get results
        use_stage = strategy.get('use_stage', False)
        stage_name = strategy.get('stage_name')
        
        logger.debug(f"📥 Getting results (optimized direct loading)")
        
        # Use optimized direct loading for all cases (stage parameters are deprecated)
        result = query_bapi20.get_bulk_results(
            self.session, self.access_info, job_id, sobject, schema, table,
            use_stage=use_stage, stage_name=stage_name
        )
        
        # Clean up job
        try:
            logger.debug(f"🧹 Cleaning up job: {job_id}")
            cleanup_result = query_bapi20.delete_specific_job(self.access_info, job_id)
            if cleanup_result.get('success'):
                print(f"🧹 Cleaned up job: {job_id}")
            else:
                logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {cleanup_result.get('error', 'Unknown error')}")
                print(f"⚠️ Warning: Could not clean up job {job_id}: {cleanup_result.get('error', 'Unknown error')}")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {e}")
            print(f"⚠️ Warning: Could not clean up job {job_id}: {e}")
        
        return {
            'success': True,
            'records_processed': strategy['estimated_records'],
            'job_id': job_id
        }
    
    def cleanup_old_jobs(self, max_age_hours=24):
        """Clean up old completed Bulk API 2.0 jobs from Salesforce.
        
        Args:
            max_age_hours (int): Maximum age in hours for jobs to be kept. 
                Jobs older than this will be deleted. Default is 24 hours.
        
        Returns:
            dict: Summary of cleanup operation.
        """
        logger.debug(f"🧹 Starting cleanup of jobs older than {max_age_hours} hours")
        print(f"🧹 Starting cleanup of jobs older than {max_age_hours} hours")
        
        try:
            from . import query_bapi20
            cleanup_result = query_bapi20.cleanup_completed_jobs(self.access_info, max_age_hours)
            
            logger.debug(f"🧹 Cleanup result: {cleanup_result}")
            return cleanup_result
            
        except Exception as e:
            error_msg = f"Error during job cleanup: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return {
                'deleted_count': 0,
                'failed_count': 0,
                'total_processed': 0,
                'error': str(e)
            }
    
    def _execute_regular_api_sync(self, 
                                 strategy: Dict[str, Any], 
                                 sobject: str, 
                                 schema: str, 
                                 table: str,
                                 match_field: str) -> Dict[str, Any]:
        """Execute regular API sync using sobject_query."""
        
        logger.debug(f"🚀 Starting regular API sync for {sobject}")
        
        # Get query string and field descriptions
        last_modified_date = None
        if strategy['is_incremental']:
            last_modified_date = self._get_last_modified_date(schema, table)
            if last_modified_date:
                lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
                logger.debug(f"📅 Using last modified date for incremental sync: {lmd_sf}")
        
        logger.debug(f"🔍 Getting field descriptions for {sobject}")
        query_string, df_fields = sobjects.describe(self.access_info, sobject, lmd_sf if last_modified_date else None)
        logger.debug(f"📋 Raw query string from sobjects.describe: {query_string}")
        
        # Convert query string to proper SOQL
        soql_query = query_string.replace('+', ' ').replace('select', 'SELECT').replace('from', 'FROM')
        if last_modified_date:
            soql_query = soql_query.replace('where', 'WHERE').replace('LastModifiedDate>', 'LastModifiedDate > ')
        
        logger.debug(f"🔍 Final SOQL query: {soql_query}")
        print(f"🔍 Executing regular API query: {soql_query}")
        
        # Execute query and process results
        records_processed = 0
        
        if strategy['is_incremental']:
            # Incremental sync - use merge logic
            # First check if the main table exists before creating temp table
            if not self._table_exists(schema, table):
                error_msg = f"Cannot perform incremental sync: table {schema}.{table} does not exist"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            # Get current database for fully qualified table names
            current_db = self.session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
            
            tmp_table = f"TMP_{table}"
            create_temp_query = f"CREATE OR REPLACE TEMPORARY TABLE {current_db}.{schema}.{tmp_table} LIKE {current_db}.{schema}.{table}"
            logger.debug(f"🔍 Creating temp table: {create_temp_query}")
            debug_sql_execution(self.session, create_temp_query, "create_temp_table")
            
            # Use the existing df_fields from Salesforce describe - no need to query temp table
            table_fields = df_fields
            logger.debug(f"📋 Using existing table fields: {len(table_fields)} fields")
            
            # Query and load to temp table
            logger.debug("📥 Processing batches for incremental sync...")
            print(f"📥 Processing batches for incremental sync...")
            for batch_num, batch_df in enumerate(sobject_query.query_records(self.access_info, soql_query), 1):
                if batch_df is not None and not batch_df.empty:
                    logger.debug(f"📦 Processing batch {batch_num}: {len(batch_df)} records")
                    print(f"📦 Processing batch {batch_num}: {len(batch_df)} records")
                    # Let data_writer handle all formatting - no duplicate calls
                    formatted_df = batch_df.replace(np.nan, None)
                    
                    # Write to temp table using centralized data writer with type handling
                    logger.debug(f"💾 Writing batch {batch_num} to temp table {schema}.{tmp_table}")
                    print(f"💾 Writing batch {batch_num} to temp table {schema}.{tmp_table}")
                    
                    # Use type handling to prevent casting errors
                    try:
                        data_writer.write_batch_to_temp_table(
                            self.session, formatted_df, schema, tmp_table, df_fields,
                            validate_types=True
                        )
                    except Exception as e:
                        error_msg = str(e)
                        if any(phrase in error_msg for phrase in ["Failed to cast", "cast", "variant", "FIXED"]):
                            logger.warning(f"⚠️ Casting error detected: {error_msg[:100]}...")
                            logger.warning(f"⚠️ Retrying with type standardization...")
                            # Standardize types and retry
                            df_standardized = data_writer.standardize_dataframe_types(formatted_df, "string")
                            data_writer.write_batch_to_temp_table(
                                self.session, df_standardized, schema, tmp_table, df_fields,
                                validate_types=False
                            )
                        else:
                            logger.error(f"❌ Non-casting error: {error_msg}")
                            raise
                    
                    records_processed += len(batch_df)
            
            # Merge temp table with main table
            if records_processed > 0:
                logger.debug(f"🔄 Merging {records_processed} records from temp table to main table")
                print(f"🔄 Merging {records_processed} records from temp table to main table")
                try:
                    print(f"📋 About to call merge.format_filter_condition")
                    print(f"📋 Parameters: session={type(self.session)}, src_table={schema}.{tmp_table}, tgt_table={schema}.{table}, match_field={match_field}")
                    
                    # Get current database for schema context
                    current_db = self.session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
                    
                    # Set the correct schema context for the merge operation
                    self.session.sql(f"USE SCHEMA {current_db}.{schema}").collect()
                    
                    # Call merge with just table names (not fully qualified) since we set the schema context
                    merge_result = merge.format_filter_condition(self.session, tmp_table, table, match_field, match_field)
                    print(f"✅ Merge completed: {merge_result}")
                except Exception as e:
                    print(f"❌ Error during merge: {e}")
                    print(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    print(f"❌ Full merge error traceback: {traceback.format_exc()}")
                    raise
            
        else:
            # Full sync - overwrite table
            logger.debug("📥 Processing batches for full sync...")
            for batch_num, batch_df in enumerate(sobject_query.query_records(self.access_info, soql_query), 1):
                if batch_df is not None and not batch_df.empty:
                    logger.debug(f"📦 Processing batch {batch_num}: {len(batch_df)} records")
                    # Let data_writer handle all formatting - no duplicate calls
                    formatted_df = batch_df.replace(np.nan, None)
                    
                    # Write to table using centralized data writer with type handling (overwrite for first batch, append for subsequent)
                    is_first_batch = records_processed == 0
                    logger.debug(f"💾 Writing batch {batch_num} to table {schema}.{table} (overwrite={is_first_batch})")
                    
                    # Use type handling to prevent casting errors
                    try:
                        data_writer.write_batch_to_main_table(
                            self.session, formatted_df, schema, table, is_first_batch,
                            validate_types=True,
                            use_logical_type=False,  # More lenient for problematic data
                            df_fields=df_fields  # Pass field definitions for proper formatting
                        )
                    except Exception as e:
                        error_msg = str(e)
                        if any(phrase in error_msg for phrase in ["Failed to cast", "cast", "variant", "FIXED"]):
                            logger.warning(f"⚠️ Casting error detected: {error_msg[:100]}...")
                            logger.warning(f"⚠️ Retrying with type standardization...")
                            # Standardize types and retry
                            df_standardized = data_writer.standardize_dataframe_types(formatted_df, "string")
                            data_writer.write_batch_to_main_table(
                                self.session, df_standardized, schema, table, is_first_batch,
                                validate_types=False,
                                use_logical_type=False,
                                df_fields=df_fields  # Pass field definitions for proper formatting
                            )
                        else:
                            logger.error(f"❌ Non-casting error: {error_msg}")
                            raise
                    
                    records_processed += len(batch_df)
        
        logger.debug(f"✅ Regular API sync completed: {records_processed} records processed")
        return {
            'success': True,
            'records_processed': records_processed
        }


def sync_sobject_intelligent(session, 
                           access_info: Dict[str, str],
                           sobject: str, 
                           schema: str, 
                           table: str, 
                           match_field: str = 'ID',
                           use_stage: bool = False,
                           stage_name: Optional[str] = None,
                           force_full_sync: bool = False) -> Dict[str, Any]:
    """
    Convenience function for intelligent SObject synchronization.
    
    Args:
        session: Snowflake Snowpark session
        access_info: Dictionary containing Salesforce access details
        sobject: Salesforce SObject name (e.g., 'Account', 'Contact')
        schema: Snowflake schema name
        table: Snowflake table name
        match_field: Field to use for matching records (default: 'ID')
        use_stage: Whether to use Snowflake stage for large datasets
        stage_name: Snowflake stage name (required if use_stage=True)
        force_full_sync: Force a full sync regardless of previous sync status
        
    Returns:
        Dictionary containing sync results and metadata
    """
    sync_system = IntelligentSync(session, access_info)
    return sync_system.sync_sobject(
        sobject, schema, table, match_field, use_stage, stage_name, force_full_sync
    )


def sync_with_debug(session, access_info, sobject, schema, table, **kwargs):
    """
    Simple debug wrapper that prints everything to stdout.
    Use this in Snowflake notebooks to see exactly what's happening.
    """
    print("\n" + "="*100)
    print("🚀 STARTING SYNC WITH DEBUG OUTPUT")
    print("="*100)
    print(f"📋 Parameters:")
    print(f"   - SObject: {sobject}")
    print(f"   - Schema: {schema}")
    print(f"   - Table: {table}")
    print(f"   - Additional args: {kwargs}")
    print("="*100)
    
    try:
        result = sync_sobject_intelligent(
            session=session,
            access_info=access_info,
            sobject=sobject,
            schema=schema,
            table=table,
            **kwargs
        )
        
        print("\n" + "="*100)
        print("✅ SYNC COMPLETED SUCCESSFULLY")
        print("="*100)
        print(f"📊 Result: {result}")
        print("="*100)
        
        return result
        
    except Exception as e:
        print("\n" + "="*100)
        print("❌ SYNC FAILED")
        print("="*100)
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback:")
        print(traceback.format_exc())
        print("="*100)
        raise 