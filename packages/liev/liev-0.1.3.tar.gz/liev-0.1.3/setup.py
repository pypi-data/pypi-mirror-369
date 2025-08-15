from setuptools import setup, find_packages

setup(
    name="liev",
    version="0.1.3",
    author="Liev.ai",
    author_email="gabriel.penna@inmetrics.com.br",
    description="Liev LLM Dispatcher client",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://liev.ai",  # Mudar para GIT
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    install_requires=[
        "requests>=2.32.4",
        "openai>=1.92.0"
    ],
)