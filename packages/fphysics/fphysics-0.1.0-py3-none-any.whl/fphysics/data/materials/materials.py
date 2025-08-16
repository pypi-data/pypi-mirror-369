"""Material property database module.

This module provides access to material property data including:
- Density, elastic constants, thermal properties
- Optical constants (refractive index, absorption)
- Electrical properties (conductivity, permittivity)
- Crystal structure data
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np


class Material:
    """Represents a material with its properties."""
    
    def __init__(self, name: str, properties: Dict[str, Any] = None):
        self.name = name
        self.properties = properties or {}
    
    def get_property(self, prop_name: str, default=None):
        """Get a material property by name."""
        return self.properties.get(prop_name, default)
    
    def set_property(self, prop_name: str, value: Any, unit: str = None):
        """Set a material property with optional unit."""
        if unit:
            self.properties[prop_name] = {"value": value, "unit": unit}
        else:
            self.properties[prop_name] = value
    
    def __repr__(self):
        return f"Material('{self.name}', {len(self.properties)} properties)"


class MaterialDatabase:
    """Database for storing and querying material properties."""
    
    def __init__(self):
        self.materials = {}
    
    def add_material(self, material: Material):
        """Add a material to the database."""
        self.materials[material.name] = material
    
    def get_material(self, name: str) -> Optional[Material]:
        """Get a material by name."""
        return self.materials.get(name)
    
    def list_materials(self):
        """List all available materials."""
        return list(self.materials.keys())
    
    def search_by_property(self, prop_name: str, value_range: tuple = None):
        """Search materials by property value or range."""
        results = []
        for material in self.materials.values():
            prop_value = material.get_property(prop_name)
            if prop_value is not None:
                if value_range is None:
                    results.append(material)
                elif isinstance(prop_value, (int, float)):
                    if value_range[0] <= prop_value <= value_range[1]:
                        results.append(material)
        return results
    
    def load_from_csv(self, filepath: Union[str, Path]):
        """Load materials from CSV file."""
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.pop('material_name', row.pop('name', 'Unknown'))
                material = Material(name)
                for key, value in row.items():
                    try:
                        # Try to convert to float
                        material.set_property(key, float(value))
                    except ValueError:
                        # Keep as string if not numeric
                        material.set_property(key, value)
                self.add_material(material)
    
    def load_from_json(self, filepath: Union[str, Path]):
        """Load materials from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            for name, properties in data.items():
                material = Material(name, properties)
                self.add_material(material)
    
    def save_to_json(self, filepath: Union[str, Path]):
        """Save database to JSON file."""
        data = {name: material.properties for name, material in self.materials.items()}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Common material properties constants
DENSITY_UNITS = "kg/m³"
ELASTIC_MODULUS_UNITS = "GPa"
THERMAL_CONDUCTIVITY_UNITS = "W/(m·K)"
REFRACTIVE_INDEX_UNITS = "dimensionless"
ELECTRICAL_RESISTIVITY_UNITS = "Ω·m"

# Common materials with basic properties
COMMON_MATERIALS = {
    "silicon": {
        "density": {"value": 2329, "unit": DENSITY_UNITS},
        "elastic_modulus": {"value": 170, "unit": ELASTIC_MODULUS_UNITS},
        "thermal_conductivity": {"value": 148, "unit": THERMAL_CONDUCTIVITY_UNITS},
        "refractive_index": {"value": 3.42, "unit": REFRACTIVE_INDEX_UNITS},
        "band_gap": {"value": 1.12, "unit": "eV"}
    },
    "aluminum": {
        "density": {"value": 2700, "unit": DENSITY_UNITS},
        "elastic_modulus": {"value": 70, "unit": ELASTIC_MODULUS_UNITS},
        "thermal_conductivity": {"value": 237, "unit": THERMAL_CONDUCTIVITY_UNITS},
        "electrical_resistivity": {"value": 2.65e-8, "unit": ELECTRICAL_RESISTIVITY_UNITS}
    },
    "copper": {
        "density": {"value": 8960, "unit": DENSITY_UNITS},
        "elastic_modulus": {"value": 128, "unit": ELASTIC_MODULUS_UNITS},
        "thermal_conductivity": {"value": 401, "unit": THERMAL_CONDUCTIVITY_UNITS},
        "electrical_resistivity": {"value": 1.68e-8, "unit": ELECTRICAL_RESISTIVITY_UNITS}
    }
}


def create_default_database() -> MaterialDatabase:
    """Create a database with common materials."""
    db = MaterialDatabase()
    for name, properties in COMMON_MATERIALS.items():
        material = Material(name, properties)
        db.add_material(material)
    return db
