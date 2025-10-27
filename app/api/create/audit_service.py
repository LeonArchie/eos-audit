# SPDX-License-Identifier: AGPL-3.0-only WITH LICENSE-ADDITIONAL
# Copyright (C) 2025 Петунин Лев Михайлович

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from maintenance.database_connector import get_db_connector
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AuditService:
    """Сервис для работы с аудитом"""
    
    def __init__(self):
        self.db_connector = get_db_connector()
    
    def create_audit_record(self, audit_data: Dict[str, Any]) -> Optional[int]:
        """
        Создание записи аудита в базе данных.
        
        :param audit_data: Данные для создания записи аудита
        :return: ID созданной записи или None в случае ошибки
        """
        try:
            # Валидация обязательных полей
            required_fields = ['module_name', 'object_id', 'initiator_id', 'message']
            for field in required_fields:
                if field not in audit_data or not audit_data[field]:
                    logger.error(f"Отсутствует обязательное поле: {field}")
                    return None
            
            # Валидация UUID
            try:
                object_uuid = uuid.UUID(audit_data['object_id'])
                initiator_uuid = uuid.UUID(audit_data['initiator_id'])
            except ValueError as e:
                logger.error(f"Неверный формат UUID: {e}")
                return None
            
            # Валидация длины module_name
            if len(audit_data['module_name']) > 45:
                logger.error(f"Длина module_name превышает 45 символов: {audit_data['module_name']}")
                return None
            
            # Подготовка данных для вставки
            insert_data = {
                'module_name': audit_data['module_name'],
                'object_id': str(object_uuid),
                'initiator_id': str(initiator_uuid),
                'message': audit_data['message']
            }
            
            # Если передано время, используем его, иначе БД сама установит NOW()
            if 'time' in audit_data and audit_data['time']:
                try:
                    # Парсим время из строки или используем как есть
                    if isinstance(audit_data['time'], str):
                        created_at = datetime.fromisoformat(audit_data['time'].replace('Z', '+00:00'))
                    else:
                        created_at = audit_data['time']
                    insert_data['created_at'] = created_at
                except (ValueError, TypeError) as e:
                    logger.warning(f"Неверный формат времени, используется текущее время: {e}")
            
            # SQL запрос для вставки (исправлено на message_id)
            sql = """
            INSERT INTO audit (module_name, object_id, initiator_id, created_at, message)
            VALUES (:module_name, :object_id, :initiator_id, 
                    COALESCE(:created_at, NOW()), :message)
            RETURNING message_id
            """
            
            with self.db_connector.get_session() as session:
                result = session.execute(text(sql), insert_data)
                message_id = result.scalar()
                session.commit()
                
                logger.info(
                    f"Создана запись аудита: ID={message_id}, "
                    f"модуль={insert_data['module_name']}, "
                    f"объект={insert_data['object_id']}"
                )
                
                return message_id
                
        except Exception as e:
            logger.error(f"Ошибка при создании записи аудита: {e}", exc_info=True)
            return None

# Глобальный экземпляр сервиса
_audit_service = None

def get_audit_service() -> AuditService:
    """
    Получение глобального экземпляра AuditService.
    
    :return: экземпляр AuditService
    """
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service