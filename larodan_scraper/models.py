from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Product:
    """Class for storing product information"""
    id: str
    name: str
    CAS: str
    structure: str
    smiles: str
    description: str
    molecular_weight: str
    url: str
    image_path: str
    img: str
    pdf_msds: str
    synonyms: List[str]
    packaging: Dict[str, float]
    un_number: Optional[str] = None