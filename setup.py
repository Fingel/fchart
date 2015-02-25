from distutils.core import setup
from distutils.dist import Distribution

import os
import glob

import sys

def remove_slashes(str):
    if str[-1] == '\\':
        s = str[0:-1]
    else:
        s = str
        pass
    return s


attrs = {'name':'fchart',
         'version':"0.2",
         'description':"Collection of Python scripts to make beautiful deepsky\nfinder charts in EPS and PDF format",
         'author':"Michiel Brentjens",
         'packages':['fchart'],
         'package_dir':{'fchart':'lib'},
         'scripts':['scripts/fchart',
                  'scripts/tyc2_to_binary'],
         'data_files':[('fchart/catalogs', ['data/catalogs/index.dat',
                                            'data/catalogs/revngc.txt',
                                            'data/catalogs/revic.txt',
                                            'data/catalogs/sac.txt']),
                     ('fchart/font-metrics',
                      glob.glob('data/font-metrics/*.afm')),
                     ('fchart/labels',['data/label_positions.txt'])],
         'url':'http://www.astro.rug.nl/~brentjen/fchart.html'}

# first obtain the installation directory of the data files
if not '--help' in sys.argv:
    d = Distribution(attrs)
    d.parse_config_files()
    d.parse_command_line()
    cmd_obj = d.get_command_obj('install')
    cmd_obj.finalize_options()
    
    #todo: remove trailing '\'
    DATA_DIR =remove_slashes(os.path.join(cmd_obj.install_data,'fchart'))
    LIB_DIR =remove_slashes(cmd_obj.install_lib)
    SCRIPT_DIR =remove_slashes(cmd_obj.install_scripts)
    
    config_out = file(os.path.join('lib','config.py'), 'w')
    config_out.write('FCHART_DATA_DIR = \''+DATA_DIR+'\'\n')
    config_out.write('FCHART_LIB_DIR = \''+LIB_DIR+'\'\n')
    config_out.write('FCHART_SCRIPT_DIR = \''+SCRIPT_DIR+'\'\n')
    config_out.write('FCHART_VERSION = \''+attrs['version']+'\'\n')
    config_out.close()
    pass

    
s = setup(**attrs)

