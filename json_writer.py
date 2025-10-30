"""
Модуль для сохранения данных в JSON с правильной кодировкой.
"""

import json
from pathlib import Path
from typing import Dict


class JSONWriter:
    """Класс для записи структурированных данных в JSON."""

    def __init__(self, verbose: bool = False):
        """
        Инициализация writer'а.

        Args:
            verbose: Включить подробный вывод
        """
        self.verbose = verbose

    def save_to_json(self, data: Dict, output_path: Path) -> None:
        """
        Сохраняет данные в JSON-файл с правильной кодировкой UTF-8.

        Args:
            data: Данные для сохранения
            output_path: Путь к выходному файлу

        Raises:
            Exception: При ошибке записи файла
        """
        try:
            # Создаем директорию если её нет
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Сохраняем с правильной кодировкой и форматированием
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,  # Важно для кириллицы
                    indent=2,
                    sort_keys=False
                )

            if self.verbose:
                print(f"  Сохранено в: {output_path}")

        except Exception as e:
            raise Exception(f"Ошибка при сохранении JSON {output_path}: {str(e)}")

    def create_output_structure(self, metadata: Dict, content: Dict) -> Dict:
        """
        Создает финальную структуру для JSON.

        Args:
            metadata: Метаданные документа
            content: Содержимое и структура документа

        Returns:
            Dict: Структурированные данные
        """
        return {
            'metadata': metadata,
            'content': content
        }
