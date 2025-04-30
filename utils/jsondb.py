import json
import os
import uuid
from typing import Any, Dict, List, Optional


class Collection:
    def __init__(self, name: str, data: List[Dict[str, Any]], db: "JSONDatabase"):
        self.name = name
        self.data = data
        self.db = db
    
    def find_all(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if query is None:
            return self.data
        return [doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())]
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    def insert(self, document: Dict[str, Any]):
        document["@id"] = str(uuid.uuid4())
        self.data.append(document)
        self.db.data[self.name] = self.data
        self.db._save()
    
    def update(self, query: Dict[str, Any], updates: Dict[str, Any]):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(updates)
        self.db.data[self.name] = self.data
        self.db._save()

    def delete(self, query: Dict[str, Any]):
        self.data[:] = [doc for doc in self.data if not all(doc.get(k) == v for k, v in query.items())]
        self.db.data[self.name] = self.data
        self.db._save()
        

class JSONDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({}, f)
                
        self.data = self._load()
    
    def _load(self) -> Dict[str, List[Dict[str, Any]]]:
        with open(self.db_path, 'r') as f:
            return json.load(f)

    def _save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)
            
    def reload(self):
        self.data = self._load()
    
    def create_collection(self, name: str):
        if name not in self.data:
            self.data[name] = []
            self._save()
    
    def get_collection(self, name: str) -> Collection | None:
        if name not in self.data:
            return None
        return Collection(name, self.data[name], self)
    
    def drop_collection(self, name: str) -> bool:
        if name not in self.data:
            return False
        
        del self.data[name]
        self._save()
        return True
