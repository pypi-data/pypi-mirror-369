r'''
# CDK Private S3 Hosting Construct

This is a CDK construct that creates a private S3 bucket and an Application Load Balancer (ALB) with a listener rule that forwards requests to the S3 bucket.

You can use this construct for a enterprise use case where you want to host a static website in a private network.

Original idea is from [this blog post](https://aws.amazon.com/jp/blogs/networking-and-content-delivery/hosting-internal-https-static-websites-with-alb-s3-and-privatelink/). And some implementations are referenced from [this post](https://qiita.com/k_bobchin/items/c016cc65912a905b90ef).

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-private-s3-hosting)](https://constructs.dev/packages/cdk-private-s3-hosting)
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-private-s3-hosting)
[![npm version](https://badge.fury.io/js/cdk-private-s3-hosting.svg)](https://badge.fury.io/js/cdk-private-s3-hosting)
[![Build Status](https://github.com/badmintoncryer/cdk-private-s3-hosting/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-private-s3-hosting/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-private-s3-hosting/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-private-s3-hosting/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-private-s3-hosting.svg?style=flat)](https://www.npmjs.com/package/cdk-private-s3-hosting)

## Architecture

![Architecture](./images/private_s3_hosting.png)

## Installation

You can install the package via npm:

```sh
npm install cdk-private-s3-hosting
```

## Usage

To create a private S3 bucket and an ALB with a listener rule that forwards requests to the S3 bucket, you can use the following code:

```python
import { PrivateS3Hosting } from 'cdk-private-s3-hosting';

const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
});
```

After you deploy the stack, you can access the S3 bucket using the ALB's DNS name from the VPC where the stack is deployed.

For example, if you put the `hoge.txt` file in the root of S3 bucket, you can access it using the following command:

```sh
curl http://cryer-nao-domain.com/hoge.txt
```

### Use existing VPC

You can use an existing VPC by specifying the `vpc` property.

```python
declare const vpc: ec2.IVpc;

const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
  vpc,
});
```

### Specify the sub domain

You can specify the sub domain by setting the `subDomain` property.

```python
const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
  subDomain: 'sub',
});
```

In this case, the S3 bucket name will be created with `${subDomain}.${domainName}`.

If `enablePrivateDns` is enabled, a private hosted zone will also be created for the `domainName` and an A record will be created from `${subDomain}.${domainName}` to the ALB DNS name.

You can retrieve `hoge.txt` on the root of the S3 bucket using the following command:

```sh
curl http://sub.cryer-nao-domain.com/hoge.txt
```

### Deploy the frontend assets

You can deploy the frontend assets to the S3 bucket like below:

```python
import { PrivateS3Hosting } from 'cdk-private-s3-hosting';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';

const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
});

new s3deploy.BucketDeployment(this, 'DeployWebsite', {
  sources: [s3deploy.Source.asset('./website-dist')],
  destinationBucket:  privateS3Hosting.bucket,
});
```

After deploying the stack, you can access the website using the `domainName` you specified from the VPC.

```sh
[cloudshell-user@ip-10-0-31-170 ~]$ curl http://cryer-nao-domain.com/ -L
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React + TS</title>
    <script type="module" crossorigin src="/assets/index-f40OySzR.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-DiwrgTda.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

**Note**: All access to the path pattern `*/` will be redirected to `/index.html`. Therefore, it will function correctly even when the path is set on the frontend and the page is reloaded.

**Note**: I also recommend to use [deploy-time-build](https://github.com/tmokmss/deploy-time-build) to build the frontend assets while deploying the stack.

### Setup DNS

This construct creates Route53 hosted zone and an A record for the domain name you specified by default.

If you want to use your own DNS settings(e.g. using a corporate DNS server),
you can disable the Route53 hosted zone creation by setting the `enablePrivateDns` property to `false`.

```python
import { PrivateS3Hosting } from 'cdk-private-s3-hosting';

const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
  enablePrivateDns: false,
});
```

### TLS Certificate

If you want to use HTTPS, you need to create a TLS certificate in ACM and pass it to the `certificate` property.

```python
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import { PrivateS3Hosting } from 'cdk-private-s3-hosting';

declare const certificate: acm.ICertificate;

const privateS3Hosting = new PrivateS3Hosting(this, 'PrivateS3Hosting', {
  domainName: 'cryer-nao-domain.com',
  certificate,
});
```

Of course, specified domain name (`domainName` and `subDomain`) must be the same as the domain name of the certificate.
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

import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class PrivateS3Hosting(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-private-s3-hosting.PrivateS3Hosting",
):
    '''A construct to host a private S3 website.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_props: typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]],
        domain_name: builtins.str,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        enable_private_dns: typing.Optional[builtins.bool] = None,
        internet_facing: typing.Optional[builtins.bool] = None,
        sub_domain: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_props: The properties for the S3 bucket. Default: - use default properties
        :param domain_name: The domain name for the website. S3 bucket name will be created with ``domainName``. If ``enablePrivateDns`` is enabled, a private hosted zone also will be created for the ``domainName`` and an A record has been created from ``domainName`` to the ALB DNS name.". If ``subDomein`` is provided, these names will be ``${subDomain}.${domainName}``.
        :param certificate: The certificate for the website. Default: - use HTTP
        :param enable_private_dns: Enable private DNS for the website. By eneabling this, a private hosted zone will be created for the domain name and an alias record will be created for the ALB You can access to the alb by the ``http(s)://<domainName>`` from the VPC Default: true
        :param internet_facing: Whether the ALB is internet facing. Default: false
        :param sub_domain: The sub domain for the website. S3 bucket name will be created with ``${subDomain}.{domainName}``. If ``enablePrivateDns`` is enabled, a private hosted zone also will be created for the ``domainName`` and an A record has been created from ``${subDomain}.${domainName}`` to the ALB DNS name.". Default: - no sub domain
        :param vpc: The VPC for the website. Default: - create a new VPC with 2 AZs and 0 NAT gateways
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f6a3822c2541f3c785fce5f3187d688039409f4677b681948fb4a3ae13d4292)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PrivateS3HostingProps(
            bucket_props=bucket_props,
            domain_name=domain_name,
            certificate=certificate,
            enable_private_dns=enable_private_dns,
            internet_facing=internet_facing,
            sub_domain=sub_domain,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer:
        '''The ALB to access the website.'''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer, jsii.get(self, "alb"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''The S3 bucket for hosting the website.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''The hosted zone for the website.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], jsii.get(self, "hostedZone"))


