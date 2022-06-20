#!/usr/bin/env python3
#


import os
import shutil
import sys
import hashlib
import json
import urllib.request
from shutil import (unpack_archive, copyfile, rmtree)
from pathlib import Path
from platform import system
from tempfile import NamedTemporaryFile, TemporaryDirectory


try:
	#from bs4 import BeautifulSoup
	import requests
	from requests import Response
	import tqdm
except Exception as e:
	print(e)
	sys.exit(1)

KERNEL_TYPE = system()


#=====================================================================#
# Funções
#=====================================================================#

def get_user_home() -> str:
    return os.path.abspath(Path().home())

def mkdir(path: str) -> bool:
    """Função para criar um diretório."""
    if path is None:
        return False

    if os.path.exists(path):
        return True
        
    try:
        os.makedirs(path)
    except Exception as e:
        print(__name__, e)
        return False
    else:
        return True

def rmdir(path: str) -> bool:
    if path is None:
        return False

    try:
        shutil.rmtree(path)
    except:
        return False
    else:
        return True



def _get_file_header(file: str) -> str:
    """
      Usa o módulo magic do python para obter o cabeçalho de um arquivo

    """
    try:
        from magic import from_file
    except Exception as e:
        print(e)
        return None
    else:
        return from_file(file)



def get_abspath(path: str) -> str:
    """Retorna o caminho absoluto de um arquivo ou diretório."""
    return os.path.abspath(path)


#=========================================================================#
# Downloader
#=========================================================================#

def get_terminal_width() -> int:
	try:
		width = int(os.get_terminal_size()[0])
	except:
		width = 80
	return width

def clean_line():
	"""Limpar a linha do console"""
	print(' ' * get_terminal_width(), end='\r')


def download_file(url: str, output_file: str, verbose: bool=True) -> bool:
	if os.path.isfile(output_file):
		print(f'[PULANDO] ... {output_file}')
		return True

	if len(output_file) > 20:
		show_filename = f'{output_file}[0:20]...'
	else:
		show_filename = output_file

	req: Response = requests.get(url, stream=True)
	#req = requests.get(url, stream=True)
	
	try:
		file_size = int(req.headers['Content-Length'])
	except:
		file_size = int(0)


	chunk = 1
	chunk_size = 1024
	num_bars = int(file_size / chunk_size)
	clean_line()
	# unit='KB'

	try:
		with open(output_file, 'wb') as fp:
			for chunk in tqdm.tqdm(
				req.iter_content(chunk_size=chunk_size), total=num_bars, unit='KB', desc=show_filename,leave=True # progressbar stays
				):
				fp.write(chunk)

	except Exception as e:
		print(e)
		return False
	else:
		return True


class ByteSize(int):
    """
      Classe para mostrar o tamaho de um arquivo (B, KB, MB, GB) de modo legível para humanos.
    """

    # https://qastack.com.br/programming/1392413/calculating-a-directorys-size-using-python
    # 2021-11-13 - 21:12
    
    _kB = 1024
    _suffixes = 'B', 'kB', 'MB', 'GB', 'PB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.kB = self / self._kB**1
        self.megabytes = self.MB = self / self._kB**2
        self.gigabytes = self.GB = self / self._kB**3
        self.petabytes = self.PB = self / self._kB**4
        *suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 < getattr(self, suffix) < self._kB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))

    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other))


