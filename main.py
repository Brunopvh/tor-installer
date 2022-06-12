#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path
from argparse import ArgumentParser

try:
    import wget
except Exception as e:
    print(e)
    sys.exit(1)


__version__ = '1.0'
__script__ = os.path.abspath(__file__)
dir_of_project = os.path.dirname(__script__)

sys.path.insert(0, dir_of_project)


from conflib import (
    KERNEL_TYPE,
    get_abspath,
    get_user_home,
    mkdir,
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
app_dirs: AppDirs = BuilderAppDirs().build_user_root(False).build_appname('tor-browser-installer').build()



class TorBrowserLinux(PackageTarGz):
    def __init__(self, pkgname: str, pkgfile: str, save_dir: str, temp_dir: str) -> None:
        super().__init__(pkgname, pkgfile, save_dir, temp_dir)
        self.app_dirs_tor_browser: AppDirs = BuilderAppDirs().build_appname('torbrowser').build_user_root(False).build()

    def install(self):
        if Path(self.app_dirs_tor_browser.appdir()).exists():
            shutil.rmtree(self.app_dirs_tor_browser.appdir())

        self.unpack()
        os.chdir(self.temp_dir)


        for _dir in os.listdir('.'):
            if 'tor-browser' in _dir:
                #os.chdir(_dir)
                src_dir =  _dir
                break

        print(f'Copiando arquivos para ... {self.app_dirs_tor_browser.appdir()}')
        shutil.copytree(src_dir, self.app_dirs_tor_browser.appdir())
        os.chdir(self.app_dirs_tor_browser.appdir())
        os.system('chmod +x ./start-tor-browser.desktop')
        os.system('./start-tor-browser.desktop --register-app')

    def uninstall(self):
        if os.path.exists(self.app_dirs_tor_browser.appdir()):
            shutil.rmtree(self.app_dirs_tor_browser.appdir())


class TorBrowserWindows(PackageWinExe):
    def __init__(self, pkgname: str, pkgfile: str, save_dir: str) -> None:
        super().__init__(pkgname, pkgfile, save_dir)




class BuilderTorBrowser(object):
    def __init__(self) -> None:
        
        self._save_dir = app_dirs.app_cache_dir() 
        self._temp_dir = user_dirs.temp_dir()
        self._pkgname = 'torbrowser'

        if KERNEL_TYPE == 'Linux':
            self._url = 'https://www.torproject.org/dist/torbrowser/11.0.14/tor-browser-linux64-11.0.14_pt-BR.tar.xz'
            self._pkgfile = 'tor-browser-linux64-11.0.14_pt-BR.tar.xz'
            self._hash = '380bd310e55ca10622fb9aac2e013d7cc38c1619201780b761919f32fe0e7486'
        elif KERNEL_TYPE == 'Windows':
            self._url = 'https://www.torproject.org/dist/torbrowser/11.0.14/torbrowser-install-win64-11.0.14_pt-BR.exe'
            self._pkgfile = 'torbrowser-install-win64-11.0.14_pt-BR.exe'
            self._hash = '3f2f67525d964ee86b42d78eec23baa05afc628d0610ad68027cf6a0f9a52a3d'
   
    def build_save_dir(self, save_dir):
        self._save_dir = save_dir
        return self

    def build_hash(self, hash):
        self._hash = hash
        return self

    def build(self) -> PackageApp:
        
        if KERNEL_TYPE == 'Linux':
            tb: PackageTarGz = TorBrowserLinux(self._pkgname, self._pkgfile, self._save_dir, self._temp_dir)
        elif KERNEL_TYPE == 'Windows':
            tb: PackageWinExe = PackageWinExe(self._pkgname, self._pkgfile, self._save_dir)
        else:
            print(f'{__class__.__name__} ERRO sistema não suportado')
            sys.exit(1)
        
        tb.hash = self._hash
        tb.url = self._url
        return tb




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
     
    tor: PackageApp = BuilderTorBrowser().build()

    if args.install_tor:
        mkdir(tor.save_dir)
        print(f'OUT -> {tor.save_dir}')
        print(f'URL -> {tor.url}')
        print(f'FILE -> {tor.pkg_path().absolute()}')
    
        if not tor.pkg_path().exists():
            wget.download(tor.url, tor.pkg_path().absolute())

        tor.install()
    elif args.uninstall_tor:
        tor.uninstall()

   

if __name__ == '__main__':
    main()
