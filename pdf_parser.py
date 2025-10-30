"""
Модуль для парсинга структуры законодательных документов.
"""

import re
from typing import Dict, List, Optional
import pdfplumber
from pathlib import Path


class LegalDocumentParser:
    """Парсер для законодательных документов РК."""

    # Паттерны для структуры документа
    ARTICLE_PATTERN = r'^\s*Статья\s+(\d+(?:-\d+)?)\s*\.?\s*(.*?)$'
    PARAGRAPH_PATTERN = r'^\s*(\d+)\s*\.\s+(.*?)$'
    SUBPARAGRAPH_PATTERN = r'^\s*(\d+)\s*\)\s+(.*?)$'
    NOTE_PATTERN = r'^\s*(Примечани[ея]|Сноска|СНОСКА)\s*[:\.]?\s*(.*?)$'

    def __init__(self, verbose: bool = False):
        """
        Инициализация парсера.

        Args:
            verbose: Включить подробный вывод
        """
        self.verbose = verbose

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Извлекает текст из PDF с корректной обработкой кириллицы.

        Args:
            pdf_path: Путь к PDF-файлу

        Returns:
            str: Извлеченный текст

        Raises:
            Exception: При ошибке чтения PDF
        """
        try:
            text_parts = []

            with pdfplumber.open(pdf_path) as pdf:
                if self.verbose:
                    print(f"  Обработка {len(pdf.pages)} страниц...")

                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()

                    if page_text:
                        text_parts.append(page_text)

                        if self.verbose and page_num % 10 == 0:
                            print(f"    Обработано {page_num} страниц")

            full_text = '\n'.join(text_parts)

            if self.verbose:
                print(f"  Извлечено {len(full_text)} символов")

            return full_text

        except Exception as e:
            raise Exception(f"Ошибка при чтении PDF {pdf_path}: {str(e)}")

    def parse_structure(self, text: str) -> Dict[str, List]:
        """
        Парсит структуру законодательного документа.

        Args:
            text: Текст документа

        Returns:
            Dict: Структура документа со статьями, параграфами и т.д.
        """
        lines = text.split('\n')
        articles = []
        current_article = None
        current_paragraph = None
        buffer = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Проверяем на статью
            article_match = re.match(self.ARTICLE_PATTERN, line, re.IGNORECASE)
            if article_match:
                # Сохраняем предыдущую статью
                if current_article:
                    if current_paragraph:
                        current_paragraph['text'] = ' '.join(buffer).strip()
                        current_article['paragraphs'].append(current_paragraph)
                        current_paragraph = None
                        buffer = []
                    articles.append(current_article)

                # Создаем новую статью
                article_num, article_title = article_match.groups()
                current_article = {
                    'article_number': article_num,
                    'title': article_title.strip() if article_title else '',
                    'paragraphs': [],
                    'notes': []
                }
                buffer = []
                continue

            # Если нет текущей статьи, пропускаем
            if not current_article:
                continue

            # Проверяем на примечание
            note_match = re.match(self.NOTE_PATTERN, line, re.IGNORECASE)
            if note_match:
                if current_paragraph:
                    current_paragraph['text'] = ' '.join(buffer).strip()
                    current_article['paragraphs'].append(current_paragraph)
                    current_paragraph = None

                note_text = note_match.group(2) if note_match.group(2) else line
                current_article['notes'].append(note_text.strip())
                buffer = []
                continue

            # Проверяем на параграф (начинается с цифры и точки)
            paragraph_match = re.match(self.PARAGRAPH_PATTERN, line)
            if paragraph_match and len(paragraph_match.group(1)) <= 3:  # Ограничиваем 3 цифрами
                # Сохраняем предыдущий параграф
                if current_paragraph:
                    current_paragraph['text'] = ' '.join(buffer).strip()
                    current_article['paragraphs'].append(current_paragraph)

                # Создаем новый параграф
                para_num, para_text = paragraph_match.groups()
                current_paragraph = {
                    'number': para_num,
                    'text': para_text.strip(),
                    'subparagraphs': []
                }
                buffer = [para_text.strip()] if para_text.strip() else []
                continue

            # Проверяем на подпункт (начинается с цифры и скобки)
            subpara_match = re.match(self.SUBPARAGRAPH_PATTERN, line)
            if subpara_match and current_paragraph:
                subpara_num, subpara_text = subpara_match.groups()
                current_paragraph['subparagraphs'].append({
                    'number': subpara_num,
                    'text': subpara_text.strip()
                })
                continue

            # Добавляем строку к текущему буферу
            if line:
                buffer.append(line)

        # Сохраняем последнюю статью
        if current_article:
            if current_paragraph:
                current_paragraph['text'] = ' '.join(buffer).strip()
                current_article['paragraphs'].append(current_paragraph)
            articles.append(current_article)

        if self.verbose:
            print(f"  Извлечено статей: {len(articles)}")

        return {'articles': articles}

    def parse_pdf(self, pdf_path: Path) -> tuple[str, Dict]:
        """
        Полный парсинг PDF-файла.

        Args:
            pdf_path: Путь к PDF-файлу

        Returns:
            tuple: (текст документа, структура документа)
        """
        if self.verbose:
            print(f"Парсинг файла: {pdf_path.name}")

        # Извлекаем текст
        text = self.extract_text_from_pdf(pdf_path)

        # Парсим структуру
        structure = self.parse_structure(text)

        return text, structure
