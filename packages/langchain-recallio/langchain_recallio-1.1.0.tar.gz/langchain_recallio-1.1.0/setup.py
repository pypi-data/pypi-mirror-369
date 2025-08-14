from setuptools import setup, find_packages

setup(
    name="langchain-recallio",
    version="1.1.0",
    description="Drop-in RecallIO Memory for LangChain",
    author="RecallIO",
    author_email="support@recallio.ai",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "recallio>=1.2.4"
    ],
    python_requires=">=3.8"
)