class File(object):
    """
       Classe para trabalhar com um arquivo, e obter algumas informações como:
    path()      - Caminho absoluto.
    exists()    - Verificar se o arquivo existe.
    name()      - Retorna o nome do arquivo, sem a extensão.
    dirname()   - Retorna o diretório PAI do arquivo.
    basename()  - Retorna o nome do arquivo com a extensão.
    extension() - Retorna a extensão do arquivo, com base no nome.
    """

    def __init__(self, file: str) -> None:
        super().__init__()
        self.file = file
        self.path: Path = Path(self.file)

    def get_path(self) -> Path:
        """Retorna uma nova instância de Path() para o arquivo atual"""
        return Path(self.absolute())

    def absolute(self) -> str:
        """Retorna o caminho absoluto de um arquivo"""
        return get_abspath(self.path.absolute())

    def exists(self) -> bool:
        return self.path.exists()

    def name(self) -> str:
        """
           Retorna o nome do arquivo sem a extensão, e sem o caminho absoluto.
        Ex:
           /path/to/file_name.pdf

        self.name() -> file_name
        """
        if self.extension() is None:
            return self.basename()
        return self.basename().replace(self.extension(), "")

    def dirname(self) -> str:
        """
           Retorna o caminho absoluto do diretório pai do arquivo.
        """
        return os.path.dirname(self.absolute())

    def basename(self) -> str:
        """
           Retorna o nome do arquivo com a extensão, sem o caminho absoluto.
        Ex:
           /path/to/file_name.pdf

        basename() -> file_name.pdf
        """
        return os.path.basename(self.absolute())

    def extension(self) -> str:
        """Retorna a extensão do arquivo baseado no nome"""
        _ext = os.path.splitext(self.absolute())[1]
        if _ext == '':
            return None
        return _ext

    def extension_header(self) -> str:
        """Retorna a extensão/tipo de arquivo com base no cabeçalho"""
        if self.header() is None:
            return None
        return self.header().split()[0]

    def header(self) -> str:
        """
           Retorna o cabeçalho de arquivo
        """
        return _get_file_header(self.absolute())

    def delete(self) -> None:
        """Deleta o arquivo"""
        os.remove(self.absolute())


class FileReader(object):
    """
       Classe para ler e escrever linhas em arquivos de texto

    get_lines() - Retorna as linhas de um arquivo em forma de lista.
    write_lines(list) - Recebe uma lista, e grava os dados da lista no arquivo.
    """

    def __init__(self, file: File) -> None:
        self.file: File = file

    def get_lines(self) -> list:
        """Retorna uma lista com as linhas do arquivo de texto."""
        lines = []

        try:
            with open(self.file.absolute(), 'rt') as f:
                lines = f.readlines()
        except Exception as e:
            print(__class__.__name__, e)
            return lines
        else:
            return lines

    def read(self):
        try:
            with open(self.file.absolute(), 'rt') as f:
                return f.read()
        except Exception as e:
            print(f'{__class__.__name__} ... {e}')
        return None

    def write_lines(self, lines: list) -> None:
        """
           Sobreescrever um arquivo, gravando o conteúdo de lines no arquivo.
        Todos os dados existentes serão perdidos. Quebras de linha '\n' são
        inseridas automáticamente no fim de cada linha.
        """
        if not isinstance(lines, list):
            print(__class__.__name__, "ERRO ... lines precisa ser do tipo lista")
            return

        try:
            with open(self.file.absolute(), 'w') as file:
                for line in lines:
                    file.write(f'{line}\n')
        except Exception as e:
            print(__class__.__name__, e)

    def append_lines(self, lines: list) -> None:
        """Adiciona o conteúdo de lines no fim do arquivo de texto"""
        if not isinstance(lines, list):
            print(__class__.__name__, "ERRO ... lines precisa ser do tipo lista")
            return

        try:
            with open(self.file.absolute(), 'a') as f:
                for line in lines:
                    f.write(f'{line}\n')
        except Exception as e:
            print(__class__.__name__, e)

    def is_text(self, text: str) -> bool:
        """Verifica se text existe no arquivo de texto"""
        if len(self.find_text(text)) > 0:
            return True
        return False

    def find_text(self, text: str, *, max_count: int = 0, ignore_case: bool = False) -> list:
        """
            Retorna uma lista com todas as ocorrências de text nas linhas do arquivo.
        max_cout = Máximo de ocorrências a buscar no arquivo.
        ignore_case = Ignora o case sensitive.
        """

        _lst = []
        if self.get_lines() == []:
            return []

        for line in self.get_lines():
            if ignore_case:
                if text.lower() in line.lower():
                    _lst.append(line)
            else:
                if text in line:
                    _lst.append(line)

            if (max_count > 0) and (len(_lst) == max_count):
                break

        return _lst


