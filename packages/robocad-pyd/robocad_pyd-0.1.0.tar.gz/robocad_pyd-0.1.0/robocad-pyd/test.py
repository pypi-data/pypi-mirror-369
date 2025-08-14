import pygame
import sys
import time
import os
import subprocess
import threading
from robocad.studica import RobotVmxTitan

# Инициализация робота и Pygame
robot = RobotVmxTitan(False)
pygame.init()
screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)
pygame.display.set_caption("")
time.sleep(1)

# Константы
BASE_SPEED = 30
RECORD_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "robot_trajectory.py")
RECORD_KEY = pygame.K_r
STOP_KEY = pygame.K_f
PLAY_KEY = pygame.K_p
QUIT_KEY = pygame.K_q

# Состояния управления
KEY_STATE = {
    pygame.K_w: False,
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False
}


class RobotRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.events = []
        self.start_time = 0
        self.last_speeds = (0, 0)
        self.last_event_time = 0
        self.keys_changed = False  # Флаг изменения состояния клавиш

    def get_motor_speeds(self):
        """Вычисление скоростей моторов на основе нажатых клавиш"""
        left_speed = 0
        right_speed = 0

        # Комбинации клавиш
        if KEY_STATE[pygame.K_w]:  # Вперед
            left_speed += BASE_SPEED
            right_speed -= BASE_SPEED
        if KEY_STATE[pygame.K_s]:  # Назад
            left_speed -= BASE_SPEED
            right_speed += BASE_SPEED
        if KEY_STATE[pygame.K_a]:  # Влево
            left_speed -= BASE_SPEED
            right_speed -= BASE_SPEED
        if KEY_STATE[pygame.K_d]:  # Вправо
            left_speed += BASE_SPEED
            right_speed += BASE_SPEED

        # Ограничение скоростей
        left_speed = max(min(left_speed, 100), -100)
        right_speed = max(min(right_speed, 100), -100)

        return left_speed, right_speed

    def start_recording(self):
        """Начало записи траектории"""
        if not self.recording:
            self.recording = True
            self.events = []
            self.start_time = time.time()
            self.last_event_time = self.start_time
            self.last_speeds = (0, 0)
            print("Начало записи траектории...")

            # Запись начального состояния
            self.record_snapshot(0.0)

    def stop_recording(self):
        """Остановка записи и сохранение в автономный скрипт"""
        if self.recording:
            self.recording = False
            # Добавляем событие остановки в конец
            current_time = time.time() - self.start_time
            self.record_snapshot(current_time)
            self.save_to_python_script()
            print(f"Автономный скрипт сохранен в {RECORD_FILE}")

    def record_snapshot(self, timestamp):
        """Запись состояния движения - ТОЛЬКО СКОРОСТИ"""
        event = {
            'time': timestamp,
            'left_speed': self.last_speeds[0],
            'right_speed': self.last_speeds[1]
        }
        self.events.append(event)

    def save_to_python_script(self):
        """Сохранение траектории в автономный Python-скрипт"""
        with open(RECORD_FILE, 'w', encoding='utf-8') as f:
            # Заголовок скрипта
            f.write("#!/usr/bin/env python\n")
            f.write("# -*- coding: utf-8 -*-\n\n")
            f.write("import time\n")
            f.write("from robocad.studica import RobotVmxTitan\n\n")

            f.write("def main():\n")
            f.write("    robot = RobotVmxTitan(False)  # Используем реального робота\n")
            f.write("    events = [\n")
            for event in self.events:
                # Сохраняем только необходимые для движения данные
                f.write(
                    f"        {{'time': {event['time']}, 'left_speed': {event['left_speed']}, 'right_speed': {event['right_speed']}}},\n")
            f.write("    ]\n\n")

            # Реальное ожидание кнопки старт
            f.write("    print(\"Ожидание кнопки старт...\")\n")
            f.write("    while not robot.vmx_flex[1]:\n")
            f.write("        time.sleep(0.1)\n")
            f.write("    print(\"Начало воспроизведения...\")\n\n")

            f.write("    start_time = time.time()\n")
            f.write("    prev_left, prev_right = 0, 0\n")
            f.write("    \n")
            f.write("    for event in events:\n")
            f.write("        t = event['time']\n")
            f.write("        elapsed = time.time() - start_time\n")
            f.write("        if elapsed < t:\n")
            f.write("            time.sleep(t - elapsed)\n")
            f.write("        \n")
            f.write("        # Устанавливаем скорости на реального робота\n")
            f.write("        left_speed = event['left_speed']\n")
            f.write("        right_speed = event['right_speed']\n")
            f.write("        if left_speed != prev_left or right_speed != prev_right:\n")
            f.write("            robot.motor_speed_0 = left_speed\n")
            f.write("            robot.motor_speed_1 = right_speed\n")
            f.write("            prev_left, prev_right = left_speed, right_speed\n")
            f.write("    \n")
            f.write("    # Остановка в конце воспроизведения\n")
            f.write("    robot.motor_speed_0 = 0\n")
            f.write("    robot.motor_speed_1 = 0\n")
            f.write("    print(\"Воспроизведение завершено!\")\n\n")
            f.write("if __name__ == \"__main__\":\n")
            f.write("    main()\n")

    def play_recording(self):
        """Запуск автономного скрипта в отдельном процессе"""
        if not self.playing and os.path.exists(RECORD_FILE):
            self.playing = True
            print("Запуск автономного скрипта...")

            def run_script():
                try:
                    # Останавливаем текущее управление роботом
                    robot.motor_speed_0 = 0
                    robot.motor_speed_1 = 0
                    subprocess.run([sys.executable, RECORD_FILE], check=True)
                except Exception as e:
                    print(f"Ошибка при запуске скрипта: {e}")
                finally:
                    self.playing = False

            # Запуск в отдельном потоке
            thread = threading.Thread(target=run_script)
            thread.daemon = True
            thread.start()

    def update(self):
        """Обновление состояния записи"""
        current_speeds = self.get_motor_speeds()

        # Немедленная реакция на изменение состояния клавиш
        if self.keys_changed:
            self.keys_changed = False
            # Применяем новые скорости к роботу
            if not self.playing:
                robot.motor_speed_0 = current_speeds[0]
                robot.motor_speed_1 = current_speeds[1]

            # При записи немедленно фиксируем изменения
            if self.recording:
                current_time = time.time() - self.start_time
                self.last_speeds = current_speeds
                self.last_event_time = current_time
                self.record_snapshot(current_time)

        # Стандартное обновление при записи (каждые 0.05 сек)
        elif self.recording:
            current_time = time.time() - self.start_time
            # Записываем изменения каждые 0.05 секунд или при изменении скорости
            if (current_time - self.last_event_time >= 0.05 or
                    current_speeds != self.last_speeds):
                self.last_speeds = current_speeds
                self.last_event_time = current_time
                self.record_snapshot(current_time)

        # Стандартное управление роботом
        elif not self.playing:
            robot.motor_speed_0 = current_speeds[0]
            robot.motor_speed_1 = current_speeds[1]

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    KEY_STATE[event.key] = True
                    self.keys_changed = True  # Флаг изменения состояния

                elif event.key == RECORD_KEY:
                    self.start_recording()

                elif event.key == STOP_KEY:
                    self.stop_recording()

                elif event.key == PLAY_KEY:
                    self.play_recording()

                elif event.key == QUIT_KEY:
                    return False

            # Обработка отпускания клавиш
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    KEY_STATE[event.key] = False
                    self.keys_changed = True  # Флаг изменения состояния

        return True


# Основная программа
def main():
    recorder = RobotRecorder()

    # Ждет нажатия на кнопку старт
    print("Ожидание кнопки старт...")
    while not robot.vmx_flex[1]:
        time.sleep(0.1)

    try:
        running = True
        while running:
            running = recorder.handle_events()
            recorder.update()

            # Статус в консоли
            if recorder.recording:
                status = f"[REC] Events: {len(recorder.events)}"
            elif recorder.playing:
                status = "[PLAY]"
            else:
                status = "[READY]"

            # Отображение активных клавиш
            active_keys = []
            if KEY_STATE[pygame.K_w]: active_keys.append("W")
            if KEY_STATE[pygame.K_a]: active_keys.append("A")
            if KEY_STATE[pygame.K_s]: active_keys.append("S")
            if KEY_STATE[pygame.K_d]: active_keys.append("D")

            keys_status = ' '.join(active_keys) if active_keys else 'None'
            print(f"{status} | Keys: {keys_status}", end="\r")

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        # Гарантированная остановка при завершении
        print("\nЗавершение работы...")
        robot.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()