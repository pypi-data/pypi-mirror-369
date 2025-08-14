from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='QuickATETools',
    version='1.0.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='A collection of useful command-line tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/QuickATETools',
    packages=find_packages(),
    install_requires=[
        'pyperclip',
    ],
    entry_points={
        'console_scripts': [
            'qate=quickatetools.commands:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)