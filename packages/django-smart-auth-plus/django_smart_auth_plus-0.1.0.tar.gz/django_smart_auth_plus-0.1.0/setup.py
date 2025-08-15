from setuptools import setup, find_packages

setup(
    name="django-smart-auth-plus",
    version="0.1.0",
    author="ProgrammerHasan",
    description="Advanced Django Authentication package with MFA, JWT, Social Login, Role-based Permissions",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["Django>=3.2", "PyJWT", "requests"],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
