from setuptools import setup
import lanchat

version = '.'.join(map(str, lanchat.__version__))
long_desc = '''
Distributed LAN chat
'''

setup(name='lanchat',
      version=version,
      description='Distributed LAN chat',
      long_description=long_desc,
      url='https://github.com/theSage21/lanchat',
      author='Arjoonn Sharma',
      author_email='Arjoonn Sharma',
      license='MIT',
      packages=['lanchat'],
      zip_safe=False,
      include_package_data=True,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.4',
                   ],
      keywords='LAN chat serverless'.split(' '),
      entry_points={'console_scripts': ['lanchat=lanchat.cli:main']},
      )
