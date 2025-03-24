from tinydb import TinyDB, Query
import json
import os

class Database:
    def __init__(self, db_path="data/db.json"):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.db = TinyDB(db_path)
        self.query = Query()

    def set(self, key, value):
        """Store a value with a key"""
        # Convert set to list before JSON serialization
        if isinstance(value, set):
            value = list(value)

        # Convert value to JSON string if it's not already a string
        if not isinstance(value, str):
            value = json.dumps(value)

        # Update or insert the value
        self.db.upsert({'key': key, 'value': value}, self.query.key == key)

    def set_if_not_exists(self, key, value):
        """Store a value with a key if it doesn't exist"""
        if not self.exists(key):
            self.set(key, value)

    def get(self, key, default=None):
        """Retrieve a value by key"""
        result = self.db.get(self.query.key == key)
        if result:
            try:
                # Try to parse as JSON if it's a JSON string
                return json.loads(result['value'])
            except:
                # Return as string if not JSON
                return result['value']
        return default

    def delete(self, key):
        """Delete a key-value pair"""
        self.db.remove(self.query.key == key)

    def exists(self, key):
        """Check if a key exists"""
        return self.db.contains(self.query.key == key)

    def clear(self):
        """Clear all data"""
        self.db.truncate()

class CommonDB(Database):
    def __init__(self, db_path="data/common.json"):
        super().__init__(db_path)

class TargetDB(Database):
    def __init__(self, db_path="data/target.json"):
        super().__init__(db_path)

class PokemonCenterDB(Database):
    def __init__(self, db_path="data/pk_center.json"):
        super().__init__(db_path)

# Create a global instance
common_db = None
target_db = None
pk_center_db = None
def Init():
    global common_db, target_db, pk_center_db
    common_db = CommonDB(db_path="data/common.json")
    target_db = TargetDB(db_path="data/target.json")
    pk_center_db = PokemonCenterDB(db_path="data/pk_center.json")
