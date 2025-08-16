"""
Database schema reader module
"""

import psycopg2
from psycopg2 import sql
from typing import Dict, List, Any

class DatabaseSchemaReader:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def read_schema(self) -> Dict[str, Any]:
        """Read database schema and return structured data"""
        conn = psycopg2.connect(self.connection_string)
        cursor = conn.cursor()
        
        try:
            # Get all tables with their schemas
            cursor.execute("""
                SELECT 
                    t.table_schema,
                    t.table_name 
                FROM information_schema.tables t
                WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_schema, t.table_name
            """)
            
            tables_data = cursor.fetchall()
            tables = []
            
            for schema_name, table_name in tables_data:
                # Get columns information
                cursor.execute("""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        c.character_maximum_length,
                        c.numeric_precision,
                        c.numeric_scale
                    FROM information_schema.columns c
                    WHERE c.table_schema = %s AND c.table_name = %s
                    ORDER BY c.ordinal_position
                """, (schema_name, table_name))
                
                columns_data = cursor.fetchall()
                columns = []
                
                for col in columns_data:
                    column = {
                        'name': col[0],
                        'data_type': col[1],
                        'is_nullable': col[2] == 'YES',
                        'default': col[3],
                        'max_length': col[4],
                        'numeric_precision': col[5],
                        'numeric_scale': col[6]
                    }
                    columns.append(column)
                
                # Get primary keys
                cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
                """, (schema_name, table_name))
                
                primary_keys = [row[0] for row in cursor.fetchall()]
                
                # Mark primary key columns
                for column in columns:
                    column['is_primary_key'] = column['name'] in primary_keys
                
                # Get foreign keys
                cursor.execute("""
                    SELECT
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
                """, (schema_name, table_name))
                
                foreign_keys = []
                for row in cursor.fetchall():
                    foreign_keys.append({
                        'column': row[0],
                        'foreign_table_schema': row[1],
                        'foreign_table': row[2],
                        'foreign_column': row[3]
                    })
                
                # Mark foreign key columns
                for column in columns:
                    column['is_foreign_key'] = any(
                        fk['column'] == column['name'] for fk in foreign_keys
                    )
                
                table = {
                    'schema': schema_name,
                    'name': table_name,
                    'columns': columns,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys
                }
                
                tables.append(table)
            
            return {'tables': tables}
            
        finally:
            cursor.close()
            conn.close()