#!/usr/bin/env python3
"""
Тестовый пример для демонстрации работы модулей.
Создает тестовые данные и демонстрирует парсинг структуры.
"""

import json
from metadata_extractor import MetadataExtractor
from pdf_parser import LegalDocumentParser


def test_metadata_extraction():
    """Тестирует извлечение метаданных."""
    print("=== Тест извлечения метаданных ===\n")

    # Тестовый текст с различными форматами
    test_texts = [
        """
        ЗАКОН РЕСПУБЛИКИ КАЗАХСТАН
        О противодействии коррупции
        от 18 ноября 2015 года № 410-V
        """,
        """
        КОДЕКС РЕСПУБЛИКИ КАЗАХСТАН
        Гражданский кодекс
        от 27.12.1994
        """,
        """
        КОНСТИТУЦИЯ РЕСПУБЛИКИ КАЗАХСТАН
        принят 30 августа 1995 года
        """
    ]

    extractor = MetadataExtractor(verbose=True)

    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Тест {i} ---")
        metadata = extractor.extract_metadata(text, f"test_{i}.pdf")
        print(f"Название: {metadata['title']}")
        print(f"Дата: {metadata['date']}")
        print()


def test_structure_parsing():
    """Тестирует парсинг структуры документа."""
    print("\n=== Тест парсинга структуры ===\n")

    # Тестовый текст с типичной структурой закона
    test_document = """
    ЗАКОН РЕСПУБЛИКИ КАЗАХСТАН
    О тестовом законодательстве
    от 1 января 2025 года № 1-VI

    Статья 1. Основные понятия

    В настоящем Законе используются следующие основные понятия:

    1. Тестирование - процесс проверки работоспособности программного обеспечения.

    2. Качество - соответствие требованиям и ожиданиям пользователей, включающее:

    1) функциональность системы;

    2) производительность и надежность;

    3) удобство использования.

    3. Верификация - подтверждение соответствия установленным требованиям.

    Примечание: Данное определение применяется для целей настоящего Закона.

    Статья 2. Область применения

    1. Настоящий Закон регулирует отношения в сфере тестирования.

    2. Действие настоящего Закона распространяется на:

    1) юридических лиц;

    2) физических лиц;

    3) государственные органы.

    Сноска: См. также положения статьи 15 настоящего Закона.

    Статья 3. Основные принципы

    Основными принципами являются:

    1. Законность - соблюдение законодательства Республики Казахстан.

    2. Прозрачность - открытость процессов для заинтересованных лиц.
    """

    parser = LegalDocumentParser(verbose=True)

    print("Парсинг тестового документа...\n")
    structure = parser.parse_structure(test_document)

    print(f"\n📊 Результаты парсинга:\n")
    print(f"Найдено статей: {len(structure['articles'])}\n")

    for article in structure['articles']:
        print(f"📄 Статья {article['article_number']}: {article['title']}")
        print(f"   Параграфов: {len(article['paragraphs'])}")
        print(f"   Примечаний: {len(article['notes'])}")

        for para in article['paragraphs']:
            subpara_count = len(para['subparagraphs'])
            if subpara_count > 0:
                print(f"   └─ Параграф {para['number']}: {subpara_count} подпунктов")

        if article['notes']:
            print(f"   └─ Примечания: {article['notes']}")

        print()


def test_json_output():
    """Демонстрирует формат JSON выхода."""
    print("\n=== Пример JSON выхода ===\n")

    # Создаем пример структуры
    example_output = {
        "metadata": {
            "filename": "закон_о_тестировании.pdf",
            "title": "ЗАКОН РЕСПУБЛИКИ КАЗАХСТАН О тестовом законодательстве",
            "date": "01.01.2025",
            "processing_date": "2025-10-30T12:00:00.000000"
        },
        "content": {
            "articles": [
                {
                    "article_number": "1",
                    "title": "Основные понятия",
                    "paragraphs": [
                        {
                            "number": "1",
                            "text": "Тестирование - процесс проверки работоспособности.",
                            "subparagraphs": []
                        },
                        {
                            "number": "2",
                            "text": "Качество - соответствие требованиям.",
                            "subparagraphs": [
                                {
                                    "number": "1",
                                    "text": "функциональность системы"
                                },
                                {
                                    "number": "2",
                                    "text": "производительность и надежность"
                                }
                            ]
                        }
                    ],
                    "notes": ["Данное определение применяется для целей настоящего Закона."]
                }
            ]
        }
    }

    # Выводим JSON с правильной кодировкой
    json_output = json.dumps(example_output, ensure_ascii=False, indent=2)
    print(json_output)


def test_special_characters():
    """Тестирует обработку специальных символов."""
    print("\n\n=== Тест специальных символов ===\n")

    test_text = """
    Статья 15. Специальные символы

    1. В документе могут использоваться следующие символы:

    1) символ номера: №;

    2) параграф: §;

    3) кавычки: «елочки» и "лапки";

    4) тире: — (длинное) и – (короткое);

    5) специальные буквы: Ә, ә, Ғ, ғ, Қ, қ, Ң, ң, Ө, ө, Ұ, ұ, Ү, ү, Һ, һ.

    Примечание: Все символы должны отображаться корректно.
    """

    parser = LegalDocumentParser(verbose=False)
    structure = parser.parse_structure(test_text)

    if structure['articles']:
        article = structure['articles'][0]
        print(f"✓ Статья распознана: {article['title']}")
        print(f"✓ Параграфов: {len(article['paragraphs'])}")

        for para in article['paragraphs']:
            if para['subparagraphs']:
                print(f"\n✓ Параграф {para['number']}: {len(para['subparagraphs'])} подпунктов")
                for sub in para['subparagraphs'][:3]:  # Показываем первые 3
                    print(f"  • {sub['text'][:50]}...")

        if article['notes']:
            print(f"\n✓ Примечание распознано: {article['notes'][0][:50]}...")


def main():
    """Запускает все тесты."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "ТЕСТИРОВАНИЕ PDF TO JSON PARSER" + " "*16 + "║")
    print("╚" + "="*58 + "╝")

    test_metadata_extraction()
    test_structure_parsing()
    test_json_output()
    test_special_characters()

    print("\n" + "="*60)
    print("✅ Все тесты завершены")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
