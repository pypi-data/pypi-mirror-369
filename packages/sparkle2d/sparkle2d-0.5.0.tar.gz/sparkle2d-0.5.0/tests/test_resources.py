"""
ResourceManager testleri
"""

import pytest
import tempfile
import os
from sparkle2d.resources import ResourceManager


class TestResourceManager:
    """ResourceManager test sınıfı"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.resource_manager = ResourceManager()
        
        # Geçici test dosyaları oluştur
        self.temp_dir = tempfile.mkdtemp()
        self.resource_manager.set_base_path(self.temp_dir)
        
        # Test JSON dosyası oluştur
        self.test_json_path = os.path.join(self.temp_dir, "test.json")
        with open(self.test_json_path, 'w') as f:
            f.write('{"test": "data", "number": 42}')
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Geçici dosyaları temizle
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_json_cache(self):
        """JSON yükleme cache testi"""
        # İlk yükleme
        data1 = self.resource_manager.load_json("test.json")
        assert data1["test"] == "data"
        assert data1["number"] == 42
        
        # Cache bilgilerini kontrol et
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) == 1
        
        # İkinci yükleme - aynı dosya cache'den döndürülmeli
        data2 = self.resource_manager.load_json("test.json")
        assert data2 is data1  # Aynı obje referansı
        
        # Refcount artmış olmalı
        cache_info = self.resource_manager.get_cache_info()
        assert cache_info[os.path.join(self.temp_dir, "test.json")] == 2
    
    def test_unload_json(self):
        """JSON unload testi"""
        # Yükle
        data = self.resource_manager.load_json("test.json")
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) == 1
        
        # Unload
        self.resource_manager.unload("test.json")
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) == 0
    
    def test_unload_multiple_times(self):
        """Çoklu unload testi"""
        # İki kez yükle
        data1 = self.resource_manager.load_json("test.json")
        data2 = self.resource_manager.load_json("test.json")
        
        cache_info = self.resource_manager.get_cache_info()
        assert cache_info[os.path.join(self.temp_dir, "test.json")] == 2
        
        # İlk unload - refcount azalmalı ama cache'de kalmalı
        self.resource_manager.unload("test.json")
        cache_info = self.resource_manager.get_cache_info()
        assert cache_info[os.path.join(self.temp_dir, "test.json")] == 1
        
        # İkinci unload - cache'den kaldırılmalı
        self.resource_manager.unload("test.json")
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) == 0
    
    def test_file_not_found(self):
        """Dosya bulunamadı testi"""
        with pytest.raises(FileNotFoundError):
            self.resource_manager.load_json("nonexistent.json")
    
    def test_clear_cache(self):
        """Cache temizleme testi"""
        # Birkaç dosya yükle
        self.resource_manager.load_json("test.json")
        
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) > 0
        
        # Cache'i temizle
        self.resource_manager.clear_cache()
        cache_info = self.resource_manager.get_cache_info()
        assert len(cache_info) == 0
