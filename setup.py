from setuptools import setup

setup(
    name='friendisqt',
    version='0.0.1',
    author='Alistair Buxton',
    author_email='a.j.buxton@gmail.com',
    url='http://github.com/ali1234/friendisqt',
    packages=['friendisqt'],
    package_data={
        'friendisqt': [
            'sprites/*/*',
        ],
    },
    entry_points={
        'gui_scripts': [
            'friendisqt = friendisqt.__main__:main',
        ],
    },
    install_requires=[
        'PyQt5', 'click'
    ],
)
