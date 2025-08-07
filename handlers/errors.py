import logging

logger = logging.getLogger(__name__)

async def error_handler(update, exception):
    """Обработчик ошибок с подробным логированием"""
    logger.error(
        f"Ошибка при обработке обновления {update.update_id}: {exception}",
        exc_info=True  # Добавляем стек вызовов для детального анализа
    )
    return True
