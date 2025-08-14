import datetime
import sqlite3
import time
from enum import Enum as PyEnum
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, RootModel

from kodosumi import const
from kodosumi.dtypes import DynamicModel
from kodosumi.log import logger

fromUnix = datetime.datetime.fromtimestamp

# Pydantic Enum für MODES
class MODES(str, PyEnum):
    NEXT = "next"
    UPDATE = "update"

FIELDS = ("fid", "tags", "summary", "description", "author", "organization", 
          "version", "final", "inputs", "status", "startup", "finish", 
          "search")

META_FIELDS = ("fid", "tags", "summary", "description", "author",
               "organization", "version")

DELIVER_FIELDS = ("fid", "tags", "summary", "inputs", "status", "startup",
                  "finish", "runtime", "locks")
SEARCH_FIELDS = ("author", "organization", "summary", "description", "fid", 
                 "status")

def get_time(cursor):
    query = "SELECT min(timestamp), max(timestamp) FROM monitor"
    cursor.execute(query)   
    ret = cursor.fetchone()
    start = end = None
    if ret:
        start = fromUnix(ret[0]) if ret[0] else None
        end = fromUnix(ret[1]) if ret[1] else None
    if start and end:
        runtime = (end - start).total_seconds()
    else:
        runtime = None
    return start, end, runtime

def get_status(cursor):
    # select latest status        
    query = """
    SELECT message FROM monitor 
    WHERE kind = 'status' 
    ORDER BY id DESC 
    LIMIT 1
    """
    cursor.execute(query)   
    ret = cursor.fetchone()
    if ret and ret[0]:
        return ret[0]
    return None

def build_search(result):
    search = []
    for key in SEARCH_FIELDS:
        if result[key]:
            search.append(f"{key}:{result[key]}")
    if result["tags"]:
        for tag in result["tags"]:
            search.append(f"tag:{tag}")
    if result["startup"]:
        search.append(
            f"startup:{result['startup'].isoformat()}")
    if result["inputs"]:
        search.append(f"inputs:{result["inputs"]}")
    if result["final"]:
        search.append(f"final:{result['final']}")
    return " ".join(search).lower()

def load_result(filename):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    startup, finish, runtime = get_time(cursor)
    status = get_status(cursor)
    query = """
    SELECT kind, message FROM monitor 
    WHERE kind IN ('inputs', 'meta', 'final', 'lock', 'lease')
    ORDER BY id DESC
    """
    cursor.execute(query)
    result = {k: None for k in FIELDS}
    result["status"] = status
    result["startup"] = startup
    result["finish"] = finish
    result["runtime"] = runtime
    result["locks"] = []
    lock = set()
    lease = set()
    for rec in cursor.fetchall():
        kind, message = rec
        data = DynamicModel.model_validate_json(message)
        if kind == "meta":
            for key in META_FIELDS:
                result[key] = data.root["dict"][key]
        elif kind in ("final", "inputs"):
            result[kind] = data.root
        elif kind == "lock":
            lock.add(data.root["dict"]["lid"])
        elif kind == "lease":
            lease.add(data.root["dict"]["lid"])
    if result["status"] == "running":
        result["locks"] = list(lock - lease)
    return result

def load_page(root: Union[Path, str], 
              mode: Optional[MODES]=MODES.NEXT,
              origin: Optional[str]=None, 
              offset: Optional[str]=None, 
              timestamp: Optional[float]=None,
              pp: int=10, 
              query: Optional[str]=None):
    current_timestamp = time.time()    
    all_dirs = []
    root = Path(root)
    if root.exists():
        all_dirs = [d for d in root.iterdir() if d.is_dir()]    
    all_dirs.sort(key=lambda d: d.name, reverse=True)
    total = len(all_dirs)
    if origin is None and all_dirs:
        origin = all_dirs[0].name  # origin is newest fid
    append_items: list[dict] = []
    insert_items: list[dict] = []
    update_items: list[dict] = []
    delete_items: list[str] = []
    next_offset = offset

    def _load(db_file, target, match=True):
        fid = db_file.parent.name
        try:
            result = load_result(db_file)
            result["fid"] = fid
            if result.get("status"):
                if query and match:
                    search = build_search(result)
                    if query.lower() not in search:
                        return False
                rec = {
                    k: v for k, v in result.items() 
                    if k in DELIVER_FIELDS
                }
                target.append(rec)
                return True
        except Exception as e:
            logger.error(f"failed to load {db_file}: {e}")
        return False
    
    for dir_path in all_dirs:
        fid = dir_path.name
        db_file = dir_path / const.DB_FILE
        archive = db_file.parent.joinpath(db_file.name + const.DB_ARCHIVE)
        is_archive = False
        if not db_file.exists():
            if archive.exists():
                is_archive = True
                db_file = archive
            else:
                continue
        # case 1: new element
        if origin and fid > origin and not is_archive:
            logger.debug(f"new execution: {fid}")
            if _load(db_file, insert_items, match=True):
                continue
        # case 2: modified element
        mod_time = db_file.stat().st_mtime
        for supp in (dir_path / const.DB_FILE_WAL, 
                     dir_path / const.DB_FILE_SHM):
            if supp.exists():
                mod_time = max(mod_time, supp.stat().st_mtime)
        if timestamp and mod_time > timestamp:
            if is_archive:
                logger.debug(f"archived execution: {fid}")
                delete_items.append(fid)
            else:
                logger.debug(f"modified execution: {fid}")
                _load(db_file, update_items, match=False)
            continue
        if is_archive:
            continue
        # case 3: elements for current page request
        if mode == "next" and (next_offset is None or fid < next_offset):
            if len(append_items) < pp:
                _load(db_file, append_items, match=True)
                next_offset = fid
            if len(append_items) >= pp:
                break
    if insert_items:
        sorted_inserts = sorted(
            insert_items, key=lambda x: x["fid"], reverse=True)
        new_origin = sorted_inserts[0]["fid"]
    else:
        new_origin = origin
    if append_items or insert_items or update_items or delete_items:
        timestamp = current_timestamp
    result = {
        "total": total,
        "origin": new_origin,
        "offset": next_offset if mode == MODES.NEXT and append_items else offset,
        "timestamp": timestamp,
        "items": {
            "append": append_items,
            "insert": insert_items,
            "update": update_items,
            "delete": delete_items
        },
        "query": query
    }
    return result

