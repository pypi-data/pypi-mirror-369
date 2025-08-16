from setuptools import setup, find_packages

setup(
    name="enhanced_print",
    version="0.1.0",
    packages=find_packages(),
    description="An enhanced print function for Python with advanced features.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Manus AI",
    author_email="manus_ai@example.com",
    url="https://github.com/manus-ai/enhanced_print_lib", # Placeholder URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyYAML",
    ],
)


