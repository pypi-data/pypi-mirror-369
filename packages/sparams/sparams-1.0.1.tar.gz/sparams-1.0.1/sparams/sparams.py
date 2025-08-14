from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import yaml
import sys

ignor_config = ["app_name", "module_name", "config",'filename','is_writting']

def resource_path(relative_path):
    # Dùng để lấy đường dẫn file đúng khi chạy cả trong PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class ConfigObject:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, base_params, filename):
        self.base_params = base_params
        self.filename = filename

    def on_modified(self, event):
        if event.src_path.endswith(self.filename):
            print(f"[INFO] Detected change in {self.filename}, reloading config...")
            self.base_params.reload_config()

class BaseParams:
    def __init__(self, app_name, module_name):
        self.app_name = app_name
        self.module_name = module_name
        self.filename = f"{self.app_name}.yaml"
        # Khởi động watchdog để theo dõi file
        self.start_file_watcher()
        self.is_writting = False

    def create_or_load_yaml(self):
        # self.sync_config_back()
        filename = self.filename

        default_data = {
            k: v for k, v in self.__dict__.items()
            if k not in ignor_config
        }

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                full_config = yaml.safe_load(f) or {}
            print(f"[INFO] Loaded existing config from: {filename}")
        else:
            full_config = {}
            print(f"[INFO] Config file not found. Creating new: {filename}")

        module_config = full_config.get(self.module_name, {})
        updated = False

        # Gán lại giá trị từ YAML vào self (load từ file)
        keys_to_remove = []
        for key, value in module_config.items():
            if key in default_data:
                setattr(self, key, value)
            else:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del module_config[key]
            updated = True
            print(f"[INFO] Removed invalid key '{key}' from module '{self.module_name}'")

        # Thêm các key mới từ class vào module config nếu chưa có (merge ngược lại)
        for key, value in default_data.items():
            if key not in module_config:
                module_config[key] = value
                updated = True
                print(f"[INFO] Added missing key '{key}' to module '{self.module_name}'")

        full_config[self.module_name] = module_config

        if updated or not os.path.exists(filename):
            with open(filename, 'w') as f:
                yaml.dump(full_config, f,sort_keys=False)
            print(f"[INFO] Saved updated config to: {filename}")

        return ConfigObject(module_config)

    def reload_config(self):
        print("[INFO] Reloading config from file...")
        self.config = self.create_or_load_yaml()

    def start_file_watcher(self):
        event_handler = ConfigWatcher(self, self.filename)
        observer = Observer()
        observer.schedule(event_handler, ".", recursive=False)
        observer_thread = threading.Thread(target=observer.start, daemon=True)
        observer_thread.start()
    
    def save_to_config_file(self):
        """
        Ghi toàn bộ config hiện tại vào một file tạm, xóa file cũ và đổi tên file tạm thành file gốc.
        """
        try:
            temp_filename = self.filename + ".tmp"

            # Tạo dữ liệu để ghi ra file
            full_config = {}
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    full_config = yaml.safe_load(f) or {}

            module_config = {
                k: v for k, v in self.__dict__.items()
                if k not in ignor_config
            }

            full_config[self.module_name] = module_config

            # Ghi vào file tạm
            with open(temp_filename, 'w') as f:
                yaml.dump(full_config, f, sort_keys=False)
            print(f"[INFO] Ghi config tạm vào {temp_filename}")

            # Xóa file gốc và đổi tên file tạm
            os.remove(self.filename)
            os.rename(temp_filename, self.filename)
            print(f"[INFO] Ghi config an toàn thành công vào {self.filename}")

        except Exception as e:
            print(f"[ERROR] Lỗi khi ghi config an toàn: {e}")
    

