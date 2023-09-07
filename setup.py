from setuptools import setup, find_packages

setup(

    name="crmsum_",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'natasha==1.6.0'

    ],
    author="Федор",
    author_email="",
    description="Библиотека для работы с CRM",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],

)