def get_paginated_results(root: Union[Path, str], 
                         offset: Optional[str] = None,
                         pp: int = 10,
                         q: Optional[str] = None):
    all_dirs = []
    root = Path(root)
    if root.exists():
        all_dirs = [d for d in root.iterdir() if d.is_dir()]    
    all_dirs.sort(key=lambda d: d.name, reverse=True)
    
    items: list[dict] = []
    
    for dir_path in all_dirs:
        if len(items) >= pp:
            break
            
        fid = dir_path.name
        db_file = dir_path / const.DB_FILE
        archive = db_file.parent.joinpath(db_file.name + const.DB_ARCHIVE)
        
        if not db_file.exists():
            continue
        
        if offset and fid >= offset:
            continue
            
        try:
            result = load_result(db_file)
            result["fid"] = fid
            
            if q and result.get("status"):
                search = build_search(result)
                if q.lower() not in search:
                    continue
            
            if result.get("status"):
                rec = {
                    k: v for k, v in result.items() 
                    if k in DELIVER_FIELDS
                }
                items.append(rec)
                
        except Exception as e:
            logger.error(f"failed to load {db_file}: {e}")

    return {
        "items": items,
        "query": q,
        "offset": items[-1]["fid"] if items else None
    }

def get_changes(root: Union[Path, str],
                since_timestamp: Optional[float] = None,
                q: Optional[str] = None):
    """
    Retrieve changes to items since a given timestamp.
    
    Args:
        root: Root directory containing execution data
        since_timestamp: Timestamp to check for changes since (None = get current max timestamp)
        q: Optional search query to filter results
        
    Returns:
        Dict containing:
        - items: List of changed items
        - changes: Dict with 'insert', 'update', 'delete' lists
        - timestamp: Current max modification timestamp for next request
        - query: The search query used
    """
    all_dirs = []
    root = Path(root)
    if root.exists():
        all_dirs = [d for d in root.iterdir() if d.is_dir()]    
    all_dirs.sort(key=lambda d: d.name, reverse=True)
    
    max_mod_time = 0.0
    changed_items: list[dict] = []
    delete_items: list[str] = []
    
    def _load_changed_item(db_file, match=True):
        """Helper function to load a changed item"""
        fid = db_file.parent.name
        try:
            result = load_result(db_file)
            result["fid"] = fid
            if result.get("status"):
                if q and match:
                    search = build_search(result)
                    if q.lower() not in search:
                        return False
                rec = {
                    k: v for k, v in result.items() 
                    if k in DELIVER_FIELDS
                }
                changed_items.append(rec)
                return True
        except Exception as e:
            logger.error(f"failed to load {db_file}: {e}")
        return False
    
    for dir_path in all_dirs:
        fid = dir_path.name
        db_file = dir_path / const.DB_FILE
        archive = dir_path.joinpath(const.DB_FILE + const.DB_ARCHIVE)
        is_archive = False
        
        # Check if file exists (either active or archived)
        if not db_file.exists():
            if archive.exists():
                is_archive = True
                db_file = archive
            else:
                continue
        
        # Calculate modification time (including WAL/SHM files)
        mod_time = db_file.stat().st_mtime
        for supp in (dir_path / const.DB_FILE_WAL, 
                     dir_path / const.DB_FILE_SHM):
            if supp.exists():
                supp_time = supp.stat().st_mtime
                mod_time = max(mod_time, supp_time)
        
        # Track max modification time
        max_mod_time = max(max_mod_time, mod_time)
        
        # If no timestamp provided, just collect max timestamp
        if since_timestamp is None:
            continue
            
        # Check for changes since timestamp
        if mod_time > since_timestamp:
            if is_archive:
                # File was archived since last check
                logger.debug(f"archived execution: {fid}")
                delete_items.append(fid)
            else:
                # This is a new or modified item since the timestamp
                logger.debug(f"changed execution: {fid}")
                _load_changed_item(db_file, match=True)
    
    # If no timestamp was provided, return just the current max timestamp
    if since_timestamp is None:
        return {
            # "items": [],
            # "changes": {
            "update": [],
            "delete": [],
            # },
            "timestamp": max_mod_time, # if max_mod_time > 0 else current_timestamp,
            "query": q
        }
    
    logger.debug(f"Changes since {since_timestamp}: {len(changed_items)} changed, {len(delete_items)} deleted. Returning timestamp: {max_mod_time}")
    
    return {
        "update": changed_items,
        "delete": delete_items,
        "timestamp": max_mod_time,
        "query": q
    }

