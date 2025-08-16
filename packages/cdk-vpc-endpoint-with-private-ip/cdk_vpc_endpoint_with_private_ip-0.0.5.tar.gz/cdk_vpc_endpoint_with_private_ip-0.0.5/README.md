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
