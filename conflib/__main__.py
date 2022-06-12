#!/usr/bin/env python3
#

import sys
import os.path
from pathlib import Path

dir_of_project = os.path.dirname(Path(__file__).absolute())
dir_mod = os.path.dirname(dir_of_project)
sys.path.insert(0, dir_mod)


def main():

    from conflib.common import BuilderUserDirs
    from conflib.common import BuilderAppDirs

    user_dirs = BuilderUserDirs().build_user_root(True).build()
    app_dirs = BuilderAppDirs().build_appname('TesteApp').build()
   
    print(app_dirs.app_cache_dir())
    print(app_dirs.app_json_conf())

    print(user_dirs.binary_dir())



   
if __name__ == '__main__':
    main()
