from setuptools import setup, find_packages

setup(
    name='GenieAPI',
    version='0.1.1',
    description='Genie Music API',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Pma10',
    author_email='pmavmak10@gmail.com',
    url='https://github.com/Pma10/GenieAPI',
    install_requires=[
        "requests"
    ],
    packages=find_packages(exclude=[]),
    keywords=['genie', 'korea', 'lyrics', 'api', 'music'],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    package_data={},
    zip_safe=False,
    license='MIT',
)
