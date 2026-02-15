"""
文件I/O处理模块
负责将校验合格的数据写入本地文件系统
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from src.validation.validator import MonsterSchema


class FileHandler:
    """文件处理器"""
    
    def __init__(self, base_output_dir: str = "./output"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
    
    def save_data(self, 
                 data: Any,
                 data_type: str = "monster",
                 filename: Optional[str] = None,
                 subdirectory: Optional[str] = None) -> str:
        """
        保存数据到文件（通用方法）
        
        Args:
            data: 验证通过的数据对象
            data_type: 数据类型（monster/item/dialogue）
            filename: 文件名（如未提供则自动生成）
            subdirectory: 子目录名（如未提供则使用data_type）
            
        Returns:
            保存的文件路径
        """
        if subdirectory is None:
            subdirectory = data_type + "s"  # monsters, items, dialogues
        
        # 创建目录
        output_dir = self.base_output_dir / "assets" / subdirectory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 根据数据类型获取名称
            if data_type == "monster":
                safe_name = "".join(c if c.isalnum() else "_" for c in data.name)
                identifier = getattr(data, 'level', 1)
            elif data_type == "item":
                safe_name = "".join(c if c.isalnum() else "_" for c in data.name)
                identifier = getattr(data, 'level_requirement', 1)
            elif data_type == "dialogue":
                # 对话数据使用npc_name而不是name
                safe_name = "".join(c if c.isalnum() else "_" for c in data.npc_name)
                identifier = "dialogue"
            else:
                safe_name = "unknown"
                identifier = "data"
            
            filename = f"{safe_name}_{identifier}_{timestamp}.json"
        
        filepath = output_dir / filename
        
        # 转换为字典并保存
        data_dict = data.dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        # 计算文件哈希（用于完整性校验）
        file_hash = self._calculate_file_hash(filepath)
        
        # 创建元数据文件
        self._save_metadata(filepath, data, file_hash, data_type)
        
        return str(filepath)
    
    def save_monster_data(self, 
                         monster_data: MonsterSchema,
                         filename: Optional[str] = None,
                         subdirectory: str = "monsters") -> str:
        """
        保存怪物数据到文件（兼容旧版本）
        
        Args:
            monster_data: 验证通过的怪物数据
            filename: 文件名（如未提供则自动生成）
            subdirectory: 子目录名
            
        Returns:
            保存的文件路径
        """
        return self.save_data(monster_data, "monster", filename, subdirectory)
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """计算文件SHA256哈希"""
        sha256_hash = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _save_metadata(self, 
                      filepath: Path, 
                      data: Any,
                      file_hash: str,
                      data_type: str = "monster") -> None:
        """保存元数据文件"""
        metadata = {
            "original_file": filepath.name,
            "generated_at": datetime.now().isoformat(),
            "file_hash": file_hash,
            "data_type": data_type,
            "validation_status": "passed",
            "schema_version": "1.0.0"
        }
        
        # 根据数据类型添加特定信息
        if data_type == "monster":
            metadata["entity_info"] = {
                "name": data.name,
                "type": data.type,
                "level": data.level,
                "element": data.element
            }
        elif data_type == "item":
            metadata["entity_info"] = {
                "name": data.name,
                "type": data.type,
                "rarity": data.rarity,
                "level_requirement": data.level_requirement
            }
        elif data_type == "dialogue":
            metadata["entity_info"] = {
                "name": data.npc_name,
                "type": data_type,
                "npc_role": data.npc_role,
                "dialogue_id": data.dialogue_id
            }
        else:
            metadata["entity_info"] = {
                "name": getattr(data, 'name', 'unknown'),
                "type": data_type
            }
        
        metadata_path = filepath.with_suffix('.meta.json')
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def load_monster_data(self, filepath: str) -> Dict[str, Any]:
        """
        从文件加载怪物数据
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的数据字典
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_existing_file(self, 
                           monster_name: str, 
                           monster_level: int,
                           subdirectory: str = "monsters") -> Optional[str]:
        """
        检查是否已存在相同怪物文件
        
        Args:
            monster_name: 怪物名称
            monster_level: 怪物等级
            subdirectory: 子目录名
            
        Returns:
            已存在文件的路径，如不存在则返回None
        """
        output_dir = self.base_output_dir / "assets" / subdirectory
        
        if not output_dir.exists():
            return None
        
        safe_name = "".join(c if c.isalnum() else "_" for c in monster_name)
        pattern = f"{safe_name}_{monster_level}_*.json"
        
        for file in output_dir.glob(pattern):
            if file.is_file() and not file.name.endswith('.meta.json'):
                return str(file)
        
        return None
    
    def backup_existing_file(self, filepath: str) -> str:
        """
        备份已存在的文件
        
        Args:
            filepath: 原文件路径
            
        Returns:
            备份文件路径
        """
        path = Path(filepath)
        
        if not path.exists():
            return filepath
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_suffix(f'.backup_{timestamp}.json')
        
        import shutil
        shutil.copy2(path, backup_path)
        
        return str(backup_path)


# 单例实例
file_handler = FileHandler()
