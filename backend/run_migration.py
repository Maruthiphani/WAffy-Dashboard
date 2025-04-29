"""
Script to run database migrations
"""
import os
import logging
import importlib.util
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration(migration_file):
    """Run a specific migration file"""
    try:
        # Get the absolute path to the migration file
        migration_path = os.path.join(os.path.dirname(__file__), 'migrations', migration_file)
        
        # Check if file exists
        if not os.path.exists(migration_path):
            logger.error(f"Migration file {migration_path} not found")
            return False
        
        # Load the module
        spec = importlib.util.spec_from_file_location("migration", migration_path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        
        # Run the migration
        if hasattr(migration, 'run_migration'):
            result = migration.run_migration()
            return result
        else:
            logger.error(f"Migration file {migration_file} does not have a run_migration function")
            return False
    
    except Exception as e:
        logger.error(f"Error running migration {migration_file}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a migration file name")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    logger.info(f"Running migration {migration_file}")
    
    success = run_migration(migration_file)
    
    if success:
        logger.info(f"Migration {migration_file} completed successfully")
    else:
        logger.error(f"Migration {migration_file} failed")
        sys.exit(1)
