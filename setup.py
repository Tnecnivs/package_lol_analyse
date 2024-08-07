from setuptools import setup, find_packages

setup(
    name='lol_analysis',  # Nom du package
    version='0.1.0',  # Version du package
    packages=find_packages(),  # Trouve automatiquement les packages
    install_requires=[  # Liste des dépendances (packages requis)
        'numpy>=1.18.0', 
        'requests==2.31.0',
        'pandas==2.1.4',
        "matplotlib==3.9.0",
        'mwrogue==0.1.5'
    ],
    author='Fleure',
    author_email='vincent.sogno12@gmail.com',
    description='Package to analyse opponent team in low level',
    long_description=open('README.md').read(),  # Longue description
    long_description_content_type='text/markdown',  # Format de la longue description
    url='https://github.com/Tnecnivs/package_lol_analyse',  # URL du dépôt
    classifiers=[  # Classification du package
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change la licence si nécessaire
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Version minimale de Python,
    package_data={
        'mon_package': ['assets/*.png'],  # Inclure les fichiers PNG dans le package
    },
    include_package_data=True
)
