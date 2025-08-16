"""
Utility functions for xarchgen
"""

import re
from typing import List, Dict, Any

def pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase"""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0].lower() + ''.join(x.title() for x in components[1:])

def snake_case(name: str) -> str:
    """Convert PascalCase or camelCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def map_postgres_to_python(pg_type: str, is_nullable: bool = False) -> str:
    """Map PostgreSQL data types to Python types"""
    type_map = {
        'integer': 'int',
        'bigint': 'int',
        'smallint': 'int',
        'serial': 'int',
        'bigserial': 'int',
        'smallserial': 'int',
        'numeric': 'Decimal',
        'decimal': 'Decimal',
        'real': 'float',
        'double precision': 'float',
        'money': 'Decimal',
        'character varying': 'str',
        'varchar': 'str',
        'character': 'str',
        'char': 'str',
        'text': 'str',
        'bytea': 'bytes',
        'timestamp': 'datetime',
        'timestamp without time zone': 'datetime',
        'timestamp with time zone': 'datetime',
        'date': 'date',
        'time': 'time',
        'time without time zone': 'time',
        'time with time zone': 'time',
        'interval': 'timedelta',
        'boolean': 'bool',
        'uuid': 'UUID',
        'json': 'dict',
        'jsonb': 'dict',
        'array': 'list',
        'inet': 'str',
        'cidr': 'str',
        'macaddr': 'str',
    }
    
    # Handle array types
    if pg_type.startswith('_') or pg_type.endswith('[]'):
        base_type = pg_type.strip('_').rstrip('[]')
        python_type = type_map.get(base_type, 'Any')
        array_type = f'List[{python_type}]'
        return f'Optional[{array_type}]' if is_nullable else array_type
    
    base_type = type_map.get(pg_type.lower(), 'Any')
    
    # Add Optional for nullable types (except str which can be None naturally)
    if is_nullable and base_type not in ['str', 'bytes', 'dict', 'list', 'Any']:
        return f'Optional[{base_type}]'
    
    return base_type

def map_postgres_to_csharp(pg_type: str, is_nullable: bool = False) -> str:
    """Map PostgreSQL data types to C# types"""
    type_map = {
        'integer': 'int',
        'bigint': 'long',
        'smallint': 'short',
        'serial': 'int',
        'bigserial': 'long',
        'smallserial': 'short',
        'numeric': 'decimal',
        'decimal': 'decimal',
        'real': 'float',
        'double precision': 'double',
        'money': 'decimal',
        'character varying': 'string',
        'varchar': 'string',
        'character': 'string',
        'char': 'string',
        'text': 'string',
        'bytea': 'byte[]',
        'timestamp': 'DateTime',
        'timestamp without time zone': 'DateTime',
        'timestamp with time zone': 'DateTimeOffset',
        'date': 'DateOnly',
        'time': 'TimeOnly',
        'time without time zone': 'TimeOnly',
        'time with time zone': 'TimeOnly',
        'interval': 'TimeSpan',
        'boolean': 'bool',
        'uuid': 'Guid',
        'json': 'string',
        'jsonb': 'string',
        'inet': 'string',
        'cidr': 'string',
        'macaddr': 'string',
    }
    
    # Handle array types
    if pg_type.startswith('_') or pg_type.endswith('[]'):
        base_type = pg_type.strip('_').rstrip('[]')
        csharp_type = type_map.get(base_type, 'object')
        return f'{csharp_type}[]'
    
    base_type = type_map.get(pg_type.lower(), 'object')
    
    # Add nullable annotation for value types if needed
    if is_nullable and base_type not in ['string', 'byte[]', 'object'] and not base_type.endswith('[]'):
        return f'{base_type}?'
    
    return base_type

def get_primary_key_type(table: Dict[str, Any]) -> str:
    """Get the C# type of the primary key"""
    for col in table['columns']:
        if col.get('is_primary_key', False):
            return map_postgres_to_csharp(col['data_type'], col['is_nullable'])
    return 'int'  # Default to int if no primary key found

