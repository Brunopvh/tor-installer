#!/usr/bin/env python3
#


import json
from pathlib import Path
from platform import system
from shutil import copyfile
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory



KERNEL_TYPE = system()



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



def _get_file_header(file: str) -> str:
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



class String(str):
    def __init__(self, text) -> None:
        super().__init__()
        self.__text: str = text

    def __repr__(self) -> str:
        return super().__repr__(self.__text)

    def __str__(self) -> str:
        return str(self.__text)

    def concat(self, new_text):
        self.__text += new_text
        
    def to_string(self) -> str:
        return str(self.__text)

    def len(self) -> int:
        return len(self.__text)


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
        """Retorna uma instância de Path() para o arquivo atual"""
        return self.path

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

        name() -> file_name
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

    def drive(self):
        return self.path.drive

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

    def touch(self) -> None:
        self.path.touch()

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
    def __init__(self, user_root: bool) -> None:
        super().__init__()

        self.user_root = user_root
        if os.geteuid() == 0:
            self.user_root = True

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
# Padrão de projeto Builder para criar instâncias de UserDirs em sistemas Linux e Windows
# user_dirs = BuilderUserDirs().get_user_root(True/False).build()
#================================================================================#
class BuilderUserDirs(object):
    def __init__(self) -> None:
        """
           https://github.com/kelvins/design-patterns-python

        """
        self._user_root = False

    def build_user_root(self, user_root: bool = False):
        if os.name == 'nt':
            self._user_root = False
        elif os.name == 'posix' and os.geteuid() == 0:
            self._user_root = True
        else:
            self._user_root = user_root
        return self
        
    def build(self) -> UserDirs:
        
        if KERNEL_TYPE == 'Linux':
            return UserDirsLinux(self._user_root)
        elif KERNEL_TYPE == 'Windows':
            return UserDirsWindows()
        else:
            return UserDirs()


#================================================================================#
# AppDirs
#================================================================================#

class AppDirs(object):
    def __init__(self, appname: str, author: str) -> None:
        self.appname: str = appname
        self.author: str = author
        self.user_dirs: UserDirs = BuilderUserDirs().build_user_root(False).build()

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

    def app_json_conf(self) -> str:
        _file = os.path.join(self.app_config_dir(), f'{self.appname}.json')
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
    def __init__(self, appname: str, author: str, user_root:bool) -> None:
        super().__init__(appname, author)
        self.user_root = user_root
        self.user_dirs: UserDirsLinux = BuilderUserDirs().build_user_root(self.user_root).build()
        
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

    def app_json_conf(self) -> FileJson:
        _file = os.path.join(self.app_config_dir(), f'{self.appname}.json')
        return FileJson(_file)

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
    def __init__(self, appname: str, author: str) -> None:
        super().__init__(appname, author)

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

    def build_user_root(self, user_root: bool = False):
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
            return AppDirsLinux(self._appname, self._author, self._user_root)
        elif KERNEL_TYPE == 'Windows':           
            return AppDirsWindows(self._appname, self._author)
        else:
            return AppDirs(self._appname, self._author)




def main():
    # app: AppDirsAbstract = BuilderAppDirs().build_user_root().build_appname('TesteApp').build_author('BrunoChaves').build()
    pass
    


if __name__ == '__main__':
    main()
