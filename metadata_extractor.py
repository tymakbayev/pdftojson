"""
Модуль для извлечения метаданных из PDF-файлов с законодательными актами.
"""

import re
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class MetadataExtractor:
    """Извлекает метаданные из PDF-файлов с законами РК."""

    # Паттерны для поиска названия закона
    TITLE_PATTERNS = [
        r'ЗАКОН\s+РЕСПУБЛИКИ\s+КАЗАХСТАН\s+[«"]?([^«»"\n]+)[«"]?',
        r'КОДЕКС\s+РЕСПУБЛИКИ\s+КАЗАХСТАН\s+[«"]?([^«»"\n]+)[«"]?',
        r'КОНСТИТУЦИЯ\s+РЕСПУБЛИКИ\s+КАЗАХСТАН',
        r'УКАЗ\s+ПРЕЗИДЕНТА\s+РЕСПУБЛИКИ\s+КАЗАХСТАН\s+[«"]?([^«»"\n]+)[«"]?',
        r'ПОСТАНОВЛЕНИЕ\s+ПРАВИТЕЛЬСТВА\s+РЕСПУБЛИКИ\s+КАЗАХСТАН\s+[«"]?([^«»"\n]+)[«"]?',
    ]

    # Паттерны для поиска даты
    DATE_PATTERNS = [
        r'от\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\s+года',
        r'от\s+(\d{1,2})\.(\d{1,2})\.(\d{4})',
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s*г\.',
        r'принят\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})',
    ]

    MONTHS = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }

    def __init__(self, verbose: bool = False):
        """
        Инициализация экстрактора метаданных.

        Args:
            verbose: Включить подробный вывод
        """
        self.verbose = verbose

    def extract_title(self, text: str) -> Optional[str]:
        """
        Извлекает название закона из текста.

        Args:
            text: Текст документа

        Returns:
            Optional[str]: Название закона или None
        """
        # Берем первые 2000 символов для поиска заголовка
        search_text = text[:2000]

        for pattern in self.TITLE_PATTERNS:
            match = re.search(pattern, search_text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Если есть группа захвата, используем её, иначе всю совпадение
                title = match.group(1) if match.groups() else match.group(0)
                title = ' '.join(title.split())  # Нормализуем пробелы
                if self.verbose:
                    print(f"  Найдено название: {title}")
                return title

        if self.verbose:
            print("  Название не найдено")
        return None

    def extract_date(self, text: str) -> Optional[str]:
        """
        Извлекает дату принятия закона.

        Args:
            text: Текст документа

        Returns:
            Optional[str]: Дата в формате DD.MM.YYYY или None
        """
        # Берем первые 2000 символов для поиска даты
        search_text = text[:2000]

        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                date_str = self._normalize_date(match)
                if date_str:
                    if self.verbose:
                        print(f"  Найдена дата: {date_str}")
                    return date_str

        if self.verbose:
            print("  Дата не найдена")
        return None

    def _normalize_date(self, match: re.Match) -> Optional[str]:
        """
        Нормализует дату в формат DD.MM.YYYY.

        Args:
            match: Результат regex поиска

        Returns:
            Optional[str]: Дата в формате DD.MM.YYYY
        """
        groups = match.groups()

        if len(groups) == 3:
            day, month_or_num, year = groups

            # Проверяем, является ли второй элемент названием месяца
            if month_or_num.lower() in self.MONTHS:
                month = self.MONTHS[month_or_num.lower()]
            else:
                month = month_or_num.zfill(2)

            day = day.zfill(2)
            return f"{day}.{month}.{year}"

        return None

    def extract_metadata(self, text: str, filename: str) -> Dict[str, any]:
        """
        Извлекает все метаданные из документа.

        Args:
            text: Текст документа
            filename: Имя файла

        Returns:
            Dict: Словарь с метаданными
        """
        metadata = {
            'filename': filename,
            'title': self.extract_title(text),
            'date': self.extract_date(text),
            'processing_date': datetime.now().isoformat()
        }

        return metadata

    def extract_from_file(self, file_path: Path, text: str) -> Dict[str, any]:
        """
        Извлекает метаданные из файла.

        Args:
            file_path: Путь к PDF-файлу
            text: Извлеченный текст

        Returns:
            Dict: Словарь с метаданными
        """
        return self.extract_metadata(text, file_path.name)
