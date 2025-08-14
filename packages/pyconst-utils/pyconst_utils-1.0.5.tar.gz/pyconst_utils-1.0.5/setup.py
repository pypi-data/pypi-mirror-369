from setuptools import setup, find_packages

VERSION = '1.0.5'
DESCRIPTION = 'Const type for python'
LONG_DESCRIPTION = 'A package that enables constant variables in python'

setup(
    name="pyconst-utils",
    version=VERSION,
    author="kronus-lx (Joel Manning)",
    author_email="joelem2@hotmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',  # Specify the content type
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'constants', 'const'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)