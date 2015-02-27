# fchart
Michiel Brentjens' fchart - astronomical finder charts now working with numpy and python2.7

![star chart](http://s3-us-west-2.amazonaws.com/pedaldp/images/2015-02-creating-finder-charts-for-astronomy-using-fchart/m31.jpg)

fchart is a set of python scripts and a command line utility to create star maps/finder charts.

Install:

`pip install fchart`

or download and

`python setup.py install`

[Read the original README](README)

The original source of this code can be found here:
https://www.astro.rug.nl/~brentjen/fchart.html

However it relies on numarray which has been deprecated in favor of numpy. This repository contains updated sourcecode so that the code may run with numpy.


This repo also contains tyc2.bin in the data/catalogs directory. The original tyc2.bin hosted on Michiel's website seemed to have errors, so this is a rebuilt version using data downloaded here: http://cdsarc.u-strasbg.fr/viz-bin/Cat?I/259
