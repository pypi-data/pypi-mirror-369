from setuptools import setup, find_packages

setup(
    name="django-smart-validate",
    version="0.1.0",
    author="ProgrammerHasan",
    description="Smart reusable validators for Django models & forms.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["Django>=3.2"],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
