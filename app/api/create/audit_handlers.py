# SPDX-License-Identifier: AGPL-3.0-only WITH LICENSE-ADDITIONAL
# Copyright (C) 2025 Петунин Лев Михайлович

import logging
from flask import Blueprint, request, jsonify

from api.create.audit_service import get_audit_service

logger = logging.getLogger(__name__)

# Создаем Blueprint для аудита
audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/v1/create', methods=['POST'])
def create_audit_record():
    """
    Создание записи аудита.
    
    Пример тела запроса:
    {
        "time": "2024-01-15T10:30:00Z",  # опционально
        "module_name": "users",
        "object_id": "123e4567-e89b-12d3-a456-426614174000",
        "initiator_id": "123e4567-e89b-12d3-a456-426614174001", 
        "message": "Пользователь создан"
    }
    
    :return: JSON ответ с результатом операции
    """
    try:
        # Логирование входящего запроса
        logger.info(
            f"Получен запрос на создание записи аудита от {request.remote_addr}"
        )
        
        # Проверка Content-Type
        if not request.is_json:
            logger.warning("Запрос не в формате JSON")
            return jsonify({
                'error': 'Invalid content type',
                'message': 'Content-Type должен быть application/json'
            }), 400
        
        # Получение данных из запроса
        data = request.get_json()
        
        if not data:
            logger.warning("Тело запроса пустое или невалидный JSON")
            return jsonify({
                'error': 'Invalid JSON',
                'message': 'Тело запроса должно содержать валидный JSON'
            }), 400
        
        # Логирование полученных данных (без чувствительной информации)
        logger.info(
            f"Данные запроса: module_name={data.get('module_name')}, "
            f"object_id={data.get('object_id')}"
        )
        
        # Создание записи через сервис
        audit_service = get_audit_service()
        message_id = audit_service.create_audit_record(data)
        
        if message_id is not None:
            logger.info(f"Запись аудита успешно создана с ID: {message_id}")
            return jsonify({
                'success': True,
                'message_id': message_id,  # Исправлено на message_id
                'message': 'Запись аудита успешно создана'
            }), 201
        else:
            logger.error("Не удалось создать запись аудита")
            return jsonify({
                'success': False,
                'error': 'Creation failed',
                'message': 'Не удалось создать запись аудита'
            }), 400
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке запроса: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Внутренняя ошибка сервера'
        }), 500