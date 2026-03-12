import csv
from collections import namedtuple
from pathlib import Path
from typing import Any, get_args, get_origin, Union

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

import pytest

from openfinance.brazil.business.model import BusinessAccountDTO


# CSV path: from test file location, go up to .3p/gustavorps/openfinance, then into docs
_dir_ = Path(__file__).resolve().parent
CSV_PATH = _dir_ / "_data" / "getBusinessAccounts_v1.csv"

# Define field structure from CSV
DataDictionaryField = namedtuple('DataDictionaryField', ['xpath', 'name', 'definition', 'type', 'size'])


def load_csv_fields() -> list[DataDictionaryField]:
    """Load and parse CSV data dictionary into namedtuples."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    
    fields = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:  # utf-8-sig strips BOM
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            xpath = row.get("Xpath", "").strip()
            if not xpath or xpath == "" or xpath == "/data":
                continue
            
            field = DataDictionaryField(
                xpath=xpath,
                name=row.get("Nome", "").strip(),
                definition=row.get("Definição", "").strip(),
                type=row.get("Tipo de Dado", "").strip(),
                size=row.get("Tamanho", "").strip(),
            )
            fields.append(field)
    
    return fields


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """Dynamically generate test cases from CSV data dictionary."""
    if "field" in metafunc.fixturenames:
        fields = load_csv_fields()
        
        if not fields:
            pytest.fail(f"No fields loaded from CSV: {CSV_PATH}")
        
        ids = [f"{field.xpath}" for field in fields]
        metafunc.parametrize("field", fields, ids=ids)


def parse_xpath_to_field_path(xpath: str) -> list[str | int]:
    """
    Convert CSV Xpath to field access path.
    Examples:
      /data -> ['data']
      /data/participant -> ['data', 'participant']
      /data/participant/brand -> ['data', 'participant', 'brand']
      /data/fees/services -> ['data', 'fees', 'services']
      /data/fees/services/prices/value -> ['data', 'fees', 'services', 'prices', 'value']
    """
    if xpath == "/data":
        return ["data"]
    
    parts = xpath.strip("/").split("/")
    return parts


def unwrap_type(field_type: Any) -> Any:
    """
    Recursively unwrap Optional, Annotated, and list types.
    Returns the innermost concrete type.
    """
    origin = get_origin(field_type)
    
    # Handle Union (includes Optional[T] which is Union[T, None])
    if origin is Union:
        args = get_args(field_type)
        # Get the non-None type
        field_type = next((arg for arg in args if arg is not type(None)), field_type)
        return unwrap_type(field_type)  # Recursively unwrap
    
    # Handle Annotated
    if origin is Annotated:
        args = get_args(field_type)
        if args:
            return unwrap_type(args[0])  # Recursively unwrap
    
    # Handle list
    if origin is list:
        args = get_args(field_type)
        if args:
            # Don't unwrap further - return the item type
            return args[0]
    
    return field_type


def get_field_by_path(model_class: type, path: list[str | int]) -> tuple[Any, str | None]:
    """
    Navigate model hierarchy by path and return (field_type, description).
    Handles nested models, lists, Optional, and Annotated types.
    """
    current_model = model_class
    description = None
    
    for i, part in enumerate(path):
        if isinstance(part, int):
            continue
        
        # Get model fields
        if not hasattr(current_model, "model_fields"):
            return None, None
            
        fields = current_model.model_fields
        if part not in fields:
            return None, None
        
        field_info = fields[part]
        field_type = field_info.annotation
        
        # Store description (from the final field in path)
        if i == len(path) - 1:
            # First try to get from field_info
            description = field_info.description
            
            # If not found, check if it's in Annotated metadata
            if not description:
                temp_type = field_type
                # Unwrap Optional first
                if get_origin(temp_type) is Union:
                    args = get_args(temp_type)
                    temp_type = next((arg for arg in args if arg is not type(None)), temp_type)
                
                # Check if Annotated and extract from Field metadata
                if get_origin(temp_type) is Annotated:
                    metadata = temp_type.__metadata__
                    for item in metadata:
                        if hasattr(item, 'description') and item.description:
                            description = item.description
                            break
        
        # Unwrap all type wrappers to get the concrete type
        unwrapped_type = unwrap_type(field_type)
        
        # Update current model for next iteration
        current_model = unwrapped_type
    
    return current_model, description


class TestDataDictionaryCsv:
    """Test Business Account model against CSV data dictionary."""
    
    def test_field_name(self, field: DataDictionaryField):
        """Test that CSV Xpath field exists in the DTO model."""
        path = parse_xpath_to_field_path(field.xpath)
        
        # Strip 'data' prefix since BusinessAccountDTO represents a data item
        if path and path[0] == "data":
            path = path[1:]
        
        if not path:  # Skip if only /data
            pytest.skip("Root data path")
        
        # Navigate to the field
        field_type, _ = get_field_by_path(BusinessAccountDTO, path)
        
        assert field_type is not None, (
            f"Field not found in model for Xpath: {field.xpath}. "
            f"Path: {path}"
        )
    
    def test_field_description(self, field: DataDictionaryField):
        """Test that CSV field description matches model Field description."""
        if not field.definition:
            pytest.skip("No definition in CSV")
        
        path = parse_xpath_to_field_path(field.xpath)
        
        # Strip 'data' prefix since BusinessAccountDTO represents a data item
        if path and path[0] == "data":
            path = path[1:]
        
        if not path:  # Skip if only /data
            pytest.skip("Root data path")
        
        _, model_description = get_field_by_path(BusinessAccountDTO, path)
        
        # Description should exist and not be empty
        assert model_description is not None, (
            f"No description found in model for Xpath: {field.xpath}"
        )
        
        # Description should not be empty
        assert len(model_description) > 0, (
            f"Empty description in model for Xpath: {field.xpath}"
        )

        # Trim trailing spaces/newlines before comparison
        csv_definition = field.definition.rstrip(" \n")
        model_description = model_description.rstrip(" \n")
        
        # CSV definition should match model description
        assert csv_definition == model_description, (
            f"Description mismatch for Xpath: {field.xpath}\n"
            f"CSV definition: {csv_definition}\n"
            f"Model description: {model_description}"
        )
