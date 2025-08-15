from setuptools import setup, find_packages
from pathlib import Path

# 📜 Legge la descrizione lunga dal README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

__version__ = (this_directory / "version.txt").read_text()

requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name='nezuki',  # Nome in minuscolo
    version=__version__,
    author='Sergio Catacci',
    author_email='sergio.catacci@icloud.com',
    description='Un pacchetto per la gestione della domotica e servizi server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/KingKaitoKid/Nezuki',
    packages=find_packages(include=["nezuki", "nezuki.*"]),  # Cerca automaticamente i pacchetti in "nezuki/"
    package_dir={"": "."},  # Indica che i moduli sono in "nezuki/"
    include_package_data=True,  # Includi eventuali file extra (da MANIFEST.in)
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    keywords='nezuki domotica home-server',
    project_urls={
        'Bug Reports': 'https://github.com/KingKaitoKid/Nezuki/issues',
        'Source': 'https://github.com/KingKaitoKid/Nezuki',
    },
    entry_points={
        'console_scripts': [
            'email = nezuki.Mail:main',  # Comando CLI "email"
        ],
    },
)