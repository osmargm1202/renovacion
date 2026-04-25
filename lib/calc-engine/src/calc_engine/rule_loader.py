"""
Rule loader for renovacion.json
Resolves RH and people lookup from canonical catalogs
"""
import json
from pathlib import Path
from typing import Optional


def load_rules(rules_path: Path) -> dict:
    """Load and parse renovacion.json"""
    with open(rules_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def resolve_rh_rule(
    rules: dict,
    catalog_sector: str,
    catalog_type: str
) -> Optional[dict]:
    """
    Resolve RH rule by exact match on catalog_sector + catalog_type
    
    Returns:
        dict with 'min'/'max' or 'aprox', or None if not found
    """
    for sector_block in rules.get('tablas_renovaciones_aire', []):
        if sector_block.get('sector') != catalog_sector:
            continue
        
        for local in sector_block.get('locales', []):
            if local.get('tipo_de_local') == catalog_type:
                return local.get('renovaciones_aire_por_hora')
    
    return None


def resolve_people_rule(
    rules: dict,
    catalog_type: str
) -> Optional[dict]:
    """
    Resolve people caudal rule from tabla_caudal_por_persona
    Lookup by catalog_type only (no sector filter in people table)
    
    Returns:
        dict with 'valor' or 'min'/'max', or None if not found
    """
    for entry in rules.get('tabla_caudal_por_persona', []):
        if entry.get('tipo_de_local') == catalog_type:
            return entry.get('caudal_por_persona_m3_h')
    
    return None
