from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from uuid import uuid4
from app.core.config import settings

class ScannerAdapter(ABC):
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        pass
    
    @abstractmethod
    def scan(self, collection_id: int, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass

class MockScannerAdapter(ScannerAdapter):
    def __init__(self):
        self.connected = False
        self.scan_count = 0
    
    def connect(self, config: Dict[str, Any]) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        self.connected = False
        return True
    
    def scan(self, collection_id: int, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.connected:
            raise Exception("设备未连接")
        
        self.scan_count += 1
        scan_dir = Path(settings.SCAN_STORAGE_DIR) / str(collection_id)
        scan_dir.mkdir(parents=True, exist_ok=True)
        
        mock_file_name = f"scan_{uuid4()}.obj"
        file_path = scan_dir / mock_file_name
        
        with open(file_path, "w") as f:
            f.write(f"""o scan_object
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 1.0 1.0 0.0
v 0.0 1.0 0.0
f 1 2 3 4
""")
        
        return {
            "success": True,
            "scan_id": f"SCAN{self.scan_count:04d}",
            "file_path": str(file_path),
            "file_name": mock_file_name,
            "file_size": file_path.stat().st_size,
            "scan_time": "00:00:15",
            "point_count": 100000,
            "resolution": "0.1mm",
            "message": "模拟扫描完成"
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "scan_count": self.scan_count,
            "model": "Mock 3D Scanner Pro",
            "firmware_version": "1.0.0",
            "status": "ready" if self.connected else "disconnected"
        }

class ScannerFactory:
    _adapters = {
        "mock": MockScannerAdapter
    }
    
    @classmethod
    def get_adapter(cls, adapter_type: str = "mock") -> ScannerAdapter:
        adapter_class = cls._adapters.get(adapter_type)
        if adapter_class is None:
            raise ValueError(f"不支持的扫描设备类型: {adapter_type}")
        return adapter_class()
    
    @classmethod
    def register_adapter(cls, adapter_type: str, adapter_class: type):
        if not issubclass(adapter_class, ScannerAdapter):
            raise ValueError("适配器必须继承 ScannerAdapter")
        cls._adapters[adapter_type] = adapter_class