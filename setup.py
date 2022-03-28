from setuptools import find_packages, setup

__author__ = [
    "Ingrid Sanchez",
    "Jim Hommes"
]
__copyright__ = "Copyright 2022"
__credits__ = ["Laurens de Vries", "Milos Cvetkovic"]

__license__ = "MIT License"
__maintainer__ =   "Ingrid Sanchez"
__email__= "i.j.sanchezjimenez@tudelft.nl"
__status__ = "under development"


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="emlabpy",
    version="0.0.0",
    description="electricity markets ABM",
    long_description="""
                modular python version of EMLAB
                       """,
    keywords=["ABM", "electricity markets"],
    author=", ".join(__author__),
    author_email=__email__,
    package_dir={"": "emlabpy"},
    packages=find_packages(where="emlabpy",
                           include=['domain', 'util', 'modules'],
                           exclude=['helpers'],
                           ),

    py_modules = ['domain', 'modules', 'util'],
    entry_points={ },
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Energy Modellers',
                 'License :: OSI Approved :: MIT License'],
    install_requires=[],
    extras_require={},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
)
