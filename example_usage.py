#!/usr/bin/env python3
"""
Пример использования библиотеки PDF to JSON программно (не через CLI).
"""

from pathlib import Path
from pdftojson import PDFToJSONConverter


def example_basic_usage():
    """Базовый пример использования."""
    print("=== Базовое использование ===\n")

    # Создаем конвертер
    converter = PDFToJSONConverter(verbose=True)

    # Конвертируем директорию
    converter.convert_directory(
        input_dir='./input_pdfs',
        output_dir='./output_json',
        recursive=True
    )

    print(f"\nОбработано: {converter.processed_count} файлов")
    print(f"Ошибок: {converter.error_count}")


def example_single_file():
    """Пример конвертации одного файла."""
    print("\n=== Конвертация одного файла ===\n")

    converter = PDFToJSONConverter(verbose=True)

    # Конвертируем один файл
    pdf_path = Path('./input_pdfs/закон.pdf')
    output_dir = Path('./output_json')

    if pdf_path.exists():
        success = converter.convert_file(pdf_path, output_dir)
        print(f"\nРезультат: {'Успешно' if success else 'Ошибка'}")
    else:
        print(f"Файл не найден: {pdf_path}")


def example_programmatic():
    """Пример программного использования отдельных компонентов."""
    print("\n=== Программное использование компонентов ===\n")

    from pdf_scanner import PDFScanner
    from pdf_parser import LegalDocumentParser
    from metadata_extractor import MetadataExtractor

    # Сканируем директорию
    scanner = PDFScanner(verbose=True)
    pdf_files = scanner.get_pdf_files('./input_pdfs', recursive=True)

    print(f"\nНайдено PDF файлов: {len(pdf_files)}")

    # Парсим первый файл если есть
    if pdf_files:
        parser = LegalDocumentParser(verbose=True)
        metadata_extractor = MetadataExtractor(verbose=True)

        pdf_file = pdf_files[0]
        print(f"\nОбработка файла: {pdf_file.name}")

        # Извлекаем текст и структуру
        text, structure = parser.parse_pdf(pdf_file)

        # Извлекаем метаданные
        metadata = metadata_extractor.extract_from_file(pdf_file, text)

        print(f"\nМетаданные:")
        print(f"  Название: {metadata.get('title', 'Не найдено')}")
        print(f"  Дата: {metadata.get('date', 'Не найдена')}")
        print(f"\nСтруктура:")
        print(f"  Статей: {len(structure.get('articles', []))}")


if __name__ == '__main__':
    # Раскомментируйте нужный пример:

    # example_basic_usage()
    # example_single_file()
    # example_programmatic()

    print("\n⚠️  Раскомментируйте нужный пример в коде для запуска\n")
