from setuptools import setup, find_packages

setup(
    name="django-referral2",  # unique name on PyPI
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.2',  # or your Django version
    ],
    description="A reusable Django referral system app",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Andrew Oduola",
    author_email="andrewoduola@gmail.com",
    url="https://github.com/Andrew-oduola/django-referral",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
