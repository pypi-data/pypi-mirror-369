import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-private-s3-hosting",
    "version": "0.0.15",
    "description": "CDK Construct for a private frontend hosting S3 bucket",
    "license": "Apache-2.0",
    "url": "https://github.com/badmintoncryer/cdk-private-s3-hosting.git",
    "long_description_content_type": "text/markdown",
    "author": "Kazuho CryerShinozuka<malaysia.cryer@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/badmintoncryer/cdk-private-s3-hosting.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk-private-s3-hosting",
        "cdk-private-s3-hosting._jsii"
    ],
    "package_data": {
        "cdk-private-s3-hosting._jsii": [
            "cdk-private-s3-hosting@0.0.15.jsii.tgz"
        ],
        "cdk-private-s3-hosting": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.130.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
