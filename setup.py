from setuptools import setup, find_packages
setup(name='pixiedust_peacetech',
	  version='0.1',
	  description='Real-time local visibility to mitigate business disruption in emerging economies',
	  url='https://github.com/ibm-cds-labs/pixiedust_peacetech',
	  install_requires=['pixiedust'],
	  author='David Taieb',
	  author_email='david_taieb@us.ibm.com',
	  license='Apache 2.0',
	  packages=find_packages(),
	  include_package_data=False,
	  zip_safe=False
)
