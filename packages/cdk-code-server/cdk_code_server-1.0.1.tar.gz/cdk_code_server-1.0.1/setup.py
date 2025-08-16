import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-code-server",
    "version": "1.0.1",
    "description": "CDK Construct for a VSCode Server development environment on EC2",
    "license": "Apache-2.0",
    "url": "https://github.com/badmintoncryer/cdk-code-server.git",
    "long_description_content_type": "text/markdown",
    "author": "Kazuho CryerShinozuka<malaysia.cryer@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/badmintoncryer/cdk-code-server.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_code_server",
        "cdk_code_server._jsii"
    ],
    "package_data": {
        "cdk_code_server._jsii": [
            "cdk-code-server@1.0.1.jsii.tgz"
        ],
        "cdk_code_server": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.143.0, <3.0.0",
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
