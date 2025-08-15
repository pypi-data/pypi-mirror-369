import os
import sys
import subprocess
from pynput import keyboard
import enchant
import pyperclip
import time
import pygame

class KeyboardTracker:
    def __init__(self):
        """Инициализация трекера клавиш"""
        self.letter_count = 0
        self.current_word = []
        self.listener = None
        self.en_dict = enchant.Dict("en_US")
        self.ru_dict = enchant.Dict("ru_RU")
        self.shift_pressed = False
        self.caps_lock = False
        self.last_key_pressed = None
        self.word_complete = False
        self.processing_word = False
        self.block_processing = False
        self.active = True  # Флаг активности программы
        self.ctrl_pressed = False  # Флаг нажатия Ctrl

        # Гласные буквы для проверки (добавлено)
        self.vowels_en = {'a', 'e', 'i', 'o', 'u', 'y'}
        self.vowels_ru = {'а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я'}

        # Звуковая система
        pygame.mixer.init()
        try:
            # Получаем путь к звуковому файлу относительно расположения модуля
            sound_path = os.path.join(os.path.dirname(__file__), 'assets', 'sound.wav')
            self.sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Warning: Could not load sound file: {e}")
            self.sound = None

        # Маппинг символов между раскладками
        self.keyboard_mapping = {
            'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н',
            'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ',
            'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р',
            'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э', 'z': 'я',
            'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
            ',': 'б', '.': 'ю', '/': '.'
        }

        self.reverse_mapping = {v: k for k, v in self.keyboard_mapping.items()}
        self.valid_chars = set(self.keyboard_mapping.keys()).union(set(self.reverse_mapping.keys()))

    def has_enough_vowels(self, word, lang):
        """Требует хотя бы 1 гласную для слов 3-5 букв и 20% для длинных."""
        vowels = self.vowels_en if lang == 'en' else self.vowels_ru
        word_lower = word.lower()
        vowel_count = sum(1 for char in word_lower if char in vowels)

        if len(word) <= 5:
            return vowel_count >= 1  # Хотя бы 1 гласная для коротких слов
        return (vowel_count / len(word)) >= 0.2  # 20% для длинных

    def contains_digits(self, word):
        """Проверяет, содержит ли слово хотя бы одну цифру"""
        return any(char.isdigit() for char in word)

    def check_word(self, word, lang):
        """Проверяет только наличие достаточного количества гласных"""
        return self.has_enough_vowels(word, lang)

        if lang == 'en':
            return self.en_dict.check(word)
        else:
            return self.ru_dict.check(word)

    def play_sound(self):
        """Воспроизведение звукового сигнала"""
        if self.sound:
            self.sound.play()

    def on_press(self, key):
        """Обработчик нажатия клавиш"""
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            self.ctrl_pressed = True
            return

        if key == keyboard.Key.space and self.ctrl_pressed:
            self.active = not self.active
            print(f"Program {'active' if self.active else 'inactive'}")
            self.ctrl_pressed = False  # Сбрасываем флаг после обработки комбинации
            return

        # Обработка Ctrl+Пробел для включения/выключения программы
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            self.ctrl_pressed = True
            return

        if key == keyboard.Key.space and self.ctrl_pressed:
            self.active = not self.active
            print(f"Program {'active' if self.active else 'inactive'}")
            self.ctrl_pressed = False
            return

        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            self.block_processing = True
            return

        if self.block_processing:
            self.block_processing = False
            return

        if self.processing_word:
            return

        if key == keyboard.Key.caps_lock:
            self.caps_lock = not self.caps_lock

        if self.word_complete and hasattr(key, 'char'):
            self.reset_counters()
            self.word_complete = False

        try:
            if hasattr(key, 'char'):
                current_layout = self.get_current_layout()
                char = key.char
                is_upper = char.isupper()
                lower_char = char.lower()

                # Проверяем, является ли символ допустимым
                if lower_char in self.valid_chars or char.isdigit():
                    if lower_char in self.keyboard_mapping or lower_char in self.reverse_mapping or char.isdigit():
                        if current_layout == 'ru':
                            ru_char = self.keyboard_mapping.get(lower_char, lower_char)
                            actual_char = ru_char.upper() if is_upper else ru_char
                        else:
                            actual_char = char

                        self.current_word.append({
                            'original': char,
                            'actual': actual_char,
                            'layout': current_layout,
                            'is_upper': is_upper
                        })
                        self.letter_count += 1
                else:
                    # Сбрасываем состояние, если символ не входит в допустимые
                    self.reset_counters()
                    self.last_clipboard_content = None
        except AttributeError:
            # Сбрасываем состояние для специальных клавиш
            if key not in [keyboard.Key.space, keyboard.Key.enter, keyboard.Key.backspace,
                          keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
                          keyboard.Key.pause]:
                self.reset_counters()
                self.last_clipboard_content = None

    def get_current_layout(self):
        """Определение текущей раскладки клавиатуры"""
        try:
            result = subprocess.run(['xkblayout-state', 'print', '%s'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return 'us'
        except:
            return 'us'

    def set_layout(self, layout):
        """Установка раскладки клавиатуры"""
        try:
            subprocess.run(['xkblayout-state', 'set', '0' if layout == 'us' else '1'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
        except:
            pass

    def build_original_word(self):
        """Сборка исходного слова (как было набрано)"""
        return ''.join([ch['original'] for ch in self.current_word])

    def build_actual_word(self):
        """Сборка фактического слова (с учетом раскладки)"""
        return ''.join([ch['actual'] for ch in self.current_word])

    def convert_word(self, word, from_layout, to_layout):
        """Конвертация слова между раскладками"""
        mapping = self.reverse_mapping if from_layout == 'ru' else self.keyboard_mapping
        result = []
        for c in word:
            lower_c = c.lower()
            new_c = mapping.get(lower_c, lower_c)
            result.append(new_c.upper() if c.isupper() else new_c)
        return ''.join(result)

    def delete_word(self):
        """Удаление текущего слова с помощью Backspace"""
        controller = keyboard.Controller()
        for _ in range(len(self.current_word) + 1):
            controller.press(keyboard.Key.backspace)
            controller.release(keyboard.Key.backspace)
            time.sleep(0.01)

    def insert_word(self, word, add_space=False, add_enter=False):
        """Вставка слова через буфер обмена"""
        self.last_clipboard_content = pyperclip.paste()
        pyperclip.copy(word)

        controller = keyboard.Controller()
        with controller.pressed(keyboard.Key.ctrl):
            controller.press('v')
            controller.release('v')
        time.sleep(0.05)

        pyperclip.copy(self.last_clipboard_content)

        if add_space:
            controller.press(keyboard.Key.space)
            controller.release(keyboard.Key.space)
        elif add_enter:
            controller.press(keyboard.Key.enter)
            controller.release(keyboard.Key.enter)

    def force_convert_word(self):
        """Принудительное преобразование слова"""
        if not self.current_word:
            return

        actual_word = self.build_actual_word()
        if self.contains_digits(actual_word):
            self.reset_counters()
            return

        primary_layout = self.current_word[0]['layout']

        self.processing_word = True

        try:
            controller = keyboard.Controller()
            if primary_layout == 'ru':
                en_word = self.convert_word(actual_word, 'ru', 'en')
                self.play_sound()
                controller.press(keyboard.Key.space)
                controller.release(keyboard.Key.space)
                self.delete_word()
                self.set_layout('us')
                self.insert_word(en_word)
            else:
                ru_word = self.convert_word(actual_word, 'en', 'ru')
                self.play_sound()
                controller.press(keyboard.Key.space)
                controller.release(keyboard.Key.space)
                self.delete_word()
                self.set_layout('ru')
                self.insert_word(ru_word)
        finally:
            self.processing_word = False
            self.reset_counters()

    def on_release(self, key):
        """Обработчик отпускания клавиш"""
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            self.ctrl_pressed = False

        if not self.active:
            return True

        # Обработка клавиши PB (Pause/Break)
        if key == keyboard.Key.pause and not self.block_processing:
            if not self.current_word:
                return True
            self.word_complete = True
            self.force_convert_word()
            return True

        if self.processing_word or key not in [keyboard.Key.space, keyboard.Key.enter]:
            return True

        if not self.current_word:
            return True

        # Проверка на однобуквенные слова ТОЛЬКО в английской раскладке
        en_to_ru_single_char = {
            'z': 'я', 'f': 'а', 'j': 'о', 'e': 'у',
            'b': 'и', 'd': 'в', 'r': 'к', 'c': 'с'
        }

        # Полный список русских однобуквенных слов, которые НЕ нужно трогать
        ru_single_chars = {'я', 'а', 'о', 'у', 'и', 'в', 'к', 'с'}

        if len(self.current_word) == 1 and not self.shift_pressed:
            char_data = self.current_word[0]
            actual_char = char_data['actual'].lower()

            # Если это английская раскладка и символ есть в маппинге
            if char_data['layout'] == 'us' and char_data['original'].lower() in en_to_ru_single_char:
                self.word_complete = True
                self.processing_word = True

                try:
                    ru_char = en_to_ru_single_char[char_data['original'].lower()]
                    if char_data['is_upper']:
                        ru_char = ru_char.upper()

                    self.play_sound()
                    self.delete_word()
                    self.set_layout('ru')
                    self.insert_word(ru_char, add_space=(key == keyboard.Key.space), add_enter=(key == keyboard.Key.enter))
                finally:
                    self.processing_word = False
                    self.reset_counters()
                return True

            # Если это русская раскладка и символ в списке исключений - пропускаем обработку
            elif char_data['layout'] == 'ru' and actual_char in ru_single_chars:
                self.reset_counters()
                return True

        # Остальная логика обработки слов
        self.word_complete = True
        actual_word = self.build_actual_word()

        # Проверяем, есть ли в слове цифры
        if self.contains_digits(actual_word):
            self.reset_counters()
            return True

        primary_layout = self.current_word[0]['layout']
        self.processing_word = True

        try:
            if primary_layout == 'ru':
                en_word = self.convert_word(actual_word, 'ru', 'en')
                if self.en_dict.check(en_word):
                    self.play_sound()
                    self.delete_word()
                    self.set_layout('us')
                    self.insert_word(en_word, add_space=(key == keyboard.Key.space), add_enter=(key == keyboard.Key.enter))
            else:
                ru_word = self.convert_word(actual_word, 'en', 'ru')
                if self.has_enough_vowels(ru_word, 'ru'):
                    self.play_sound()
                    self.delete_word()
                    self.set_layout('ru')
                    self.insert_word(ru_word, add_space=(key == keyboard.Key.space), add_enter=(key == keyboard.Key.enter))
        finally:
            self.processing_word = False
            self.reset_counters()
        return True

    def reset_counters(self):
        """Сброс состояния трекера"""
        self.letter_count = 0
        self.current_word = []
        self.word_complete = False
        self.last_clipboard_content = None

    def start(self):
        """Запуск слушателя клавиатуры"""
        print("Punto Switcher with vowel check")
        print("Press Pause/Break to force switch layout")
        print("Press Ctrl+Space to toggle program on/off")
        print("Press Esc to exit")
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as self.listener:
            self.listener.join()

if __name__ == "__main__":
    tracker = KeyTracker()
    tracker.start()
