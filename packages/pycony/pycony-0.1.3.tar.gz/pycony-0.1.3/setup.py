from setuptools import setup


# Read the content of your README file
def read_readme():
    try:
        with open("README.md", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


setup(
    name="pycony",  # Use the new package name
    version="0.1.3",
    packages=["pycony"],  # Specify the package directory
    install_requires=[],
    author="Dr. Rashed Z. Bhatti",
    author_email="rzbhatti@gmail.com",
    description="A cute Python utility to open an interactive console with stack inspection.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rzbhatti/pyCony.git",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
