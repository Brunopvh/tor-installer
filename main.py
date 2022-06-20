#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path
from argparse import ArgumentParser

__version__ = '1.1'
__appname__ = 'tor-installer'
__script__ = os.path.abspath(__file__)
dir_of_project = os.path.dirname(__script__)

sys.path.insert(0, dir_of_project)


from conflib import (
    KERNEL_TYPE,
    get_abspath,
    get_user_home,
    mkdir,
    rmdir,
    download_file,
    File,
    FileReader,
    FileJson,
    BuilderAppDirs,
    BuilderUserDirs,
    UserDirs, 
    AppDirs,
    PackageApp,
    PackageTarGz,
    PackageWinExe,
)

user_dirs: UserDirs = BuilderUserDirs().build_user_root(False).build()
tor_installer_app_dirs: AppDirs = BuilderAppDirs().build_user_root(False).build_appname(__appname__).build()



class TorBrowserLinux(PackageTarGz):
    def __init__(self, appname: str, appfile: str, save_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)
        self.dir_package_files = None

    def install(self):
        if Path(self.app_dirs.appdir()).exists():
            print(f'Remova a instalação atual do {self.app_dirs.appname} em ... {self.app_dirs.appdir()}')
            return False

        self.unpack()
        os.chdir(self.app_dirs.get_temp_dir())
        
        print(f'Copiando arquivos para ... {self.app_dirs.appdir()}')
        shutil.copytree(self.dir_package_files, self.app_dirs.appdir())
        os.chdir(self.app_dirs.appdir())
        os.system('chmod +x ./start-tor-browser.desktop')
        os.system('./start-tor-browser.desktop --register-app')

    def uninstall(self):
        #print(f'Desinstalando ... {self.app_dirs.appname}')
        rmdir(self.app_dirs.appdir())
        



class TorBrowserWindows(PackageWinExe):
    def __init__(self, appname: str, appfile: str, save_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)



class BuilderTorBrowser(object):
    def __init__(self) -> None:
        self._save_dir = tor_installer_app_dirs.app_cache_dir() 
        self._appname = 'torbrowser'

        if KERNEL_TYPE == 'Linux':
            self._url = 'https://www.torproject.org/dist/torbrowser/11.0.14/tor-browser-linux64-11.0.14_pt-BR.tar.xz'
            self._appfile = 'tor-browser-linux64-11.0.14_pt-BR.tar.xz'
            self._hash = '380bd310e55ca10622fb9aac2e013d7cc38c1619201780b761919f32fe0e7486'
            self._dir_project_files = 'tor-browser_pt-BR'
        elif KERNEL_TYPE == 'Windows':
            self._url = 'https://www.torproject.org/dist/torbrowser/11.0.14/torbrowser-install-win64-11.0.14_pt-BR.exe'
            self._appfile = 'torbrowser-install-win64-11.0.14_pt-BR.exe'
            self._hash = '3f2f67525d964ee86b42d78eec23baa05afc628d0610ad68027cf6a0f9a52a3d'
   
    def build_save_dir(self, save_dir):
        self._save_dir = save_dir
        return self

    def build_hash(self, hash):
        self._hash = hash
        return self

    def build(self) -> PackageApp:
        
        if KERNEL_TYPE == 'Linux':
            tb: PackageTarGz = TorBrowserLinux(self._appname, self._appfile, self._save_dir)
            tb.dir_package_files = self._dir_project_files
        elif KERNEL_TYPE == 'Windows':
            tb: PackageWinExe = PackageWinExe(self._appname, self._appfile, self._save_dir)
        else:
            print(f'{__class__.__name__} ERRO sistema não suportado')
            sys.exit(1)
        
        tb.hash = self._hash
        tb.url = self._url
        return tb


class CommandApp(object):
    def __init__(self) -> None:
        pass

    def execute(self):
        pass


class CommandDownloadApp(CommandApp):
    def __init__(self, app: PackageApp) -> None:
        super().__init__()
        self.app: PackageApp = app

    def execute(self):
        #print(f'[BAIXANDO] ... {self.app.app_dirs.appname}')
        return self.app.download()


class CommandInstallApp(CommandApp):
    def __init__(self, app: PackageApp) -> None:
        super().__init__()
        self.app: PackageApp = app

    def execute(self):
        print(f'[CHECANDO] ... {self.app.app_dirs.appname}', end=' ')
        sys.stdout.flush()
        if not self.app.verify():
            print(f'FALHA')
            return False
        print('OK') 
        #print(f'[INSTALANDO] ... {self.app.app_dirs.appname}')
        return self.app.install()


class CommandUninstallApp(CommandApp):
    def __init__(self, app: PackageApp) -> None:
        super().__init__()
        self.app: PackageApp = app

    def execute(self):
        print(f'[DESINSTALANDO] ... {self.app.app_dirs.appname}')
        return self.app.uninstall()


class ExecuteCommands(object):
    def __init__(self) -> None:
        self._commands: list = []

    def add_command(self, command: CommandApp):
        self._commands.append(command)

    def run(self):
        command: CommandApp = None
        for command in self._commands:
            command.execute()



def main():

    parser = ArgumentParser()

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
    )

    parser.add_argument(
        '-i', '--install',
        action='store_true',
        dest='install_tor',
        help='Instalar o Navegador Tor.'
    )

    parser.add_argument(
        '-u', '--uninstall',
        action='store_true',
        dest='uninstall_tor',
        help='Desinstalar o Navegador Tor.'
    )


    args = parser.parse_args()
     
    tor_app: PackageApp = BuilderTorBrowser().build()
    execute_commands = ExecuteCommands()

    if args.install_tor:
        mkdir(tor_app.save_dir)

        cmd_download = CommandDownloadApp(tor_app)
        cmd_install = CommandInstallApp(tor_app)
        
        execute_commands.add_command(cmd_download)
        execute_commands.add_command(cmd_install)
        execute_commands.run()
            
    elif args.uninstall_tor:
        cmd_uninstall = CommandUninstallApp(tor_app)
        execute_commands.add_command(cmd_uninstall)
        execute_commands.run()

   

if __name__ == '__main__':
    main()
