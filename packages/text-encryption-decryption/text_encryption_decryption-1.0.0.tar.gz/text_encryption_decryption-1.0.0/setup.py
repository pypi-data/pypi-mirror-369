from setuptools import setup, find_packages

setup(
    name='text-encryption-decryption',
    version='1.0.0',
    author='Sowmiya Narayanan A',
    author_email='sowmisn2006@gmail.com',
    description='Library which is used to Encrypt and Decrypt texts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)