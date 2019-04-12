from setuptools import setup
from distutils.core import Command
import sys

class PyTest(Command):
    description='Run pytests'
    user_options=[]
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import pytest
        sys.argv.pop(0) # remove 'setup.py' so pytest.main works
        result = pytest.main()
        sys.exit(result)

class Schemify(Command):
    description='Run the schemify tool'
    user_options=[
        ('help','h','get help'),
        ('host','H','database host')
    ]
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        from schemify.main import main
        sys.argv.pop(0) # remove 'setup.py' so schemify.main works
        result = main()
        sys.exit(result)

setup(name='schemify',
      version='0.0.1',
      description='A tool that applies a schema definition to a database.',
      url='https://https://github.com/meetearnest/schemify',
      author='Early @ Earnest',
      author_email='platform@earnest.com',
      license='MIT',
      packages=['schemify'],
      setup_requires=['pytest==4.3.1'],
      install_requires=['requests','psycopg2-binary','pyyaml'],
      classifiers=[
         'Programming Language :: Python :: 3.7.2',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'schemify=schemify.main:main'
          ]
      },
      cmdclass = {
          'pytest': PyTest,
          'schemify': Schemify
      })
