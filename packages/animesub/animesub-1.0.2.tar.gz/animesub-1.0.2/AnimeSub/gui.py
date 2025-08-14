import os
import sys
import shutil
import threading
import logging
import webbrowser
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageEnhance

# Импортируем новую утилиту для настройки логирования
from animesub.utils import setup_logging, resource_path


# =============================
# 1. Константы и глобальные переменные
# =============================
LOGO_PATH = None
ICON_PATH = None
LOG_FILE_PATH = None  # Будет установлено при запуске

# Состояние приложения
is_running = False
cancel_event = None

# Основные элементы интерфейса (остаются глобальными для простоты)
root = None
input_entry = None
output_entry = None
model_choice = None
device_choice = None
start_btn = None
progress_bar = None
status_label = None

# Опциональные уведомления
try:
    from plyer import notification as plyer_notification
except ImportError:
    plyer_notification = None

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)


# =============================
# 2. Вспомогательные функции
# =============================

def find_ffmpeg() -> bool:
    """Проверка наличия ffmpeg."""
    if shutil.which("ffmpeg"):
        return True
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        local_ffmpeg = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            os.environ["PATH"] += os.pathsep + exe_dir
            return True
    return False

def notify_user(title: str, message: str, timeout: int = 5):
    """Отправляет уведомление, если возможно."""
    if plyer_notification:
        try:
            plyer_notification.notify(title=title, message=message, timeout=timeout)
        except Exception as e:
            logger.debug(f"Ошибка уведомления: {e}")

def show_error(title: str, message: str):
    """Показывает сообщение об ошибке."""
    logger.error(f"UI Error: {title} - {message}")
    if root:
        root.after(0, lambda: messagebox.showerror(title, message))

def finalize_ui(success: bool, message: str = ""):
    """Сбрасывает UI в исходное состояние."""
    global is_running
    is_running = False

    def _finalize():
        start_btn.configure(text="🚀 Transcribe", state="normal")
        if success:
            progress_bar.set(1.0)
            status_label.configure(text=message or "Готово")
        else:
            progress_bar.set(0)
            status_label.configure(text=message or "Отменено или произошла ошибка")

    if root:
        root.after(0, _finalize)

def open_log_directory():
    """Открывает папку с логами в системном файловом менеджере."""
    if LOG_FILE_PATH:
        log_dir = os.path.dirname(LOG_FILE_PATH)
        try:
            # webbrowser.open является кросс-платформенным способом
            webbrowser.open(f"file:///{log_dir}")
            logger.info(f"Открыта директория логов: {log_dir}")
        except Exception as e:
            show_error("Ошибка", f"Не удалось открыть папку с логами: {e}")
    else:
        show_error("Информация", "Лог-файл еще не создан.")


# =============================
# 3. Обработчики событий
# =============================

def choose_file_or_url():
    file_path = filedialog.askopenfilename()
    if file_path:
        input_entry.delete(0, "end")
        input_entry.insert(0, file_path)

def choose_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, "end")
        output_entry.insert(0, folder_path)

def start_or_cancel_transcription():
    global is_running, cancel_event
    if not is_running:
        cancel_event = threading.Event()
        is_running = True
        start_btn.configure(text="❌ Cancel")
        status_label.configure(text="Подготовка...")
        progress_bar.set(0)
        
        # Запускаем основной процесс в фоновом потоке
        threading.Thread(target=run_transcription, args=(cancel_event,), daemon=True).start()
    else:
        if cancel_event:
            logger.warning("Пользователь запросил отмену процесса.")
            cancel_event.set()
        start_btn.configure(state="disabled", text="Отмена...")
        status_label.configure(text="Процесс отменяется...")

