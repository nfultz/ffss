from setuptools import setup

setup(name='ffss',
      version='0.1',
      description='Flat File Pager',
      url='http://github.com/nfultz/ffss',
      download_url="https://github.com/nfultz/ffss/tarball/0.1",
      author='Neal Fultz',
      author_email='nfultz@gmail.com',
      license='BSD',
      packages=['ffss'],
      zip_safe=False,
      include_package_data=True,
      scripts=['bin/ffss']
)
