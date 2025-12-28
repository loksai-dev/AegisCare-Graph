"""
Neo4j Database Connection and Session Management
Handles connection pooling and query execution
"""
from neo4j import GraphDatabase
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Neo4j database connection manager"""
    
    def __init__(self, lazy=True):
        """Initialize Neo4j driver with connection pool (lazy connection)"""
        self.driver = None
        if not lazy:
            self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j
        
        SECURITY: Never logs credentials - only connection status
        """
        if self.driver is None:
            try:
                # Use neo4j+ssc:// format (self-signed certificate) for Aura
                uri = settings.neo4j_uri
                if uri.startswith("neo4j+s://"):
                    uri = uri.replace("neo4j+s://", "neo4j+ssc://")
                    # Mask URI in logs (only show domain part, hide credentials)
                    uri_parts = uri.split("@")
                    if len(uri_parts) > 1:
                        masked_uri = f"neo4j+ssc://***@{uri_parts[1]}"
                    else:
                        masked_uri = f"{uri[:30]}..." if len(uri) > 30 else uri
                    logger.info(f"Adjusted URI format: {masked_uri}")
                
                # SECURITY: Credentials are only used here, never logged
                self.driver = GraphDatabase.driver(
                    uri,
                    auth=(settings.neo4j_username, settings.neo4j_password)
                )
                # Verify connectivity
                self.driver.verify_connectivity()
                logger.info(f"Successfully connected to Neo4j Aura (username: {settings.neo4j_username})")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                # Never log credentials in error messages
                raise
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            try:
                self.driver.close()
                logger.info("Database connection closed")
            except:
                pass
            finally:
                self.driver = None
    
    def get_session(self):
        """Get a new database session"""
        if self.driver is None:
            self._connect()
        return self.driver.session(database=settings.neo4j_database)
    
    def execute_query(self, query: str, parameters: dict = None):
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            
        Returns:
            List of records
        """
        try:
            # Ensure connection is initialized
            if self.driver is None:
                self._connect()
            
            with self.get_session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Database query error: {e}")
            logger.error(f"Query: {query[:100]}...")
            raise
    
    def execute_write(self, query: str, parameters: dict = None):
        """
        Execute a write transaction (CREATE, UPDATE, DELETE)
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            
        Returns:
            Summary of the transaction
        """
        try:
            # Ensure connection is initialized
            if self.driver is None:
                self._connect()
            
            with self.get_session() as session:
                result = session.run(query, parameters or {})
                return result.consume()
        except Exception as e:
            logger.error(f"Database write error: {e}")
            logger.error(f"Query: {query[:100]}...")
            raise


# Global database instance (lazy initialization - no connection on import)
db = Neo4jDatabase(lazy=True)

