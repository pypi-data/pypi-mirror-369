r'''
# CDK VSCode Server Construct

This is a CDK Construct for creating a VSCode server on an Amazon Linux EC2 instance.

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-code-server)](https://constructs.dev/packages/cdk-code-server)

[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-code-server)
[![npm version](https://badge.fury.io/js/cdk-code-server.svg)](https://badge.fury.io/js/cdk-code-server)
[![Build Status](https://github.com/badmintoncryer/cdk-code-server/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-code-server/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-code-server/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-code-server/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-code-server.svg?style=flat)](https://www.npmjs.com/package/cdk-code-server)

![CDK VSCode Server Construct](./images/code-server.png)

You can easily access Visual Studio Code Server through your browser and start development.

In the EC2 security group's inbound rules, communication from the Internet is not allowed, ensuring secure access to the VSCode server.
Additionally, by passing the IAM policy to be attached to the EC2 instance as a property, you can grant appropriate permissions for AWS access within VSCode.

## Usage

Install the package:

```bash
npm install cdk-code-server
```

Use it in your CDK stack:

```python
import { CodeServer } from 'cdk-code-server';

new CodeServer(this, 'CodeServer');
```

You can customize the instance type, vpc, and other properties:

```python
import { CodeServer } from 'cdk-code-server';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

// Use an existing VPC
declare const vpc: ec2.IVpc;
// Use an existing policy as a instance role
declare const policy: iam.PolicyStatememnt;

new CodeServer(this, 'CodeServer', {
  vpc,
  // Specify the instance type
  // Default is c7g.2xlarge
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
  // Specify the CPU architecture
  // Default is ec2.AmazonLinuxCpuType.ARM_64
  cpuType: ec2.AmazonLinuxCpuType.X86_64,
  // Specify the IAM policy for the instance role
  // Default is a policy that has an administrator access
  policy,
  // Specify the size of the EBS volume
  // Default is 30 GB
  volumeSize: 100,
});
```

## Setup VSCode Server

After the stack is deployed, you can access the server via AWS Systems Manager (SSM) Session Manager by default and start the VSCode server:

### Access to the EC2 instance (Default: SSM)

1. In the AWS Console, go to the EC2 Instances page and select your instance.
2. Click the "Connect" button, choose "Session Manager", and click "Connect".
3. Once connected, switch to the ec2-user account:

```sh
sudo su --login ec2-user
```

### Start the VSCode server

Execute the following command to start the VSCode server:

```sh
[ec2-user@ip-10-0-0-23 ~]$ code tunnel service install
[2024-06-10 02:10:42] info Using GitHub for authentication, run `code tunnel user login --provider <provider>` option to change this.
To grant access to the server, please log into https://github.com/login/device and use code 3811-9932
```

Next, open your browser and go to [https://github.com/login/device](https://github.com/login/device), enter the code, and complete the authentication.

In the example above, enter '3811-9932' > Continue > Continue > Authorize-Visual-Studio-Code.

Return to the EC2 instance, run the code tunnel again, and open the displayed URL [https://vscode.dev/tunnel/ip-{privateIp}{region}](https://vscode.dev/tunnel/ip-%7BprivateIp%7D%7Bregion%7D) in your browser.

```sh
[ec2-user@ip-10-0-0-23 ~]$ code tunnel
*
* Visual Studio Code Server
*
* By using the software, you agree to
* the Visual Studio Code Server License Terms (https://aka.ms/vscode-server-license) and
* the Microsoft Privacy Statement (https://privacy.microsoft.com/en-US/privacystatement).
*
[2024-06-10 02:11:44] info Creating tunnel with the name: ip-10-0-0-23ap-north
[2024-06-10 02:11:44] info Open this link in your browser https://vscode.dev/tunnel/ip-10-0-0-23ap-north

Connected to an existing tunnel process running on this machine.

Open this link in your browser https://vscode.dev/tunnel/ip-10-0-0-23ap-north
```

VSCode will open, and you'll be prompted with "What type of account did you use to start this tunnel?" Select `GitHub`.

At this point, the GitHub authentication screen may appear again, so press Authorize.

Once you open the terminal, you’re all set.

![VSCode](./images/vscode.png)

---


### (Option) Access via EC2 Instance Connect Endpoint (EIC Endpoint)

If the `useInstanceConnectEndpoint` option is set to true, you can connect via the EC2 Instance Connect Endpoint.

1. In the AWS Console, go to the EC2 Instances page and select your instance.
2. Click the "Connect" button, choose "EC2 Instance Connect", then select "Connect using EC2 Instance Connect Endpoint", and click "Connect".
3. Once connected, you will see a screen similar to the following:

![EC2 Instance Connect](./images/console.png)

1. Follow the same steps as in the SSM section to start the VSCode server and connect via tunnel.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class CodeServer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-code-server.CodeServer",
):
    '''A CodeServer Construct.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cpu_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement] = None,
        use_instance_connect_endpoint: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cpu_type: The CPU type. Default: - ARM_64
        :param instance_type: The instance type. Default: - C7g.2xlarge
        :param policy: The IAM policy to attach to the instance role. Default: - Allow all actions on all resources
        :param use_instance_connect_endpoint: Whether to use EC2 instance connect endpoint for instance access. If set to true, it will create an EC2 Instance Connect Endpoint in the VPC. You can access the instance using either EC2 Instance Connect or SSM Session Manager. Default: false - Uses only SSM Session Manager for instance access
        :param user_data: User data to run when launching the instance. Default: - No additional user data
        :param volume_size: The size of the root volume in GiB. Default: 30
        :param vpc: The VPC where the instance will be deployed. Default: - A new VPC will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3dc073ef85aeeab8ffd2fe5c32c737ce76d0e4197f8d84ff2cfe4d4ae5bf187)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeServerProps(
            cpu_type=cpu_type,
            instance_type=instance_type,
            policy=policy,
            use_instance_connect_endpoint=use_instance_connect_endpoint,
            user_data=user_data,
            volume_size=volume_size,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-code-server.CodeServerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_type": "cpuType",
        "instance_type": "instanceType",
        "policy": "policy",
        "use_instance_connect_endpoint": "useInstanceConnectEndpoint",
        "user_data": "userData",
        "volume_size": "volumeSize",
        "vpc": "vpc",
    },
)
class CodeServerProps:
    def __init__(
        self,
        *,
        cpu_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement] = None,
        use_instance_connect_endpoint: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Properties for CodeServer construct.

        :param cpu_type: The CPU type. Default: - ARM_64
        :param instance_type: The instance type. Default: - C7g.2xlarge
        :param policy: The IAM policy to attach to the instance role. Default: - Allow all actions on all resources
        :param use_instance_connect_endpoint: Whether to use EC2 instance connect endpoint for instance access. If set to true, it will create an EC2 Instance Connect Endpoint in the VPC. You can access the instance using either EC2 Instance Connect or SSM Session Manager. Default: false - Uses only SSM Session Manager for instance access
        :param user_data: User data to run when launching the instance. Default: - No additional user data
        :param volume_size: The size of the root volume in GiB. Default: 30
        :param vpc: The VPC where the instance will be deployed. Default: - A new VPC will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb583e2cef71433ccfaa187bf48195bf7085ded509b20a2c01dc80cffe3f0229)
            check_type(argname="argument cpu_type", value=cpu_type, expected_type=type_hints["cpu_type"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument use_instance_connect_endpoint", value=use_instance_connect_endpoint, expected_type=type_hints["use_instance_connect_endpoint"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument volume_size", value=volume_size, expected_type=type_hints["volume_size"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_type is not None:
            self._values["cpu_type"] = cpu_type
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if policy is not None:
            self._values["policy"] = policy
        if use_instance_connect_endpoint is not None:
            self._values["use_instance_connect_endpoint"] = use_instance_connect_endpoint
        if user_data is not None:
            self._values["user_data"] = user_data
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cpu_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType]:
        '''The CPU type.

        :default: - ARM_64
        '''
        result = self._values.get("cpu_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''The instance type.

        :default: - C7g.2xlarge
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def policy(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''The IAM policy to attach to the instance role.

        :default: - Allow all actions on all resources
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], result)

    @builtins.property
    def use_instance_connect_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Whether to use EC2 instance connect endpoint for instance access.

        If set to true, it will create an EC2 Instance Connect Endpoint in the VPC.
        You can access the instance using either EC2 Instance Connect or SSM Session Manager.

        :default: false - Uses only SSM Session Manager for instance access
        '''
        result = self._values.get("use_instance_connect_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_data(self) -> typing.Optional[typing.List[builtins.str]]:
        '''User data to run when launching the instance.

        :default: - No additional user data
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''The size of the root volume in GiB.

        :default: 30
        '''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the instance will be deployed.

        :default: - A new VPC will be created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeServer",
    "CodeServerProps",
]

publication.publish()

def _typecheckingstub__a3dc073ef85aeeab8ffd2fe5c32c737ce76d0e4197f8d84ff2cfe4d4ae5bf187(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cpu_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement] = None,
    use_instance_connect_endpoint: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
    volume_size: typing.Optional[jsii.Number] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb583e2cef71433ccfaa187bf48195bf7085ded509b20a2c01dc80cffe3f0229(
    *,
    cpu_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.AmazonLinuxCpuType] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyStatement] = None,
    use_instance_connect_endpoint: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
    volume_size: typing.Optional[jsii.Number] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass
