from setuptools import setup, find_packages
setup(
    name="BuildAi",
    version="1.0.2",
    description="Improved BuildAi: lightweight educational deep-learning toolkit (numpy-backed).",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["numpy"],
)
