# Classification (U)

"""Program:  setup.py

    Description:  A setuptools based setup module.

"""

# Libraries and Global Variables

# Standard
import os
import setuptools

# Third-party

# Local
import version


# Read in long description from README file.
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f_hdlr:
    LONG_DESCRIPTION = f_hdlr.read()

setuptools.setup(
    name="Process_Graphplots",
    description="Processes imagery graph plot files.",
    author="Mark Pernot",
    author_email="Mark.J.Pernot@coe.ic.gov",
    url="https://sc.appdev.proj.coe.ic.gov/JAC-DSXD/process-graphplots",
    version=version.__version__,
    platforms=["Linux"],
    long_description=LONG_DESCRIPTION,

    classifiers=[
        # Common Values:
        #  2 - Pre-Alpha
        #  3 - Alpha
        #  4 - Beta
        #  5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Operating System :: Linux",
        "Operating System :: Linux :: Centos",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6"])