@jsii.data_type(
    jsii_type="cdk-private-s3-hosting.PrivateS3HostingProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_props": "bucketProps",
        "domain_name": "domainName",
        "certificate": "certificate",
        "enable_private_dns": "enablePrivateDns",
        "internet_facing": "internetFacing",
        "sub_domain": "subDomain",
        "vpc": "vpc",
    },
)
class PrivateS3HostingProps:
    def __init__(
        self,
        *,
        bucket_props: typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]],
        domain_name: builtins.str,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        enable_private_dns: typing.Optional[builtins.bool] = None,
        internet_facing: typing.Optional[builtins.bool] = None,
        sub_domain: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Properties for PrivateS3Hosting.

        :param bucket_props: The properties for the S3 bucket. Default: - use default properties
        :param domain_name: The domain name for the website. S3 bucket name will be created with ``domainName``. If ``enablePrivateDns`` is enabled, a private hosted zone also will be created for the ``domainName`` and an A record has been created from ``domainName`` to the ALB DNS name.". If ``subDomein`` is provided, these names will be ``${subDomain}.${domainName}``.
        :param certificate: The certificate for the website. Default: - use HTTP
        :param enable_private_dns: Enable private DNS for the website. By eneabling this, a private hosted zone will be created for the domain name and an alias record will be created for the ALB You can access to the alb by the ``http(s)://<domainName>`` from the VPC Default: true
        :param internet_facing: Whether the ALB is internet facing. Default: false
        :param sub_domain: The sub domain for the website. S3 bucket name will be created with ``${subDomain}.{domainName}``. If ``enablePrivateDns`` is enabled, a private hosted zone also will be created for the ``domainName`` and an A record has been created from ``${subDomain}.${domainName}`` to the ALB DNS name.". Default: - no sub domain
        :param vpc: The VPC for the website. Default: - create a new VPC with 2 AZs and 0 NAT gateways
        '''
        if isinstance(bucket_props, dict):
            bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f3ff047cbd8e8c18995347a63899f04375c4e4a279cffb2f203e5b1009daff0)
            check_type(argname="argument bucket_props", value=bucket_props, expected_type=type_hints["bucket_props"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument enable_private_dns", value=enable_private_dns, expected_type=type_hints["enable_private_dns"])
            check_type(argname="argument internet_facing", value=internet_facing, expected_type=type_hints["internet_facing"])
            check_type(argname="argument sub_domain", value=sub_domain, expected_type=type_hints["sub_domain"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_props": bucket_props,
            "domain_name": domain_name,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if enable_private_dns is not None:
            self._values["enable_private_dns"] = enable_private_dns
        if internet_facing is not None:
            self._values["internet_facing"] = internet_facing
        if sub_domain is not None:
            self._values["sub_domain"] = sub_domain
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def bucket_props(self) -> _aws_cdk_aws_s3_ceddda9d.BucketProps:
        '''The properties for the S3 bucket.

        :default: - use default properties
        '''
        result = self._values.get("bucket_props")
        assert result is not None, "Required property 'bucket_props' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.BucketProps, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The domain name for the website.

        S3 bucket name will be created with ``domainName``.

        If ``enablePrivateDns`` is enabled,
        a private hosted zone also will be created for the ``domainName``
        and an A record has been created from ``domainName`` to the ALB DNS name.".

        If ``subDomein`` is provided, these names will be ``${subDomain}.${domainName}``.
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''The certificate for the website.

        :default: - use HTTP
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def enable_private_dns(self) -> typing.Optional[builtins.bool]:
        '''Enable private DNS for the website.

        By eneabling this, a private hosted zone will be created for the domain name
        and an alias record will be created for the ALB

        You can access to the alb by the ``http(s)://<domainName>`` from the VPC

        :default: true
        '''
        result = self._values.get("enable_private_dns")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def internet_facing(self) -> typing.Optional[builtins.bool]:
        '''Whether the ALB is internet facing.

        :default: false
        '''
        result = self._values.get("internet_facing")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sub_domain(self) -> typing.Optional[builtins.str]:
        '''The sub domain for the website.

        S3 bucket name will be created with ``${subDomain}.{domainName}``.

        If ``enablePrivateDns`` is enabled,
        a private hosted zone also will be created for the ``domainName``
        and an A record has been created from ``${subDomain}.${domainName}`` to the ALB DNS name.".

        :default: - no sub domain
        '''
        result = self._values.get("sub_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC for the website.

        :default: - create a new VPC with 2 AZs and 0 NAT gateways
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrivateS3HostingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PrivateS3Hosting",
    "PrivateS3HostingProps",
]

publication.publish()

def _typecheckingstub__1f6a3822c2541f3c785fce5f3187d688039409f4677b681948fb4a3ae13d4292(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_props: typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]],
    domain_name: builtins.str,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    enable_private_dns: typing.Optional[builtins.bool] = None,
    internet_facing: typing.Optional[builtins.bool] = None,
    sub_domain: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f3ff047cbd8e8c18995347a63899f04375c4e4a279cffb2f203e5b1009daff0(
    *,
    bucket_props: typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]],
    domain_name: builtins.str,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    enable_private_dns: typing.Optional[builtins.bool] = None,
    internet_facing: typing.Optional[builtins.bool] = None,
    sub_domain: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass
