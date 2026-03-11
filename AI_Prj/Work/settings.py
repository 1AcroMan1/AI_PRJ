import json
import os

class Settings:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        # Параметры по умолчанию
        self.silence_threshold = 500       # порог громкости (RMS)
        self.silence_timeout = 10           # секунд тишины для останова
        self.output_dir = "recordings"       # папка для сохранения
        self.hotkey_toggle_record = "f9"    # старт/стоп записи
        self.hotkey_toggle_auto = "f10"     # переключение авторежима
        self.hotkey_settings = "f11"        # открыть настройки
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")

    def save(self):
        data = {key: getattr(self, key) for key in dir(self)
                if not key.startswith('_') and not callable(getattr(self, key))}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")