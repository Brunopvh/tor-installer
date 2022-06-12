#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import sys

from conflib.common import (
    File,
    BuilderUserDirs,
    BuilderAppDirs,
    AppDirs,
    UserDirs,
    get_user_home,
    mkdir,
)


app_dirs: AppDirs = BuilderAppDirs().build_appname('appcli').build()
user_dirs: UserDirs = BuilderUserDirs().build_user_root(False).build()


class PackageApp(object):
    def __init__(self, pkgname: str, pkgfile: str, save_dir: str) -> None:
        self.pkgname = pkgname
        self.pkgfile = pkgfile
    
        self.version: str = None
        self.save_dir: str = save_dir # Diretório onde o pacote pode ser 
        self.url = None

        self.hash = None

    @property
    def hash(self):
        return self._hash

    @hash.setter
    def hash(self, new_hash):
        self._hash = new_hash

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url):
        self._url = new_url    
    
    def pkg_path(self) -> File:
        #return Path(os.path.join(self.save_dir, self.pkgfile))
        return File(os.path.join(self.save_dir, self.pkgfile))

    def install(self):
        pass

    def uninstall(self):
        pass



class PackageTarGz(PackageApp):
    def __init__(self, pkgname: str, pkgfile: str, save_dir: str, temp_dir:str) -> None:
        super().__init__(pkgname, pkgfile, save_dir)
        self.temp_dir = temp_dir # Diretório para descomprimir o pacote .tar

    def unpack(self):
        print(f'Descompactando ... {self.pkgfile} em ... {self.temp_dir}', end=' ')
        mkdir(self.temp_dir)
        sys.stdout.flush()
        shutil.unpack_archive(self.pkg_path().absolute(), extract_dir=self.temp_dir, format='tar')
        print('OK')


class PackageWinExe(PackageApp):
    def __init__(self, pkgname: str, pkgfile: str, save_dir: str) -> None:
        super().__init__(pkgname, pkgfile, save_dir)

    def install(self):
        os.system(self.pkg_path().absolute())



def main():
    pass


if __name__ == '__main__':
    main()