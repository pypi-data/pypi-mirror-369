import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hdpws",
    version="0.6.26",
    description="NASA's Heliophysics Data Portal Web Service Client Library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://heliophysicsdata.gsfc.nasa.gov/WebServices",
    author="Bernie Harris",
    author_email="NASA-SPDF-Support@nasa.onmicrosoft.com",
    license="NOSA",
    packages=["hdpws"],
#    packages=find_packages(exclude=["tests"]),
#    packages=find_packages(),
    include_package_data=True,
    install_requires=["python-dateutil>=2.8.0", "requests>=2.20", "urllib3>=1.26.14"],
#    extras_require={
#        'plot': ["matplotlib>=3.3.2"],
#    },
    keywords=["heliophysics", "spase", "space physics", "spdf", "hdp"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
#        "License :: OSI Approved :: NASA Open Source Agreement",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
#    entry_points={
#        "console_scripts": [
#            hdpcws=hdpws.__main__:example",
#        ]
#    },
)
