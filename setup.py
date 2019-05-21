import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gdrive_sync",
    version="0.0.1",
    author="Daniel Velez",
    author_email="daniel.enr.velez@gmail.com",
    description="A daemon to sync a directory with Google Drive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dan-velez/gdrive_sync",
    packages=setuptools.find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "watchdog",
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
