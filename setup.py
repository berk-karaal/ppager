import setuptools

VERSION = "0.1.1"
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ppager",
    version=VERSION,
    author="Berk Karaal",
    author_email="iletisim.berkkaraal@gmail.com",
    description="PAGER with Python that can be implemented to your projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="pager less more most terminal",
    url="https://github.com/berk-karaal/ppager",
    license="MIT",
    project_urls={
        "Documentation": "https://berkkaraal.com/ppager-docs/",
        "Source": "https://github.com/berk-karaal/ppager/",
        "Bug Tracker": "https://github.com/berk-karaal/ppager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["ppager"],
    entry_points={"console_scripts": ["ppager=ppager.run_ppager:run"]},
    python_requires=">=3.8",
)
