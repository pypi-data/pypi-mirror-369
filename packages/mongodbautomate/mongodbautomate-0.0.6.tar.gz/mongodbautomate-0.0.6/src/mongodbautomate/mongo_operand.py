from typing import Any, Optional, List, Dict, Union
import os
import pandas as pd
import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoOperation:
    __collection = None
    __database = None

    def __init__(self, client_url: str, database_name: str, collection_name: Optional[str] = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name

    def create_mongo_client(self) -> MongoClient:
        """Create and return a MongoDB client."""
        try:
            return MongoClient(self.client_url)
        except PyMongoError as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def create_database(self):
        """Create and return the MongoDB database."""
        if MongoOperation.__database is None:
            client = self.create_mongo_client()
            self.database = client[self.database_name]
            MongoOperation.__database = self.database
        return MongoOperation.__database

    def create_collection(self, collection: Optional[str] = None):
        """Create and return a MongoDB collection."""
        if collection is None:
            collection = self.collection_name
        if not collection:
            raise ValueError("Collection name must be provided either during initialization or in this method.")
        
        if MongoOperation.__collection != collection:
            database = self.create_database()
            self.collection = database[collection]
            MongoOperation.__collection = collection

        return self.collection

    # -------------------
    # INSERT OPERATIONS
    # -------------------
    def insert_record(self, record: Union[Dict, List[Dict]], collection_name: Optional[str] = None) -> None:
        """Insert a single or multiple records into the collection."""
        collection = self.create_collection(collection_name)
        
        if isinstance(record, list):
            if not all(isinstance(data, dict) for data in record):
                raise TypeError("All items must be dictionaries.")
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection.insert_one(record)
        else:
            raise TypeError("Record must be a dictionary or a list of dictionaries.")

    def bulk_insert(self, datafile: str, collection_name: Optional[str] = None) -> None:
        """Insert bulk data from CSV or Excel into the collection."""
        if not os.path.exists(datafile):
            raise FileNotFoundError(f"The file '{datafile}' does not exist.")

        if datafile.endswith(".csv"):
            dataframe = pd.read_csv(datafile, encoding="utf-8")
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile)
        else:
            raise ValueError("File must be a CSV or XLSX.")

        datajson = json.loads(dataframe.to_json(orient="records"))
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)

    # -------------------
    # READ OPERATIONS
    # -------------------
    def find_records(self, query: Optional[Dict] = None, projection: Optional[Dict] = None,
                     limit: Optional[int] = None, collection_name: Optional[str] = None) -> List[Dict]:
        """Find records in the collection."""
        collection = self.create_collection(collection_name)
        cursor = collection.find(query or {}, projection or {})
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def aggregate_records(self, pipeline: List[Dict], collection_name: Optional[str] = None) -> List[Dict]:
        """Perform aggregation on the collection."""
        collection = self.create_collection(collection_name)
        return list(collection.aggregate(pipeline))

    # -------------------
    # UPDATE OPERATIONS
    # -------------------
    def update_record(self, query: Dict, update_values: Dict, multiple: bool = False,
                      collection_name: Optional[str] = None) -> None:
        """Update single or multiple records in the collection."""
        collection = self.create_collection(collection_name)
        if multiple:
            collection.update_many(query, {"$set": update_values})
        else:
            collection.update_one(query, {"$set": update_values})

    # -------------------
    # DELETE OPERATIONS
    # -------------------
    def delete_record(self, query: Dict, multiple: bool = False, collection_name: Optional[str] = None) -> None:
        """Delete single or multiple records from the collection."""
        collection = self.create_collection(collection_name)
        if multiple:
            collection.delete_many(query)
        else:
            collection.delete_one(query)

    # -------------------
    # UTILITY FUNCTIONS
    # -------------------
    def count_documents(self, query: Optional[Dict] = None, collection_name: Optional[str] = None) -> int:
        """Count documents in the collection."""
        collection = self.create_collection(collection_name)
        return collection.count_documents(query or {})

    def drop_collection(self, collection_name: Optional[str] = None) -> None:
        """Drop a MongoDB collection."""
        collection = self.create_collection(collection_name)
        collection.drop()

    def drop_database(self) -> None:
        """Drop the current MongoDB database."""
        client = self.create_mongo_client()
        client.drop_database(self.database_name)
        MongoOperation.__database = None
        MongoOperation.__collection = None
