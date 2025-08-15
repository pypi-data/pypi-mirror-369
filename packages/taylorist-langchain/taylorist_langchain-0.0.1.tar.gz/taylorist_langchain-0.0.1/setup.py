from setuptools import setup, find_packages

setup(
      name="taylorist-langchain",
      version="0.0.1",
      packages=find_packages(),
      include_package_data=True,
      author="umutkrts",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/umutkrts07/taylorist-langchain",
      project_urls={
          "Bug Tracker": "https://github.com/umutkrts07/taylorist-langchain/issues",
          "Source Code": "https://github.com/umutkrts07/taylorist-langchain",
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
    install_requires=[
        "taylorist>=0.1.0",
        "langchain-core>=0.3.70"
    ],
    python_requires=">=3.8",
)