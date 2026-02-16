# mods.py
import os
import requests
import json
import zipfile
import shutil
from pathlib import Path
import sys
import subprocess


class ModsDownloader:
    def __init__(self, minecraft_dir):

        self.minecraft_dir = Path(minecraft_dir)
        self.mods_dir = self.minecraft_dir / 'mods'
        self.version_file = self.minecraft_dir / 'mods_version.json'


        self.api_url = "https://pililteam.ru/lanc/version.txt"
        self.download_url = "https://pililteam.ru/lanc/mods.zip"
        self.mods_dir.mkdir(parents=True, exist_ok=True)

    def get_current_mods_version(self):

        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.0')
            except:
                return '0.0.0'
        return '0.0.0'

    def check_server_mods_version(self):

        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                return response.json().get('version')
        except Exception as e:
            print(f"ошибка проверки модов: {e}")
        return None

    def download_file(self, url, save_path):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)


            return True
        except Exception as e:
            print(f"ошиб при скачивании: {e}")
            return False

    def extract_zip(self, zip_path, extract_to):

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            print(f"ошибка при распаковке: {e}")
            return False

    def cleanup_old_mods(self):
        try:
            # удаляем все .jar
            for jar_file in self.mods_dir.glob('*.jar'):
                jar_file.unlink()
            for item in self.mods_dir.iterdir():
                if item.is_file() and item.suffix != '.json':
                    item.unlink()
            print("моды удалены")
            return True
        except Exception as e:
            print(f"при очистке модов: {e}")
            return False

    def save_mods_version(self, version):
        with open(self.version_file, 'w') as f:
            json.dump({'version': version}, f)

    def download_mods(self, force=False):

        current_version = self.get_current_mods_version()
        print(f" версия модов: {current_version}")

        if not force:
            server_version = self.check_server_mods_version()
            if not server_version:
                print("не удалось проверить версию модов на сервере")
                return False

            print(f"версия модов на сервере: {server_version}")

            if server_version <= current_version:
                print("моды уже последней версии")
                return True
        else:
            server_version = "forced_update"
            print(" обновление модов...")


        zip_path = self.minecraft_dir / 'mods_temp.zip'


        if not self.download_file(self.download_url, zip_path):
            print("ош при скачивании модов")
            return False


        self.cleanup_old_mods()



        if not self.extract_zip(zip_path, self.mods_dir):
            print("ош при распаковке модов")
            zip_path.unlink()
            return False


        zip_path.unlink()


        if not force:
            self.save_mods_version(server_version)


        mods_count = len(list(self.mods_dir.glob('*.jar')))
        print(f"установлено {mods_count} модов")

        return True

    def get_mods_list(self):

        mods = []
        for mod_file in self.mods_dir.glob('*.jar'):
            mods.append(mod_file.name)
        return mods

    def download_single_mod(self, mod_url, mod_name):

        mod_path = self.mods_dir / mod_name
        return self.download_file(mod_url, mod_path)



def download_mods(minecraft_dir, force=False):
    downloader = ModsDownloader(minecraft_dir)
    return downloader.download_mods(force)



def configure(urls_dict):
    global MODS_API_URL, MODS_DOWNLOAD_URL
    if 'api' in urls_dict:
        MODS_API_URL = urls_dict['api']
    if 'download' in urls_dict:
        MODS_DOWNLOAD_URL = urls_dict['download']