def normalize_connection_string(conn_str: str) -> str:
    """Convert PostgreSQL URL to .NET connection string format"""
    if not conn_str:
        return ""
    
    # If it's already in .NET format, return as is
    if 'Host=' in conn_str or 'Server=' in conn_str:
        return conn_str
    
    # Parse PostgreSQL URL format
    import re
    pattern = r'postgresql://(?:([^:]+):([^@]+)@)?([^:/]+)(?::(\d+))?/(.+)'
    match = re.match(pattern, conn_str)
    
    if match:
        user, password, host, port, database = match.groups()
        port = port or '5432'
        
        parts = [
            f"Host={host}",
            f"Port={port}",
            f"Database={database}"
        ]
        
        if user:
            parts.append(f"Username={user}")
        if password:
            parts.append(f"Password={password}")
        
        return ";".join(parts)
    
    return conn_str

def extract_tables_by_schema(tables: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Group tables by their database schema"""
    groups = {}
    for table in tables:
        schema = table.get('schema', 'public')
        if schema not in groups:
            groups[schema] = []
        groups[schema].append(table['name'])
    return groups

def map_postgres_to_sqlalchemy(pg_type: str, is_nullable: bool = False) -> str:
    """Map PostgreSQL data types to SQLAlchemy types"""
    
    pg_type = pg_type.lower()
    
    type_map = {
        'integer': 'Integer',
        'int': 'Integer',
        'int4': 'Integer',
        'serial': 'Integer',
        'smallint': 'SmallInteger',
        'int2': 'SmallInteger',
        'bigint': 'BigInteger',
        'int8': 'BigInteger',
        'bigserial': 'BigInteger',
        'serial8': 'BigInteger',
        'uuid': 'PG_UUID(as_uuid=True)',
        'text': 'Text',
        'character varying': 'String',
        'varchar': 'String',
        'character': 'String',
        'char': 'String',
        'boolean': 'Boolean',
        'bool': 'Boolean',
        'date': 'Date',
        'timestamp': 'DateTime(timezone=True)',
        'timestamp without time zone': 'DateTime',
        'timestamp with time zone': 'DateTime(timezone=True)',
        'timestamptz': 'DateTime(timezone=True)',
        'numeric': 'Numeric',
        'decimal': 'Numeric',
        'double precision': 'Float',
        'float8': 'Float',
        'real': 'Float',
        'float4': 'Float',
        'bytea': 'LargeBinary',
        'json': 'JSON',
        'jsonb': 'JSON',
        'time': 'Time',
        'time without time zone': 'Time',
        'time with time zone': 'Time',
        'interval': 'Interval',
        'money': 'Numeric',
    }
    
    base_type = pg_type.split('(')[0].strip()
    
    # Handle varchar with length
    if base_type in ['varchar', 'character varying'] and '(' in pg_type:
        length = pg_type.split('(')[1].split(')')[0]
        return f'String({length})'
    
    return type_map.get(base_type, 'String')

def normalize_connection_string_for_python(conn_str: str) -> str:
    """Normalize connection string for Python/SQLAlchemy async (asyncpg)"""
    if not conn_str:
        return "postgresql+asyncpg://username:password@localhost:5432/database"
    
    # If it's already in async format, return as is
    if conn_str.startswith('postgresql+asyncpg://'):
        return conn_str
    
    # Convert postgresql:// to postgresql+asyncpg://
    if conn_str.startswith('postgresql://'):
        return conn_str.replace('postgresql://', 'postgresql+asyncpg://')
    
    # Convert .NET format to PostgreSQL URL format with asyncpg
    if 'Host=' in conn_str:
        parts = {}
        for part in conn_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key.strip()] = value.strip()
        
        host = parts.get('Host', 'localhost')
        port = parts.get('Port', '5432')
        database = parts.get('Database', 'database')
        username = parts.get('Username', 'username')
        password = parts.get('Password', 'password')
        
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    
    # Default case - assume it's a basic postgresql:// and convert to asyncpg
    if conn_str.startswith('postgres://'):
        return conn_str.replace('postgres://', 'postgresql+asyncpg://')
    
    return f"postgresql+asyncpg://{conn_str}" if not conn_str.startswith('postgresql') else conn_str