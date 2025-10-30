#!/bin/bash
# Скрипт установки зависимостей для PDF to JSON

echo "🔧 Установка зависимостей для PDF to JSON..."
echo ""

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Пожалуйста, установите Python 3.7 или выше."
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip не найден. Пожалуйста, установите pip."
    exit 1
fi

echo "✓ pip найден"
echo ""

# Создаем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка при создании виртуального окружения"
        exit 1
    fi
    echo "✓ Виртуальное окружение создано"
else
    echo "✓ Виртуальное окружение уже существует"
fi
echo ""

# Активируем виртуальное окружение и устанавливаем зависимости
echo "📦 Установка зависимостей из requirements.txt..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Установка завершена успешно!"
    echo ""
    echo "Для запуска программы:"
    echo "  1. Активируйте виртуальное окружение:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Запустите программу:"
    echo "     python pdftojson.py -i <input_dir> -o <output_dir>"
    echo ""
    echo "Для справки:"
    echo "  python pdftojson.py --help"
    echo ""
    echo "Для деактивации виртуального окружения:"
    echo "  deactivate"
    echo ""
else
    echo ""
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi
