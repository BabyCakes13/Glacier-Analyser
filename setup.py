import setuptools

setuptools.setup(
    name='glacier-analyzer',
    version='0.1',
    scripts=['main.py'],
    author="Maria Minerva Vonica",
    author_email="maria.minerva.vonica@gmail.com",
    description="Image alignment and glacier change prediction on satellite images using artificial intelligence.",
    url="https://github.com/BabyCakes13/Glacier-Analyser",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'glacier-analyzer = Licenta.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
)
