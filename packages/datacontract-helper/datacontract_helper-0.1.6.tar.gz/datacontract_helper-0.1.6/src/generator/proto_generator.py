from pathlib import Path
import yaml
import subprocess
import tempfile

def generate_proto_from_yml(contract_path: str) -> str:
    """
    Генерирует .proto файл из datacontract YAML
    
    Args:
        contract_path: Путь к файлу datacontract (.yml)
        
    Returns:
        str: Содержимое сгенерированного .proto файла
    """
    with open(contract_path, 'r') as file:
        contract = yaml.safe_load(file)

    # Здесь должна быть логика преобразования YAML в .proto
    proto_content = f"""
    syntax = "proto3";
    
    package {contract['name'].lower()};
    
    message {contract['name']} {{
        // поля из контракта
    }}
    """
    
    return proto_content.strip()