def run_transcription(current_cancel_event):
    """Обертка для запуска процесса транскрипции в фоне."""
    from animesub.main_logic import process_audio
    
    
    # Флаг для отслеживания успешности
    was_successful = False
    final_message = "Процесс завершен."

    def report_progress(progress_value, status_message):
        # Эта функция будет вызываться из другого потока, поэтому используем root.after
        def _update_gui():
            if current_cancel_event.is_set():
                return
            progress_bar.set(progress_value)
            status_label.configure(text=status_message)
            
        if root:
            root.after(0, _update_gui)

    try:
        input_path = input_entry.get().strip()
        output_folder = output_entry.get().strip() or os.getcwd()
        model_name = model_choice.get()
        device = "cuda" if device_choice.get() == "GPU CUDA" else "cpu"

        if not find_ffmpeg():
            show_error("Ошибка", "FFmpeg не найден! Убедитесь, что ffmpeg.exe находится в папке с программой или в системном PATH.")
            finalize_ui(success=False, message="Ошибка: FFmpeg не найден")
            return
        
        url = None
        output_path = None
        if input_path.startswith(("http://", "https://")):
            url = input_path
            # Имя выходного файла будет определено после скачивания в main_logic
            output_path = output_folder 
        elif not input_path:
            show_error("Ошибка", "Не указан путь к файлу или URL.")
            finalize_ui(success=False, message="Ошибка: нет входа")
            return
        else:
            if not os.path.exists(input_path):
                show_error("Ошибка", f"Файл не найден: {input_path}")
                finalize_ui(success=False, message="Ошибка: файл не найден")
                return
            file_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_folder, f"{file_name}.srt")

        # Вызываем основную логику
        process_audio(
            input_path=input_path if not url else None,
            output_path=output_path,
            model_name=model_name,
            device=device,
            url=url,
            progress_callback=report_progress,
            cancel_event=current_cancel_event
        )
        
        # Проверяем, была ли отмена в процессе
        if current_cancel_event.is_set():
            final_message = "Отменено пользователем."
            was_successful = False
        else:
            final_message = "Транскрибация успешно завершена!"
            was_successful = True
            notify_user("Kataribe", final_message, timeout=5)

    except Exception as e:
        # Логгер уже перехватит это через excepthook, но мы также покажем ошибку пользователю
        final_message = "Произошла критическая ошибка."
        show_error("Критическая ошибка", f"{e}\n\nПодробности смотрите в лог-файле.")
        was_successful = False
    finally:
        finalize_ui(success=was_successful, message=final_message)


def switch_theme():
    ctk.set_appearance_mode("dark" if theme_switch_var.get() else "light")


# =============================
# 4. Инициализация GUI
# =============================

