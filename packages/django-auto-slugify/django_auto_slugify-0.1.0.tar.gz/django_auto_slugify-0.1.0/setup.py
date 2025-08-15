from setuptools import setup, find_packages

setup(
    name="django-auto-slugify",
    version="0.1.0",
    author="ProgrammerHasan",
    author_email="programmerhasan@email.com",
    description="Auto-generate unique slugs for Django models",
    long_description_content_type="text/markdown",
    url="https://github.com/programmerhasan/django-auto-slugify",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2"
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
