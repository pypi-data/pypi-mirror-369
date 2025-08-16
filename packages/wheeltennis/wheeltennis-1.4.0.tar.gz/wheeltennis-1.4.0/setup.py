import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
	name             		= 'wheeltennis',
	version          		= '1.4.0',
	description      		= 'Basic scripts for wheelchair tennis analysis',
	author           		= 'Thomas Rietveld',
	author_email     		= 't.rietveld@lboro.ac.uk',
	url              		= 'https://gitlab.com/Thomas2016/wheeltennis',
	download_url     		= 'https://gitlab.com/Thomas2016/wheeltennis',
	packages         		= ['wheeltennis'],
	package_data     		= {},
	include_package_data 	= True,
	long_description 		= read("README.md"),
	license 				= 'GNU GPLv3',
	keywords         		= ['wheelchair tennis', 'sensor', 'IMUs'],
	classifiers      		= ["Programming Language :: Python",
							   "Intended Audience :: Science/Research",
							   "Operating System :: OS Independent"],
	install_requires 		= ["numpy", "seaborn", "scipy>=1.2.0", "pandas", "matplotlib", "worklab"]
)