def init_gui():
    global root, input_entry, output_entry, model_choice, device_choice
    global start_btn, progress_bar, status_label, theme_switch_var

    root = ctk.CTk()
    root.title("Kataribe v1.0")
    if os.path.exists(ICON_PATH):
        try:
            root.iconbitmap(ICON_PATH)
        except Exception:
            logger.debug(f"Не удалось установить иконку: {ICON_PATH}", exc_info=True)
    root.geometry("620x540")
    ctk.set_appearance_mode("dark")

    # --- Верхняя панель ---
    top_bar = ctk.CTkFrame(root, fg_color="transparent")
    top_bar.pack(fill="x", pady=5, padx=5)
    
    ctk.CTkButton(top_bar, text="📂 Open Logs", command=open_log_directory, width=100).pack(side="left", padx=5)
    
    theme_switch_var = ctk.BooleanVar(value=True)
    ctk.CTkSwitch(top_bar, variable=theme_switch_var, command=switch_theme, text="").pack(side="right")
    ctk.CTkLabel(top_bar, text="Theme", text_color='gray', font=("Segoe UI", 12)).pack(side="right", padx=(0, 3))

    ctk.CTkLabel(root, text="KATARIBE", font=("Segoe UI", 28, "bold"), text_color="#58c68b").pack(pady=(0, 5))
    ctk.CTkLabel(root, text="Media Transcribing Tool", font=("Segoe UI", 14), text_color="gray").pack(pady=(0, 15))

    # --- Фреймы ввода/вывода ---
    input_frame = ctk.CTkFrame(root, corner_radius=10)
    input_frame.pack(pady=10, fill="x", padx=20)
    input_entry = ctk.CTkEntry(input_frame, placeholder_text="Path or URL", height=35)
    input_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
    ctk.CTkButton(input_frame, text="📁", width=40, command=choose_file_or_url).pack(side="left", padx=(5, 5), pady=5)

    output_frame = ctk.CTkFrame(root, corner_radius=10)
    output_frame.pack(pady=10, fill="x", padx=20)
    output_entry = ctk.CTkEntry(output_frame, placeholder_text="Output folder (current by default)", height=35)
    output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
    ctk.CTkButton(output_frame, text="📁", width=40, command=choose_output_folder).pack(side="left", padx=(5, 5), pady=5)

    # --- Фрейм опций ---
    options_frame = ctk.CTkFrame(root, corner_radius=10)
    options_frame.pack(pady=10, fill="x", padx=20)
    ctk.CTkLabel(options_frame, text="Model", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
    ctk.CTkLabel(options_frame, text="Device", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(5, 0))

    model_choice = ctk.CTkOptionMenu(options_frame,
                                     values=["large-v3", "large-v2", "medium", "small", "base", "tiny",
                                             "kotoba-faster", "kotoba-whisper-v2.2", "kotoba-whisper"], height=35)
    model_choice.set("large-v3")
    model_choice.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    device_choice = ctk.CTkOptionMenu(options_frame, values=["GPU CUDA", "CPU"], height=35)
    device_choice.set("GPU CUDA")
    device_choice.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
    options_frame.grid_columnconfigure((0, 1), weight=1)

    # --- Кнопка старта и прогресс ---
    start_btn = ctk.CTkButton(root, text="🚀 Transcribe", command=start_or_cancel_transcription,
                              height=40, font=("Segoe UI", 14, "bold"))
    start_btn.pack(pady=15, padx=20, fill="x")

    progress_bar = ctk.CTkProgressBar(root, height=12, progress_color='#58c68b')
    progress_bar.pack(fill="x", padx=20, pady=(0, 5))
    progress_bar.set(0)
    status_label = ctk.CTkLabel(root, text="Ready", font=("Segoe UI", 12), text_color='gray')
    status_label.pack(pady=(0, 15))

    ctk.CTkLabel(root, text="by @iniquitousworld @shim0neta", font=("Segoe UI", 10, "italic"),
                 text_color="#888888").pack(side="bottom", pady=8)


# =============================
# 5. Splash screen (без изменений)
# =============================
def show_splash():
    # ... код splash screen оставлен без изменений ...
    splash = ctk.CTk()
    splash.geometry("380x250")
    splash.overrideredirect(True)
    splash.title("Loading...")
    splash.attributes("-topmost", True)
    splash.update_idletasks()
    w = splash.winfo_screenwidth()
    h = splash.winfo_screenheight()
    size = tuple(int(_) for _ in splash.geometry().split('+')[0].split('x'))
    x = w // 2 - size[0] // 2
    y = h // 2 - size[1] // 2
    splash.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        enhancer = ImageEnhance.Brightness(logo)
        logo_light = enhancer.enhance(1.4)
        logo_img = ctk.CTkImage(light_image=logo_light, dark_image=logo_light, size=(100, 100))
        ctk.CTkLabel(splash, image=logo_img, text="").pack(pady=(30, 5))
    except Exception as e:
        # Логируем, если не удалось загрузить лого
        logger.warning(f"Ошибка загрузки логотипа: {e}")
    ctk.CTkLabel(splash, text="KATARIBE", font=("Segoe UI", 32, "bold"), text_color="#2CDB81").pack()
    ctk.CTkLabel(splash, text="Loading...", font=("Segoe UI", 12), text_color="#525954").pack(pady=(5, 0))
    splash.after(2000, lambda: start_main_app(splash)) # Увеличил задержку для "эффекта"
    splash.mainloop()

# =============================
# 6. main()
# =============================
def start_main_app(splash_window):
    splash_window.destroy()
    init_gui()
    root.mainloop()

if __name__ == "__main__":
    # Настраиваем логирование ПЕРЕД созданием любого окна
    LOG_FILE_PATH = setup_logging()
    # Настраиваем пути до иконок
    LOGO_PATH = resource_path(r"assets\micon.png")
    ICON_PATH = resource_path(r"assets\micon.ico")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    # Рекомендуется запускать GUI в основном потоке
    show_splash()