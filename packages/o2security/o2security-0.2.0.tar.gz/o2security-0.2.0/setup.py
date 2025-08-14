from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="o2security",
    version="0.2.0",  # Version bump
    author="sina",
    author_email="sina@unknownmsv.ir",
    description="A simple library for securely managing tokens and secrets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unknownmsv/o2security",
    
    # Find all packages (including o2security and webapp)
    packages=find_packages(),
    
    # Include non-Python files (like HTML templates)
    include_package_data=True,
    
    # Define command line interface
    entry_points={
        'console_scripts': [
            'oxygen = webapp.cli:main',
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    
    # Add Flask to main requirements
    install_requires=[
        'cryptography',
        'python-dotenv',
        'Flask',
    ],
)