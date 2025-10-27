-- SPDX-License-Identifier: AGPL-3.0-only WITH LICENSE-ADDITIONAL
-- Copyright (C) 2025 Петунин Лев Михайлович

-- Создание таблицы комментариев к модулям
CREATE TABLE audit (
    message_id SERIAL PRIMARY KEY,
    module_name VARCHAR(45) NOT NULL,
    object_id UUID NOT NULL,
    initiator_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    message TEXT NOT NULL
);

GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER 
ON TABLE audit TO "DB_ADMIN";
GRANT ALL PRIVILEGES ON audit TO "DB_ADMIN";

-- Комментарии к таблице audit
COMMENT ON TABLE audit IS 'Таблица для хранения событий аудита';
COMMENT ON COLUMN audit.message_id IS 'Уникальный идентификатор события (автоинкрементный)';
COMMENT ON COLUMN audit.module_name IS 'Название модуля, к которому относится событие (максимальная длина 45 символов)';
COMMENT ON COLUMN audit.object_id IS 'Идентификатор объекта в формате UUID, к которому относится событие';
COMMENT ON COLUMN audit.initiator_id IS 'Идентификатор пользователя-инициатора события в формате UUID';
COMMENT ON COLUMN audit.created_at IS 'Дата и время создания события (часовой пояс UTC, заполняется автоматически)';
COMMENT ON COLUMN audit.message IS 'Текст события';

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_audit_module ON audit(module_name);
CREATE INDEX idx_audit_object ON audit(object_id);
CREATE INDEX idx_audit_initiator ON audit(initiator_id);
CREATE INDEX idx_audit_created ON audit(created_at);