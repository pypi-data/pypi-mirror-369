from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="unbreakablecode",
    version="2.0.0",
    author="UnbreakableCode Developer",
    author_email="support@fixitapi.dev",
    description="Your code can never crash again - Powered by 3.3M Stack Overflow solutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://fixitapi.dev",
    project_urls={
        "Bug Tracker": "https://github.com/unbreakablecode/unbreakablecode/issues",
        "API Dashboard": "https://fixitapi.dev",
        "Documentation": "https://fixitapi.dev",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="error-handling crash-prevention self-healing stackexchange debugging",
)
