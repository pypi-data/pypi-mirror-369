from setuptools import setup, find_packages

setup(
    name="pyarccli",
    version="0.0.000003",
    author="INICODE",
    author_email="contact.inicode@gmail.com",
    description="Paquetage Python pour generer des blocs de code pour faciliter la creation d'application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/inicode_celestin03/pyarccli",
    packages=find_packages(),
    install_requires=[
        'pyarccmder',
        'pyarcgenerator',
    ],
    entry_points={
        'console_scripts': [
            'pyarccli=pyarccli.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)