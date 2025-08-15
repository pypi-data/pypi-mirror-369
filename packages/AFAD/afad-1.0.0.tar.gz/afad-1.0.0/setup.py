from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    description = file.read()

setup(
    name="AFAD",
    version="v1.0.0",
    author="Henil Rakeshbhai Mistry",
    author_email="henil@arista.com",
    description="Nothing but a human leveraging the power of threads to save time. See the below diagram and try to "
                "get it.",
    packages=find_packages(exclude=["AutoFetcher.Tests", "AutoFetcher.Tests.*", "Learning", "Resources", "ShowTechScripts", "ShowTechScripts.*", "Tests", "Tests.*"]),
    install_requires=[
        "pika>=1.3.2",
        "fabric>=3.2.2",
        "packaging>=25.0",
        "pyeapi>=1.0.4"
    ],
    long_description=description,
    long_description_content_type="text/markdown"
)
