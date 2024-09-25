from setuptools import setup, find_packages

setup(
    name='my_project',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_project',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    install_requires=[
        'python_telegram_bot',
        'aiohttp',
        'cython',
        'paramiko',
        'openai',
        'torrentSearch',
        'dataclass-wizard',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'server=ssh_over_telegram.Server:main',
            'terminal=ssh_over_telegram.Terminal:main',
        ],
    },
)
