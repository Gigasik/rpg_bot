async def error_handler(update, exception):\n    logger.error(f"Ошибка при обработке обновления {update.update_id}: {exception}")\n    return True
