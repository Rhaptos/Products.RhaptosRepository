from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read("Products", "RhaptosRepository", "version.txt").strip()

setup(
    name='Products.RhaptosRepository',
    version=version,
    description="",
    long_description='\n'.join([
        read("Products", "RhaptosRepository", "README.txt"),
        read("CHANGES"),
        ]),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='',
    author='Rhaptos developers',
    author_email='rhaptos@cnx.rice.edu',
    url='http://rhaptos.org',
    license='',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.RhaptosModuleStorage',
        'Products.RhaptosCacheTool',
        'Products.References',
        ],
    extras_require={
        'test': ['plone.app.testing',],
        },
    )
