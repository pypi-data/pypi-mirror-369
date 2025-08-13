from setuptools import setup, find_packages

setup(
    name="SutraMarathi",
    version="1.0.0",
    author="Kishor Bhagwat",
    author_email="bhagwatkishor09@gmail.com",
    description="Marathi-based programming language interpreter",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://sutramarathi.in",  # GitHub link असेल तर तो दे
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "sutramarathi=sutramarathi.__main__:main"
        ]
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Natural Language :: Marathi",
    ],
)
