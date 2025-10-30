"""
Модуль для рекурсивного сканирования директорий и поиска PDF-файлов.
"""

import os
from pathlib import Path
from typing import List, Generator


class PDFScanner:
    """Сканер для поиска PDF-файлов в директориях."""

    def __init__(self, verbose: bool = False):
        """
        Инициализация сканера.

        Args:
            verbose: Включить подробный вывод
        """
        self.verbose = verbose

    def scan_directory(self, directory: str, recursive: bool = True) -> Generator[Path, None, None]:
        """
        Сканирует директорию на наличие PDF-файлов.

        Args:
            directory: Путь к директории для сканирования
            recursive: Искать рекурсивно в поддиректориях

        Yields:
            Path: Путь к найденному PDF-файлу

        Raises:
            ValueError: Если директория не существует
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            raise ValueError(f"Директория не существует: {directory}")

        if not directory_path.is_dir():
            raise ValueError(f"Путь не является директорией: {directory}")

        if self.verbose:
            print(f"Сканирование директории: {directory_path}")

        # Используем rglob для рекурсивного поиска или glob для не рекурсивного
        pattern = "**/*.pdf" if recursive else "*.pdf"

        for pdf_file in directory_path.glob(pattern):
            if pdf_file.is_file():
                if self.verbose:
                    print(f"  Найден PDF: {pdf_file.name}")
                yield pdf_file

    def get_pdf_files(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        Получает список всех PDF-файлов в директории.

        Args:
            directory: Путь к директории
            recursive: Искать рекурсивно

        Returns:
            List[Path]: Список путей к PDF-файлам
        """
        return list(self.scan_directory(directory, recursive))

    def count_pdf_files(self, directory: str, recursive: bool = True) -> int:
        """
        Подсчитывает количество PDF-файлов в директории.

        Args:
            directory: Путь к директории
            recursive: Искать рекурсивно

        Returns:
            int: Количество найденных PDF-файлов
        """
        return len(self.get_pdf_files(directory, recursive))
