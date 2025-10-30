#!/usr/bin/env python3
"""
PDF to JSON Converter - Конвертер казахстанских законодательных актов из PDF в JSON.

Программа рекурсивно сканирует директории, находит PDF-файлы с законами РК
и преобразует их в структурированный JSON-формат с корректной обработкой
кириллицы и специальных символов.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdf_scanner import PDFScanner
from pdf_parser import LegalDocumentParser
from metadata_extractor import MetadataExtractor
from json_writer import JSONWriter


class PDFToJSONConverter:
    """Главный класс конвертера PDF в JSON."""

    def __init__(self, verbose: bool = False):
        """
        Инициализация конвертера.

        Args:
            verbose: Включить подробный вывод
        """
        self.verbose = verbose
        self.scanner = PDFScanner(verbose=verbose)
        self.parser = LegalDocumentParser(verbose=verbose)
        self.metadata_extractor = MetadataExtractor(verbose=verbose)
        self.json_writer = JSONWriter(verbose=verbose)

        self.processed_count = 0
        self.error_count = 0

    def convert_file(self, pdf_path: Path, output_dir: Path) -> bool:
        """
        Конвертирует один PDF-файл в JSON.

        Args:
            pdf_path: Путь к PDF-файлу
            output_dir: Директория для сохранения JSON

        Returns:
            bool: True если конвертация успешна
        """
        try:
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Обработка: {pdf_path.name}")
                print(f"{'='*60}")

            # Парсим PDF
            text, structure = self.parser.parse_pdf(pdf_path)

            # Извлекаем метаданные
            metadata = self.metadata_extractor.extract_from_file(pdf_path, text)

            # Создаем структуру для JSON
            json_data = self.json_writer.create_output_structure(metadata, structure)

            # Формируем путь для выходного файла
            output_filename = pdf_path.stem + '.json'
            output_path = output_dir / output_filename

            # Сохраняем JSON
            self.json_writer.save_to_json(json_data, output_path)

            self.processed_count += 1

            if not self.verbose:
                print(f"✓ {pdf_path.name} → {output_filename}")

            return True

        except Exception as e:
            self.error_count += 1
            print(f"✗ Ошибка при обработке {pdf_path.name}: {str(e)}", file=sys.stderr)
            return False

    def convert_directory(self, input_dir: str, output_dir: str, recursive: bool = True) -> None:
        """
        Конвертирует все PDF-файлы из директории.

        Args:
            input_dir: Входная директория с PDF
            output_dir: Выходная директория для JSON
            recursive: Рекурсивный поиск
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        # Проверяем входную директорию
        if not input_path.exists():
            raise ValueError(f"Входная директория не существует: {input_dir}")

        # Создаем выходную директорию
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n🔍 Сканирование: {input_path}")
        print(f"📁 Выходная директория: {output_path}")
        print(f"🔄 Рекурсивный поиск: {'Да' if recursive else 'Нет'}\n")

        # Сканируем и конвертируем
        pdf_files = list(self.scanner.scan_directory(input_dir, recursive))

        if not pdf_files:
            print("⚠️  PDF-файлы не найдены")
            return

        print(f"📄 Найдено PDF-файлов: {len(pdf_files)}\n")
        print("Начало конвертации...\n")

        for pdf_file in pdf_files:
            self.convert_file(pdf_file, output_path)

        # Итоги
        print(f"\n{'='*60}")
        print(f"✅ Обработано успешно: {self.processed_count}")
        if self.error_count > 0:
            print(f"❌ Ошибок: {self.error_count}")
        print(f"{'='*60}\n")


def main():
    """Главная функция программы."""
    parser = argparse.ArgumentParser(
        description='PDF to JSON - Конвертер казахстанских законодательных актов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s -i ./pdfs -o ./output
  %(prog)s --input /path/to/pdfs --output /path/to/json --verbose
  %(prog)s -i ./pdfs -o ./output --no-recursive
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Директория с PDF-файлами'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Директория для сохранения JSON-файлов'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Рекурсивный поиск в поддиректориях (по умолчанию: включено)'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_false',
        dest='recursive',
        help='Отключить рекурсивный поиск'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод'
    )

    args = parser.parse_args()

    # Создаем конвертер и запускаем
    try:
        converter = PDFToJSONConverter(verbose=args.verbose)
        converter.convert_directory(
            input_dir=args.input,
            output_dir=args.output,
            recursive=args.recursive
        )

        # Возвращаем код ошибки если были ошибки
        sys.exit(0 if converter.error_count == 0 else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