class JSON(object):
    def __init__(self, data_json: str) -> None:
        # data_json -> Dados no formato json (que é uma string para o python)
        # EX:
        #
        # data = r'''{
        #   "Lang1": "Python",
        #   "Lang2": "C",
        #   "Lang3": "bash"
        # }''' 
        #
        # JsonObj = JSON(data)
        #
        #
        # 
        #
        self.data_json: str = data_json

    def __repr__(self) -> str:
        return json.JSONEncoder().encode(self.data_json)

    def __str__(self) -> str:
        return self.__repr__()
       
    def to_dict(self) -> dict:
        """Converte os dados em json para um dicionário"""
        return json.loads(self.data_json)

    def keys(self) -> list:
        """Retorna as keys de um json em forma de lista (list) no python"""
        return list(self.to_dict().keys())

    def values(self) -> list:
        """
           Retorna os valores de um json em formato de lista (list) python.
        """
        return list(self.to_dict().values())

    def iskey(self, key) -> bool:
        for K in self.keys():
            if key == K:
                return True
                break
        return False

    def get_key(self, key):
        """
           Retorna o valor de uma chave do json se existir, se não retorna None.
        """
        if not self.iskey(key):
            return None
        for _k in self.keys():
            if _k == key:
                return self.to_dict()[_k]
                break

    def index(self, key: str) -> int:
        """
            Retorna o número de key no json/dict
        se key não existir no json então retorna -1    
        """
        for num, value in enumerate(self.keys()):
            if value == key:
                return num
                break
        return -1

    def append(self, key: str, value: str) -> None:
        """
            Insere uma chave e valor no Json.
        """
        _d = self.to_dict()
        _d.update({key: value})
        self.data_json = json.JSONEncoder().encode(_d)

    def format(self):
        """Retorna os dados formatados com ensure_ascii=False e indent=4"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)


class FileJson(File):
    """
       Classe com as funcionalidades:
    - Ler um arquivo json e retornar o conteúdo em forma de dicionário.

    - Sobreescrever/Criar um arquivo json apartir de um dicionário.

    - Alterar/Adicionar o conteúdo de uma chave.

    - Alterar/Adicionar uma chave.

    """

    def __init__(self, file: str):
        super().__init__(file)

    def write_lines(self, new_lines: dict):
        """
        Apaga o conteúdo do arquivo .json, e escreve os dados 'new_lines' no arquivo.
        """

        if not isinstance(new_lines, dict):
            raise Exception(f'{__class__.__name__} ERRO ... tipo de dados incorreto ... {new_lines}')

        with open(self.absolute(), 'w', encoding='utf8') as jfile:
            json.dump(new_lines, jfile, ensure_ascii=False, sort_keys=True, indent=4)

    def lines_to_dict(self) -> dict:
        """
        Ler o conteúdo do arquivo .json e retorna as linhas em forma de um dicionário
        """
        try:
            with open(self.absolute(), 'rt', encoding='utf8') as jfile:
                content = json.load(jfile)
        except Exception as e:
            print(__class__.__name__, e)
            return {}
        else:
            return content

    def update_key(self, new_key: str, value: str):
        """
          Altera/Cria a chave 'new_key' com o valor 'value'

        Se new_key já existir, será modificada, se não será alterada.
        """
        content = self.lines_to_dict()

        if not new_key in content.keys():
            content.update({new_key: value})
        else:
            content[new_key] = value

        self.write_lines(content)

    def is_key(self, key: str) -> bool:
        """Verifica se uma chave/key existe no json"""
        _keys = self.lines_to_dict().keys()

        for json_key in self.lines_to_dict().keys():
            if json_key == key:
                return True
                break
        return False

    def get_lines(self):
        """
            Retorna as linhas de um arquivo no formato Json.
        """
        return json.dumps(self.lines_to_dict(), indent=4, ensure_ascii=False)

    def get_json(self) -> JSON:
        """
           Retorna uma instância de JSON() para os dados do arquivo.
        """
        # return JSON(FileReader(self.abspath()).read())

        try:
            with open(self.absolute(), 'rt') as f:
                return JSON(f.read())
        except Exception as e:
            print(f'{__class__.__name__}: {e}')
            return None



class UserDirs(object):
    def __init__(self) -> None:
        self._temp_dir = None
        self._temp_file = None
        self.user_root = False

    def temp_dir(self) -> str:
        if self._temp_dir is None:
            self._temp_dir = TemporaryDirectory().name
        return self._temp_dir

    def temp_file(self) -> str:
        if self._temp_file is None:
            self._temp_file = NamedTemporaryFile(delete=True).name
        return self._temp_file

    def config_dir(self) -> str:
        pass

    def cache_dir(self) -> str:
        pass

    def binary_dir(self) -> str:
        pass

    def opt_dir(self) -> str:
        pass

    def data_dir(self) -> str:
        pass

    def log_dir(self) -> str:
        pass


class UserDirsLinux(UserDirs):
    def __init__(self) -> None:
        super().__init__()
        self.user_root = False
        
    @property
    def user_root(self) -> bool:
        return self._user_root

    @user_root.setter
    def user_root(self, new_user_root: bool):
        self._user_root = new_user_root
        if os.geteuid() == 0:
            self._user_root = True

    def config_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.config'))
        return '/etc'

    def cache_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.cache'))
        return '/var/cache'

    def binary_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'bin'))
        return '/usr/local/bin'

    def lib_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'lib'))
        return '/usr/local/lib'

    def opt_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'opt'))
        return '/opt'

    def data_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'share'))
        return '/usr/share'

    def log_dir(self) -> str:
        return None

    def hicolor_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'share', 'icons', 'hicolor'))
        return '/usr/share/icons/hicolor'

    def icon_dir(self, resol='128x128') -> str:
        return Path(os.path.join(self.hicolor_dir(), resol, 'apps'))

    def themes_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'share', 'themes'))
        return '/usr/share/themes'

    def desktop_entry_dir(self) -> str:
        if not self.user_root:
            return get_abspath(os.path.join(get_user_home(), '.local', 'share', 'applications'))
        return '/usr/share/applications'        



class UserDirsWindows(UserDirs):
    def __init__(self) -> None:
       super().__init__()

    def config_dir(self) -> str:
        return get_abspath(os.path.join(get_user_home(), 'AppData', 'Roaming'))

    def cache_dir(self) -> str:
        return get_abspath(os.path.join(get_user_home(), 'AppData', 'Local'))

    def binary_dir(self) -> str:
        return get_abspath(os.path.join(get_user_home(), 'AppData', 'Local', 'Programs'))

    def opt_dir(self) -> str:
        pass

    def data_dir(self) -> str:
        pass

    def log_dir(self) -> str:
        pass


#================================================================================#
# AppDirs
#================================================================================#

class AppDirs(object):
    def __init__(self, appname: str) -> None:
        self.appname: str = appname
        self.author: str = None
        self.user_root: bool = False
        self.user_dirs: UserDirs = UserDirs()

    @property
    def appname(self) -> str:
        return self._appname

    @appname.setter
    def appname(self, new_appname: str) -> None:
        self._appname = new_appname

    def get_dirs(self):
        return {
            'APP_DIR': self.appdir(),
            'APP_DIR_CACHE': self.app_cache_dir(),
            'APP_DIR_CONFIG': self.app_config_dir(),
        }

    def app_cache_dir(self) -> str:
        pass

    def app_config_dir(self) -> str:
        pass

    def appdir(self) -> str:
        pass

    def app_file_conf(self) -> str:
        pass

    def app_json_conf(self, filejson: str) -> FileJson:
        """
           Retorna uma instância de FileJson para o arquivo filejson.json
        """
        _file = os.path.join(self.app_config_dir(), filejson)
        return FileJson(_file)

    def app_script(self) -> str:
        pass

    def get_temp_dir(self) -> str:
        """
           Retorna um diretório temporário.
        """
        return self.user_dirs.temp_dir()

    def get_temp_file(self) -> None:
        """Retorna um arquivo temporário."""
        return self.user_dirs.temp_file()




class AppDirsLinux(AppDirs):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)
        self.user_dirs: UserDirsLinux = UserDirsLinux()
        self.user_dirs.user_root = self.user_root
        
    @property
    def user_root(self) -> bool:
        return self._user_root

    @user_root.setter
    def user_root(self, new_user_root: bool):
        self._user_root = new_user_root
        
        if os.geteuid() == 0:
            self._user_root = True
        
        self.user_dirs: UserDirsLinux = UserDirsLinux()
        self.user_dirs.user_root = self._user_root

    @property
    def appname(self) -> str:
        return self._appname

    @appname.setter
    def appname(self, new_appname: str) -> None:
        self._appname = new_appname

    def get_dirs(self):
        return {
            'APP_DIR': self.appdir(),
            'APP_DIR_CACHE': self.app_cache_dir(),
            'APP_DIR_CONFIG': self.app_config_dir(),
        }

    def app_cache_dir(self) -> str:
        return os.path.join(self.user_dirs.cache_dir(), self.appname)

    def app_config_dir(self) -> str:
        return os.path.join(self.user_dirs.config_dir(), self.appname)

    def appdir(self) -> str:
        return os.path.join(self.user_dirs.opt_dir(), self.appname)

    def app_file_conf(self) -> str:
        return os.path.join(self.app_config_dir(), f'{self.appname}.conf')

    def app_script(self) -> str:
        return get_abspath(os.path.join(self.user_dirs.binary_dir(), self.appname))

    def app_icon(self, file_icon: str) -> str:
        """
          Recebe o nome de um arquivo (.png, .jpg, ,svg ...)
        Retorna o caminho onde o icone deve estar no sistema.
        """
        return get_abspath(os.path.join(self.user_dirs.icon_dir(), file_icon))

    def app_desktop_entry(self, file_desktop) -> str:
        """
        A extensão .desktop é adicionada automáticamente.

        Retorna o caminho completo do arquivo .desktop.
        """
        if file_desktop[-8:] != '.desktop':
            file_desktop += '.desktop'

        return get_abspath(os.path.join(self.user_dirs.desktop_entry_dir(), file_desktop))

    def create_dirs(self) -> bool:
        """
         Cria os diretórios de configuração.
        """
        pass


class AppDirsWindows(AppDirs):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)
        self.user_dirs: UserDirsWindows = UserDirsWindows()

    @property
    def appname(self) -> str:
        return self._appname

    @appname.setter
    def appname(self, new_appname: str) -> None:
        self._appname = new_appname

    def get_dirs(self):
        return {
            'APP_DIR': self.appdir(),
            'APP_DIR_CACHE': self.app_cache_dir(),
            'APP_DIR_CONFIG': self.app_config_dir(),
        }

    def app_cache_dir(self) -> str:
        return os.path.join(self.user_dirs.cache_dir(), self.appname)

    def app_config_dir(self) -> str:
        return os.path.join(self.user_dirs.config_dir(), self.appname)

    def appdir(self) -> str:
        return os.path.join(self.user_dirs.opt_dir(), self.appname)

    def app_file_conf(self) -> str:
        return os.path.join(self.app_config_dir(), f'{self.appname}.conf')

    def app_script(self) -> str:
        return get_abspath(os.path.join(self.user_dirs.binary_dir(), self.appname))

    def app_icon(self, file_icon: str) -> str:
        """
          Recebe o nome de um arquivo (.png, .jpg, ,svg ...)
        Retorna o caminho onde o icone deve estar no sistema.
        """
        return get_abspath(os.path.join(self.user_dirs.icon_dir(), file_icon))

    def create_dirs(self) -> bool:
        """
         Cria os diretórios de configuração.
        """
        pass



class BuilderUserDirs(object):
    def __init__(self) -> None:
        """
           https://github.com/kelvins/design-patterns-python

        """
        self._user_root = False

    def build_user_root(self, user_root: bool):
        if os.name == 'nt':
            self._user_root = False
        elif os.name == 'posix' and os.geteuid() == 0:
            self._user_root = True
        else:
            self._user_root = user_root
        return self

    def build(self) -> UserDirs:
        if KERNEL_TYPE == 'Linux':
            user_dirs: UserDirsLinux = UserDirsLinux()
        elif KERNEL_TYPE == 'Windows':
            user_dirs: UserDirsWindows = UserDirsWindows()

        user_dirs.user_root = self._user_root
        return user_dirs


class BuilderAppDirs(object):
    def __init__(self) -> None:
        """
           https://github.com/kelvins/design-patterns-python

        """
        self._appname = None
        self._author = None
        self._user_root = False

    def build_author(self, author: str):
        self._author = author
        return self

    def build_appname(self, appname: str):
        self._appname = appname
        return self

    def build_user_root(self, user_root: bool):
        if os.name != 'posix':
            return self
        if os.geteuid() == 0:
            self._user_root = True
        else:
            self._user_root = user_root
        return self

    def build(self) -> AppDirs:
        if self._appname is None:
            raise Exception(f'{__class__.__name__} appname não pode ser None')

        if KERNEL_TYPE == 'Linux':
            app_dirs: AppDirsLinux = AppDirsLinux(self._appname)
        elif KERNEL_TYPE == 'Windows':
            app_dirs: AppDirsWindows = AppDirsWindows(self._appname)
        else:
            app_dirs: AppDirs = AppDirs(self._appname)

        app_dirs.user_root = self._user_root
        app_dirs.author = self._author
        return app_dirs


class PackageApp(object):
    def __init__(self, appname: str, appfile: str, save_dir: str) -> None:
        super().__init__()
        self.app_dirs: AppDirs = BuilderAppDirs().build_appname(appname).build_user_root(False).build()

        self.appfile: str = appfile
        self.version: str = None
        self.save_dir: str = save_dir # Diretório onde o pacote deve ser baixado.
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

    def verify(self) -> bool:
        """
            Verifica a integridade do pacote
        """
        if self.hash is None:
            print(f'ERRO ... {__class__.__name__} sha256 não pode ser None')
            return False
        #print(f'[CHECANDO] ... {self.pkg_file().absolute()}')
        return ShaSum(self.pkg_file().absolute()).check_sha256(self.hash)

    def pkg_file(self) -> File:
        pass

    def install(self):
        pass

    def uninstall(self):
        pass

    def download(self):
        return download_file(self.url, self.pkg_file().absolute())


class PackageTarGz(PackageApp):
    def __init__(self, appname: str, appfile: str, save_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)

        # Nome do diretório após a descompressão do pacote tar.gz
        self.dir_package_files: str = None

    def unpack(self):
        print(f'Descompactando ... {self.appfile} em ... {self.app_dirs.get_temp_dir()}', end=' ')
        mkdir(self.app_dirs.get_temp_dir())
        sys.stdout.flush()
        unpack_archive(self.pkg_file().absolute(), extract_dir=self.app_dirs.get_temp_dir(), format='tar')
        print('OK')

    def pkg_file(self) -> File:
        return File(os.path.join(self.save_dir, self.appfile))


class PackagePython3Zip(PackageApp):
    def __init__(self, appname: str, appfile: str, save_dir: str, project_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)
        self.project_dir = project_dir

    def pkg_file(self) -> File:
        return File(os.path.join(self.save_dir, self.appfile))

    def unpack(self):
        print(f'Descompactando ... {self.appfile} em ... {self.app_dirs.get_temp_dir()}', end=' ')
        mkdir(self.app_dirs.get_temp_dir())
        sys.stdout.flush()
        unpack_archive(self.pkg_file().absolute(), extract_dir=self.app_dirs.get_temp_dir(), format='zip')
        print('OK')

    def install(self):
        self.unpack()
        os.chdir(self.app_dirs.get_temp_dir())
        os.chdir(self.project_dir)
        os.system(f'{sys.executable} setup.py install')
        rmtree(self.app_dirs.get_temp_dir())

    

class PackagePython2Zip(PackageApp):
    def __init__(self, appname: str, appfile: str, save_dir: str, project_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)
        self.project_dir = project_dir
        self.path_python2: str = None

    def pkg_file(self) -> File:
        return File(os.path.join(self.save_dir, self.appfile))

    def unpack(self):
        print(f'Descompactando ... {self.appfile} em ... {self.app_dirs.get_temp_dir()}', end=' ')
        mkdir(self.app_dirs.get_temp_dir())
        sys.stdout.flush()
        unpack_archive(self.pkg_file().absolute(), extract_dir=self.app_dirs.get_temp_dir(), format='zip')
        print('OK')

    def install(self):
        self.unpack()
        os.chdir(self.app_dirs.get_temp_dir())
        os.chdir(self.project_dir)
        os.system(f'{self.path_python2} setup.py install')
        #rmtree(self.app_dir.get_temp_dir())


class PackageWinExe(PackageApp):
    def __init__(self, appname: str, appfile: str, save_dir: str) -> None:
        super().__init__(appname, appfile, save_dir)

    def pkg_file(self) -> File:
        return File(os.path.join(self.save_dir, self.appfile))

    def install(self):
        os.system(self.pkg_file().absolute())



class ShaSum(object):
    def __init__(self, data) -> None:
        super().__init__()
        self.data = data # data = arquivo/string/bytes
        self.__bytes = None

    def _get_bytes(self) -> bytes:
        """
        converte self.data para bytes e retorna bytes.
        """
        if self.__bytes is not None:
            return self.__bytes

        if isinstance(self.data, bytes):
            return self.data

        if isinstance(self.data, str):
            # Verificar se data é um texto ou um arquivo.

            if os.path.isfile(self.data):
                try:
                    with open(self.data, 'rb') as file:
                        self.__bytes = file.read()
                except Exception as e:
                    print(e)
            else:
                self.__bytes = str.encode(self.data)
            return self.__bytes

    def check_md5(self, md5_string: str) -> bool:
        if len(md5_string) != 32:
            print(f'{__class__.__name__} ERRO hash do tipo md5 deve ter 32 caracteres.')
            return False

        if self.getmd5() == md5_string:
            return True

        print(f'{__class__.__name__} FALHA')
        return False

    def check_sha1(self, sha1_string: str) -> bool:
        if len(sha1_string) != 40:
            print(f'{__class__.__name__} ERRO hash do tipo sha1 deve ter 40 caracteres.')
            return False

        if self.getsha1() == sha1_string:
            return True

        print(f'{__class__.__name__} FALHA')
        return False

    def check_sha256(self, sha256_string: str) -> bool:
        if len(sha256_string) != 64:
            print(f'{__class__.__name__} ERRO hash do tipo sha256 deve ter 64 caracteres.')
            return False

        if self.getsha256() == sha256_string:
            return True

        print(f'{__class__.__name__} FALHA')
        return False

    def check_sha512(self, sha512_string: str) -> bool:
        if len(sha512_string) != 128:
            print(f'{__class__.__name__} ERRO hash do tipo sha512 deve ter 128 caracteres.')
            return False

        if self.getsha512() == sha512_string:
            return True

        print(f'{__class__.__name__} FALHA')
        return False


    def getmd5(self) -> str:
        if self._get_bytes() is None:
            return None
        return hashlib.md5(self._get_bytes()).hexdigest()

    def getsha1(self) -> str:
        if self._get_bytes() is None:
            return None
        return hashlib.sha1(self._get_bytes()).hexdigest()

    def getsha256(self) -> str:
        if self._get_bytes() is None:
            return None
        return hashlib.sha256(self._get_bytes()).hexdigest()

    def getsha512(self) -> str:
        if self._get_bytes() is None:
            return None
        return hashlib.sha512(self._get_bytes()).hexdigest()


def main():
    pass
    
if __name__ == '__main__':
    main()
