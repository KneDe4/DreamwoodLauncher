import minecraft_launcher_lib
import subprocess
import uuid
import os
import json
import shutil
import sys
import threading
import mods

appdata = os.getenv('APPDATA')
minecraft_dir = os.path.join(appdata, ".PiLauncher")
os.makedirs(minecraft_dir, exist_ok=True)

FORGE_VERSION = "1.20.1-forge-47.4.16"
MINECRAFT_VERSION = "1.20.1-47.4.16"


DEFAULT_SERVER = "dreamwoodhouse.sosal.today"
MAX_SERVERS = 1


MODS_API_URL = "https://your-server.com/api/mods/version"
MODS_DOWNLOAD_URL = "https://your-server.com/downloads/mods.zip"


def setup_mods_downloader():

    mods.configure({
        'api': MODS_API_URL,
        'download': MODS_DOWNLOAD_URL
    })


def is_forge_installed():

    return os.path.exists(os.path.join(minecraft_dir, "versions", FORGE_VERSION))


def install_forge():

    print(f"Forge {FORGE_VERSION}...")
    try:
        minecraft_launcher_lib.forge.install_forge_version(MINECRAFT_VERSION, minecraft_dir)
        print("Forge ystanovlen")
        return True
    except Exception as e:
        print(f"osibka Forge: {e}")
        return False


def cleanup_servers():

    servers_dat = os.path.join(minecraft_dir, "servers.dat")

    try:
        from pynbt import NBTFile, TAG_Compound, TAG_List, TAG_String, TAG_Byte

        my_servers = [
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},
            {"name": "Dreamwood House", "ip": "dreamwoodhouse.sosal.today"},

        ]

        servers_list = []
        for server in my_servers[:MAX_SERVERS]:
            servers_list.append(TAG_Compound({
                "name": TAG_String(server['name']),
                "ip": TAG_String(server['ip']),
                "icon": TAG_String(""),
                "acceptTextures": TAG_Byte(1)
            }))

        nbt = NBTFile(value={"servers": TAG_List(TAG_Compound, servers_list)})

        with open(servers_dat, 'wb') as f:
            nbt.save(f)

        print(f"servers.dat")
        return True

    except Exception as e:
        print(f"❌: {e}")
        return False


def set_russian_language():

    options_file = os.path.join(minecraft_dir, "options.txt")
    try:
        options = {}

        if os.path.exists(options_file):
            with open(options_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        options[key] = value

        options['lang'] = 'ru_ru'
        options['lastServer'] = 'dreamwoodhouse.sosal.today'

        with open(options_file, 'w', encoding='utf-8') as f:
            for key, value in options.items():
                f.write(f"{key}:{value}\n")

        print("язык ")
        return True
    except Exception as e:
        print(f"error yasik: {e}")
        return False


def read_minecraft_output(process):
    for line in process.stdout:
        print(f"[MINECRAFT] {line.rstrip()}")
    for line in process.stderr:
        print(f"[MINECRAFT ERROR] {line.rstrip()}")


def start_minecraft(username, min_ram, max_ram):

    setup_mods_downloader()

    print("модо...")
    try:
        mods.download_mods(minecraft_dir, force=False)
    except Exception as e:
        print(f"ощибк модов: {e}")


    if not is_forge_installed():
        print("Forge не")
        if not install_forge():
            return False

    if is_forge_installed():
        print('Запусек миникрафта')


        set_russian_language()


        try:
            cleanup_servers()
        except:
            print('очистке серверов')

        try:
            min_ram = int(min_ram)
            max_ram = int(max_ram)

            jvm_args = [
                f'-Xmx{max_ram}G',
                f'-Xms{min_ram}G',
                '-Duser.language=ru',
                '-Duser.country=RU'
            ]

            options = {
                'username': username,
                'uuid': str(uuid.uuid4()),
                'token': '',
                'jvmArguments': jvm_args
            }

            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                FORGE_VERSION,
                minecraft_dir,
                options
            )

            process = subprocess.Popen(
                minecraft_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8'
            )

            print(f"запущен с RAM: {min_ram}G - {max_ram}G")
            print(f"умолчанию: {DEFAULT_SERVER}")
            print("-" * 50)

            thread = threading.Thread(target=read_minecraft_output, args=(process,))
            thread.daemon = True
            thread.start()

            return True

        except Exception as e:
            print(f"ошибка запуска Minecraft: {e}")
            return False
    else:
        print("ошибка: Forge не установлен")
        return False


class Minecraft:
    @staticmethod
    def Start(username, min_ram, max_ram):
        return start_minecraft(username, min_ram, max_ram)



def force_update_mods():
    setup_mods_downloader()
    return mods.download_mods(minecraft_dir, force=True)



def check_mods_status():
    downloader = mods.ModsDownloader(minecraft_dir)
    current = downloader.get_current_mods_version()
    server = downloader.check_server_mods_version()

    print(f"версия модов: {current}")
    print(f"версия на сервере: {server}")

    mods_list = downloader.get_mods_list()
    print(f"установлено модов: {len(mods_list)}")
    for mod in mods_list:
        print(f"  - {mod}")

    return {
        'current_version': current,
        'server_version': server,
        'mods_count': len(mods_list),
        'needs_update': server > current if server else False
    }