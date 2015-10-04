from setuptools import setup


setup(
    name='regina',
    version='1.0',
    url='http://github.com/cburmeister/regina/',
    license='MIT',
    author='Corey Burmeister',
    author_email='burmeister.corey@gmail.com',
    oescription='Fetch new releases from http://www.juno.co.uk/.',
    py_modules=['regina'],
    platforms='any',
    install_requires=[
        'beautifulsoup4==4.3.2',
        'click==3.3',
        'requests==2.5.1',
    ],
    entry_points='''
        [console_scripts]
        regina=regina:main
    '''
)
