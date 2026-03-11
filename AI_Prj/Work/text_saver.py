import json
import os
from datetime import datetime

class TextSaver:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def save_text(self, text):
        """Сохраняет текст в JSON-файл. Возвращает (успех, сообщение)."""
        text = text.strip()
        if not text:
            return False, "Пустой текст не сохранён"

        # Убеждаемся, что папка существует
        os.makedirs(self.output_dir, exist_ok=True)

        # Формируем запись
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text
        }

        json_path = os.path.join(self.output_dir, "inputs.json")

        # Загружаем существующие записи
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]  # на случай, если файл содержит один объект
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Добавляем новую запись
        data.append(entry)

        # Сохраняем
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True, f"Текст сохранён: {text[:30]}..." + ("…" if len(text) > 30 else "")