import subprocess
import tempfile
from pathlib import Path
from typing import Optional

def generate_python_package(contract_path: str, output_dir: str) -> str:
    """
    Генерирует Python пакет из datacontract
    
    Args:
        contract_path: Путь к файлу datacontract (.yml)
        output_dir: Директория для сохранения пакета (если None - временная директория)
        
    Returns:
        str: Путь к сгенерированному пакету
    """
    from .proto_generator import generate_proto_from_yml
    
    contract_name = Path(contract_path).stem.replace('datacontract_', '')
    package_name = f"datacontract_{contract_name}"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Генерируем .proto файл
        proto_content = generate_proto_from_yml(contract_path)
        proto_path = Path(temp_dir) / f"{contract_name}.proto"
        proto_path.write_text(proto_content)
        
        # Генерируем Python код с помощью protoc
        subprocess.run([
            "protoc",
            f"--python_out={temp_dir}",
            f"--proto_path={temp_dir}",
            str(proto_path)
        ], check=True)
        
        # Создаем структуру пакета
        package_dir = Path(output_dir) if output_dir else Path(temp_dir) / package_name
        package_dir.mkdir(exist_ok=True)
        
        (package_dir / "__init__.py").touch()
        
        # Переносим сгенерированные файлы
        for pb_file in Path(temp_dir).glob("*_pb2.py"):
            pb_file.rename(package_dir / pb_file.name)
        
        # Здесь должна быть логика публикации в Nexus (заглушка)
        if output_dir is None:
            publish_to_nexus(package_dir, package_name)
        
        return str(package_dir)

def publish_to_nexus(package_path: str, package_name: str) -> None:
    """
    Заглушка для публикации пакета в Nexus
    
    Args:
        package_path: Путь к пакету
        package_name: Имя пакета
    """
    print(f"Публикация пакета {package_name} из {package_path} в Nexus...")
    # Реальная реализация будет использовать twine или другой клиент