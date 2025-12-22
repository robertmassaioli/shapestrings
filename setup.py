from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "advanced_shapestrings", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.advanced_shapestrings',
      version=str(__version__),
      packages=['freecad',
                'freecad.advanced_shapestrings'],
      maintainer="Robert Massaioli",
      maintainer_email="freecad@rmdir.app",
      url="github.com/echo_rm/advanced-shapestrings",
      description="Advanced tools that work like Shapestrings but even more powerful.",
      install_requires=[],
      include_package_data=True)
