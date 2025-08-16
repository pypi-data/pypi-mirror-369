from setuptools import setup

setup(
    name="FindBadwords",
    version="1.2.2",
    description="Find any word in a sentence",
    long_description="Find any word in a sentence, especially if contain special character ;)",
    author="BOXER",
    author_email="vagabonwalybi@gmail.com",
    maintainer="BOXER",
    maintainer_email="vagabonwalybi@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    install_requires=[
        "immutable-Python-Type",
        "regex"
    ],

    packages=['FindBadwords'],
    python_requires=">=3.9",
    include_package_data=True,
)