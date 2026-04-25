"""Catalog loader - loads local models.json."""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_catalog(catalog_path: Path) -> Dict[str, Any]:
    """
    Load catalog from JSON file.
    
    Args:
        catalog_path: Path to models.json
        
    Returns:
        Dict with 'catalog' metadata and 'models' list
        
    Raises:
        FileNotFoundError: if catalog file missing
        json.JSONDecodeError: if invalid JSON
    """
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found: {catalog_path}")
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def get_models(catalog_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract models list from catalog data.
    
    Args:
        catalog_data: loaded catalog dict
        
    Returns:
        List of model dicts
    """
    return catalog_data.get('models', [])


def get_catalog_metadata(catalog_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract catalog metadata.
    
    Args:
        catalog_data: loaded catalog dict
        
    Returns:
        Catalog metadata dict
    """
    return catalog_data.get('catalog', {})
