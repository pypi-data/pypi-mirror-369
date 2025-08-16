from setuptools import setup, find_packages

setup(
    name="localfiletransfer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gunicorn",
    ],
    entry_points={
        'console_scripts': [
            'localfiletransfer=localfiletransfer.server:cli_entry',
        ],
    },
    author="Bivab Das",
    author_email="bivabdas@gmail.com",
    description="A simple local network file transfer tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bivab0/localfiletransfer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
