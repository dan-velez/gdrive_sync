from setuptools import setup

setup(
    name='gdrive_sync',
    version='1.0.0',
    author='Daniel Velez',
    author_email='daniel.enr.velez@gmail.com',
    maintainer='Robin Nabel',
    maintainer_email='rnabel@ucdavis.edu',
    packages=['pydrive', 'pydrive.test'],
    url='https://github.com/gsuitedevs/PyDrive',
    license='LICENSE',
    description='Google Drive API made easy.',
    long_description=open('README.rst').read(),
    install_requires=[
        "google-api-python-client >= 1.2",
        "oauth2client >= 4.0.0",
        "PyYAML >= 3.0",
    ],
)
