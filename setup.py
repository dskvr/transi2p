from setuptools import setup, find_packages

setup(
    name='transi2p',
    version='1.2.3',
    description="Transparent proxy for i2p.",
    url="https://github.com/rbif/transi2p/",
    author="Arnold French",
    author_email="arnold.french1974@yandex.com",
    packages=find_packages(),
    install_requires=['zope.interface', 'txi2p-tahoe', 'twisted'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'transi2p=transi2p.main:main',  # Adjust with the correct module and function
        ],
    },
    python_requires='>=3.5',
)
