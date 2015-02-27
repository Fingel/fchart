from setuptools import setup

setup(
    name='fchart',
    version='0.3',
    description='Collection of Python scripts to make beautiful deepsky finder charts in various formats',
    keywords='fchart starchart star charts finder chart astronomy map',
    url='https://github.com/Fingel/fchart',
    author='Michiel Brentjens <brentjens@astron.nl>, Austin Riba <root@austinriba.com>',
    author_email='root@austinriba.com',
    license='GPLv2',
    packages=['fchart'],
    include_package_data=True,
    install_requires=['numpy'],
    scripts=['bin/fchart', 'bin/tyc2_to_binary'],
    package_data={'fchart': ['data/catalogs/index.dat',
                'data/catalogs/revngc.txt',
                'data/catalogs/revic.txt',
                'data/catalogs/sac.txt',
                'data/catalogs/tyc2.bin',
                'data/font-metrics/*.afm',
                'data/label_positions.txt']},
)
