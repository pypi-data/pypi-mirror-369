from setuptools import setup, find_packages

setup(
      name="taylorist",
      version="0.1.0",
      packages=find_packages(),
      include_package_data=True,
      package_data={
          "taylorist": ["**/*.py", "**/py.typed"],
      },
      author="umutkrts",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/umutkrts07/taylorist",
      project_urls={
          "Bug Tracker": "https://github.com/umutkrts07/taylorist/issues",
          "Source Code": "https://github.com/umutkrts07/taylorist",
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
    install_requires=[
        "httpx>=0.28.1",
        "requests>=2.32.3",
        "pydantic>=2.11.5",
        "aiohttp>=3.12.7"
    ],
    python_requires=">=3.8",
)