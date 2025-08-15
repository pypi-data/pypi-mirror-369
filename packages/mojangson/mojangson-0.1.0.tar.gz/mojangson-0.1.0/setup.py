from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='mojangson',
    version='0.1.0',
    author='lunaticyouthie',
    author_email='lunatic.youthie@gmail.com',
    description='Python MojangSON (NBT) parser',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/LunaticYouth/mojangson',
    packages=find_packages(),
    install_requires=['lark>=1.2.2'],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='json mojang nbt parser',
    project_urls={
        'GitHub': 'https://github.com/LunaticYouth/mojangson'
    },
    python_requires='>=3.10'
)
