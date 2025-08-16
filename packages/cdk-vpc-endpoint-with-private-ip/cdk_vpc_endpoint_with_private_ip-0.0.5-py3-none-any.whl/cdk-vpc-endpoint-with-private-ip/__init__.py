r'''
# Interface VPC Endpoint with Private IP

This is a CDK construct that retrieves the private IP address of an Interface VPC Endpoint:

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-vpc-endpoint-with-private-ip)](https://constructs.dev/packages/cdk-vpc-endpoint-with-private-ip)
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-vpc-endpoint-with-private-ip)
[![npm version](https://badge.fury.io/js/cdk-vpc-endpoint-with-private-ip.svg)](https://badge.fury.io/js/cdk-vpc-endpoint-with-private-ip)
[![Build Status](https://github.com/badmintoncryer/cdk-vpc-endpoint-with-private-ip/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-vpc-endpoint-with-private-ip/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-vpc-endpoint-with-private-ip/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-vpc-endpoint-with-private-ip/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-vpc-endpoint-with-private-ip.svg?style=flat)](https://www.npmjs.com/package/cdk-vpc-endpoint-with-private-ip)

## Architecture

![Architecture](./images/architecture.png)

## Installation

```bash
npm install cdk-vpc-endpoint-with-private-ip
```

## Usage

You can create an interface VPC endpoint and retrive its private IP addresses using the `VpcEndpointWithPrivateIp` construct.

The `ec2.InterfaceVpcEndpointProps` can be passed to the construct to configure the interface VPC endpoint.

```python
import { InterfaceVpcEndpointWithPrivateIp } from 'cdk-vpc-endpoint-with-private-ip';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

declare const vpc: ec2.IVpc;

const endpoint = new InterfaceVpcEndpointWithPrivateIp(this, 'Endpoint', {
  vpc,
  service: ec2.InterfaceVpcEndpointAwsService.S3,
});

const privateIps = endpoint.privateIps;
```

**Note**: `privateIps` is an array of CDK Tokens, and the actual IP addresses are not determined until the stack is deployed.

## Special Thanks

I am greatly referencing the content of [this post](https://qiita.com/k_bobchin/items/c016cc65912a905b90ef).
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
import constructs as _constructs_77d1e7e8


class InterfaceVpcEndpointWithPrivateIp(
    _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-vpc-endpoint-with-private-ip.InterfaceVpcEndpointWithPrivateIp",
):
    '''CDK construct for an Interface VPC Endpoint with private IPs.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        service: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpointService,
        lookup_supported_azs: typing.Optional[builtins.bool] = None,
        open: typing.Optional[builtins.bool] = None,
        private_dns_enabled: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC network in which the interface endpoint will be used.
        :param service: The service to use for this interface VPC endpoint.
        :param lookup_supported_azs: Limit to only those availability zones where the endpoint service can be created. Setting this to 'true' requires a lookup to be performed at synthesis time. Account and region must be set on the containing stack for this to work. Default: false
        :param open: Whether to automatically allow VPC traffic to the endpoint. If enabled, all traffic to the endpoint from within the VPC will be automatically allowed. This is done based on the VPC's CIDR range. Default: true
        :param private_dns_enabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: set by the instance of IInterfaceVpcEndpointService, or true if not defined by the instance of IInterfaceVpcEndpointService
        :param security_groups: The security groups to associate with this interface VPC endpoint. Default: - a new security group is created
        :param subnets: The subnets in which to create an endpoint network interface. At most one per availability zone. Default: - private subnets
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6cc3ae9f824b3bfc52e0fe7a3c31f1941599e451aa9fe8d073476aa9ab8ae6c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointProps(
            vpc=vpc,
            service=service,
            lookup_supported_azs=lookup_supported_azs,
            open=open,
            private_dns_enabled=private_dns_enabled,
            security_groups=security_groups,
            subnets=subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="privateIps")
    def private_ips(self) -> typing.List[builtins.str]:
        '''The private IPs of the network interfaces of the VPC endpoint.'''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "privateIps"))


__all__ = [
    "InterfaceVpcEndpointWithPrivateIp",
]

publication.publish()

def _typecheckingstub__b6cc3ae9f824b3bfc52e0fe7a3c31f1941599e451aa9fe8d073476aa9ab8ae6c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    service: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpointService,
    lookup_supported_azs: typing.Optional[builtins.bool] = None,
    open: typing.Optional[builtins.bool] = None,
    private_dns_enabled: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
