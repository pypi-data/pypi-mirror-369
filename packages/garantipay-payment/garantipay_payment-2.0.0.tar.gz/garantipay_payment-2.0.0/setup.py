import setuptools


def readme():
    with open("README.md", "r") as f:
        return f.read()


setuptools.setup(
    name="garantipay-payment",
    version="2.0.0",
    author="Akinon",
    author_email="dev@akinon.com",
    description="A library to provide payment gateway for GarantiPay 2.0",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/akinonteam/garantipay-payment",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "dummy.*"]),
    zip_safe=False,
    install_requires=[
        "Django>=2.2.9,<4.3",
        "requests",
        "djangorestframework>=3.14.0,<4.0",
        "mock==4.0.3",
    ],
    include_package_data=True,
    package_data={"garantipay_payment": ["templates/*"]},
)
