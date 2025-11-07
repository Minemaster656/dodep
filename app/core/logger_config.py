import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

def setup_logger(app):
    """Настройка логгера для Flask приложения"""
    
    # Создаём директорию для логов
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Формат логов
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler для общих логов (ротация по размеру)
    info_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    info_handler.setFormatter(formatter)
    info_handler.setLevel(logging.INFO)
    
    # Handler для ошибок (ротация по времени - каждый день)
    error_handler = TimedRotatingFileHandler(
        'logs/errors.log',
        when='midnight',
        interval=1,
        backupCount=30  # Хранить 30 дней
        ,encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Добавляем handlers к логгеру приложения
    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    
    # Устанавливаем общий уровень
    app.logger.setLevel(logging.INFO)
    
    # Отключаем дублирование в консоль при debug=False
    if not app.debug:
        app.logger.info('Logger enabled')
