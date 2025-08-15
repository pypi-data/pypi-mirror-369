r'''
# CDK StackSets Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This construct library allows you to define AWS CloudFormation StackSets.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_accounts(
        regions=["us-east-1"],
        accounts=["11111111111"],
        parameter_overrides={
            "SomeParam": "overrideValue"
        }
    ),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

## Installing

### TypeScript/JavaScript

```bash
npm install cdk-stacksets
```

### Python

```bash
pip install cdk-stacksets
```

### Java

```xml
// add this to your pom.xml
<dependency>
    <groupId>io.github.cdklabs</groupId>
    <artifactId>cdk-stacksets</artifactId>
    <version>0.0.0</version> // replace with version
</dependency>
```

### .NET

```bash
dotnet add package CdklabsCdkStacksets --version X.X.X
```

### Go

```bash
go get cdk-stacksets-go
```

## Creating a StackSet Stack

StackSets allow you to deploy a single CloudFormation template across multiple AWS accounts and regions.
Typically when creating a CDK Stack that will be deployed across multiple environments, the CDK will
synthesize separate Stack templates for each environment (account/region combination). Because of the
way that StackSets work, StackSet Stacks behave differently. For Stacks that will be deployed via StackSets
a single Stack is defined and synthesized. Any environmental differences must be encoded using Parameters.

A special class was created to handle the uniqueness of the StackSet Stack.
You declare a `StackSetStack` the same way that you declare a normal `Stack`, but there
are a couple of differences. `StackSetStack`s have a couple of special requirements/limitations when
compared to Stacks.

*Requirements*

* Must be created in the scope of a `Stack`
* Must be environment agnostic

*Limitations*

* Does not support Docker container assets

Once you create a `StackSetStack` you can create resources within the stack.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "StackSet")

iam.Role(stack_set_stack, "MyRole",
    assumed_by=iam.ServicePrincipal("myservice.amazonaws.com")
)
```

Or

```python
class MyStackSet(StackSetStack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        iam.Role(self, "MyRole",
            assumed_by=iam.ServicePrincipal("myservice.amazonaws.com")
        )
```

## Creating a StackSet

AWS CloudFormation StackSets enable you to create, update, or delete stacks across multiple accounts and AWS Regions
with a single operation. Using an administrator account, you define and manage an AWS CloudFormation template, and use
the template as the basis for provisioning stacks into selected target accounts across specific AWS Regions.

There are two methods for defining *where* the StackSet should be deployed. You can either define individual accounts, or
you can define AWS Organizations organizational units.

### Deploying to individual accounts

Deploying to individual accounts requires you to specify the account ids. If you want to later deploy to additional accounts,
or remove the stackset from accounts, this has to be done by adding/removing the account id from the list.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_accounts(
        regions=["us-east-1"],
        accounts=["11111111111"]
    ),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

### Deploying to organizational units

AWS Organizations is an AWS service that enables you to centrally manage and govern multiple accounts.
AWS Organizations allows you to define organizational units (OUs) which are logical groupings of AWS accounts.
OUs enable you to organize your accounts into a hierarchy and make it easier for you to apply management controls.
For a deep dive on OU best practices you can read the [Best Practices for Organizational Units with AWS Organizations](https://aws.amazon.com/blogs/mt/best-practices-for-organizational-units-with-aws-organizations/) blog post.

You can either specify the organization itself, or individual OUs. By default the StackSet will be deployed
to all AWS accounts that are part of the OU. If the OU is nested it will also deploy to all accounts
that are part of any nested OUs.

For example, given the following org hierarchy

```mermaid
graph TD
  root-->ou-1;
  root-->ou-2;
  ou-1-->ou-3;
  ou-1-->ou-4;
  ou-3-->account-1;
  ou-3-->account-2;
  ou-4-->account-4;
  ou-2-->account-3;
  ou-2-->account-5;
```

You could deploy to all AWS accounts under OUs `ou-1`, `ou-3`, `ou-4` by specifying the following:

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_organizational_units(
        regions=["us-east-1"],
        organizational_units=["ou-1"]
    ),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

This would deploy the StackSet to `account-1`, `account-2`, `account-4`.

If there are specific AWS accounts that are part of the specified OU hierarchy that you would like
to exclude, this can be done by specifying `excludeAccounts`.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_organizational_units(
        regions=["us-east-1"],
        organizational_units=["ou-1"],
        exclude_accounts=["account-2"]
    ),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

This would deploy only to `account-1` & `account-4`, and would exclude `account-2`.

Sometimes you might have individual accounts that you would like to deploy the StackSet to, but
you do not want to include the entire OU. To do that you can specify `additionalAccounts`.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_organizational_units(
        regions=["us-east-1"],
        organizational_units=["ou-1"],
        additional_accounts=["account-5"]
    ),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

This would deploy the StackSet to `account-1`, `account-2`, `account-4` & `account-5`.

### StackSet permissions

There are two modes for managing StackSet permissions (i.e. *where* StackSets can deploy & *what* resources they can create).
A StackSet can either be `Service Managed` or `Self Managed`.

You can control this through the `deploymentType` parameter.

#### Service Managed

When a StackSet is service managed, the permissions are managed by AWS Organizations. This allows the StackSet to deploy the Stack to *any*
account within the organization. In addition, the StackSet will be able to create *any* type of resource.

```python
stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet")

StackSet(stack, "StackSet",
    target=StackSetTarget.from_organizational_units(
        regions=["us-east-1"],
        organizational_units=["ou-1"]
    ),
    deployment_type=DeploymentType.service_managed(),
    template=StackSetTemplate.from_stack_set_stack(stack_set_stack)
)
```

When you specify `serviceManaged` deployment type, automatic deployments are enabled by default.
Automatic deployments allow the StackSet to be automatically deployed to or deleted from
AWS accounts when they are added or removed from the specified organizational units.

### Using File Assets

You can use the StackSet's parent stack to facilitate file assets. Behind the scenes,
this is accomplished using the `BucketDeployment` construct from the
`aws_s3_deployment` module. You need to provide a list of buckets outside the scope of the CDK
managed asset buckets and ensure you have permissions for the target accounts to pull
the artifacts from the supplied bucket(s).

As a basic example, if using a `serviceManaged` deployment, you just need to give read
access to the Organization. You can create the asset bucket in the parent stack, or another
stack in the same app and pass the object as a prop. Or, import an existing bucket as needed.

If creating in the parent or sibling stack you could create and export similar to this:

```python
bucket = s3.Bucket(self, "Assets",
    bucket_name="prefix-us-east-1"
)

bucket.add_to_resource_policy(
    iam.PolicyStatement(
        actions=["s3:Get*", "s3:List*"],
        resources=[bucket.arn_for_objects("*"), bucket.bucket_arn],
        principals=[iam.OrganizationPrincipal("o-xyz")]
    ))
```

Then pass as a prop to the StackSet stack:

```python
# bucket: s3.Bucket

stack = Stack()
stack_set_stack = StackSetStack(stack, "MyStackSet",
    asset_buckets=[bucket],
    asset_bucket_prefix="prefix"
)
```

To faciliate multi region deployments, there is an assetBucketPrefix property. This
gets added to the region the Stack Set is deployed to. The stack synthesis for
the Stack Set would look for a bucket named `prefix-{Region}` in the example
above. `{Region}` is whatever region you are deploying the Stack Set to as
defined in your target property of the StackSet. You will need to ensure the
bucket name is correct based on what was previously created and then passed in.

You can use self-managed StackSet deployments with file assets too but will
need to ensure all target accounts roles will have access to the central asset
bucket you pass as the property.

## Deploying StackSets using CDK Pipelines

You can also deploy StackSets using [CDK Pipelines](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html)

Below is an example of a Pipeline that deploys from a central account. It also
defines separate stages for each "environment" so that you can first test out
the stackset in pre-prod environments.

This would be an automated way of deploying the bootstrap stack described in
[this blog
post](https://aws.amazon.com/blogs/mt/bootstrapping-multiple-aws-accounts-for-aws-cdk-using-cloudformation-stacksets/).

```python
# app: App


class BootstrapStage(Stage):
    def __init__(self, scope, id, *, initialBootstrapTarget, stacksetName=None, env=None, outdir=None, stageName=None, permissionsBoundary=None, policyValidationBeta1=None):
        super().__init__(scope, id, initialBootstrapTarget=initialBootstrapTarget, stacksetName=stacksetName, env=env, outdir=outdir, stageName=stageName, permissionsBoundary=permissionsBoundary, policyValidationBeta1=policyValidationBeta1)

        stack = Stack(self, "BootstrapStackSet")

        bootstrap = Bootstrap(stack, "CDKToolkit")

        stack_set = StackSet(stack, "StackSet",
            template=StackSetTemplate.from_stack_set_stack(bootstrap),
            target=initial_bootstrap_target,
            capabilities=[Capability.NAMED_IAM],
            managed_execution=True,
            stack_set_name=stackset_name,
            deployment_type=DeploymentType.service_managed(
                delegated_admin=True,
                auto_deploy_enabled=True,
                auto_deploy_retain_stacks=False
            ),
            operation_preferences=OperationPreferences(
                region_concurrency_type=RegionConcurrencyType.PARALLEL,
                max_concurrent_percentage=100,
                failure_tolerance_percentage=99
            )
        )

pipeline = pipelines.CodePipeline(self, "BootstrapPipeline",
    synth=pipelines.ShellStep("Synth",
        commands=["yarn install --frozen-lockfile", "npx cdk synth"
        ],
        input=pipelines.CodePipelineSource.connection("myorg/myrepo", "main",
            connection_arn="arn:aws:codestar-connections:us-east-2:111111111111:connection/ca65d487-ca6e-41cc-aab2-645db37fdb2b"
        )
    ),
    self_mutation=True
)

regions = ["us-east-1", "us-east-2", "us-west-2", "eu-west-2", "eu-west-1", "ap-south-1", "ap-southeast-1"
]

pipeline.add_stage(
    BootstrapStage(app, "DevBootstrap",
        env=Environment(
            region="us-east-1",
            account="111111111111"
        ),
        stackset_name="CDKToolkit-dev",
        initial_bootstrap_target=StackSetTarget.from_organizational_units(
            regions=regions,
            organizational_units=["ou-hrza-ar333427"]
        )
    ))

pipeline.add_stage(
    BootstrapStage(app, "ProdBootstrap",
        env=Environment(
            region="us-east-1",
            account="111111111111"
        ),
        stackset_name="CDKToolkit-prd",
        initial_bootstrap_target=StackSetTarget.from_organizational_units(
            regions=regions,
            organizational_units=["ou-hrza-bb999427", "ou-hraa-ar111127"]
        )
    ))
```
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="cdk-stacksets.Capability")
class Capability(enum.Enum):
    '''(experimental) StackSets that contains certain functionality require an explicit acknowledgement that the stack contains these capabilities.

    :stability: experimental
    '''

    NAMED_IAM = "NAMED_IAM"
    '''(experimental) Required if the stack contains IAM resources with custom names.

    :stability: experimental
    '''
    IAM = "IAM"
    '''(experimental) Required if the stack contains IAM resources.

    If the IAM resources
    also have custom names then specify {@link Capability.NAMED_IAM} instead.

    :stability: experimental
    '''
    AUTO_EXPAND = "AUTO_EXPAND"
    '''(experimental) Required if the stack contains macros.

    Not supported if deploying
    a service managed stackset.

    :stability: experimental
    '''


class DeploymentType(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-stacksets.DeploymentType",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="selfManaged")
    @builtins.classmethod
    def self_managed(
        cls,
        *,
        admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        execution_role_name: typing.Optional[builtins.str] = None,
    ) -> "DeploymentType":
        '''(experimental) StackSets deployed using the self managed model require you to create the necessary IAM roles in the source and target AWS accounts and to setup the required IAM permissions.

        Using this model you can only deploy to AWS accounts that have the necessary IAM roles/permissions
        pre-created.

        :param admin_role: (experimental) The admin role that CloudFormation will use to perform stackset operations. This role should only have permissions to be assumed by the CloudFormation service and to assume the execution role in each individual account. When you create the execution role it must have an assume role policy statement which allows ``sts:AssumeRole`` from this admin role. To grant specific users/groups access to use this role to deploy stacksets they must have a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource. Default: - a default role will be created
        :param execution_role_name: (experimental) The name of the stackset execution role that already exists in each target AWS account. This role must be configured with a trust policy that allows ``sts:AssumeRole`` from the ``adminRole``. In addition this role must have the necessary permissions to manage the resources created by the stackset. Default: - AWSCloudFormationStackSetExecutionRole

        :stability: experimental
        '''
        options = SelfManagedOptions(
            admin_role=admin_role, execution_role_name=execution_role_name
        )

        return typing.cast("DeploymentType", jsii.sinvoke(cls, "selfManaged", [options]))

    @jsii.member(jsii_name="serviceManaged")
    @builtins.classmethod
    def service_managed(
        cls,
        *,
        auto_deploy_enabled: typing.Optional[builtins.bool] = None,
        auto_deploy_retain_stacks: typing.Optional[builtins.bool] = None,
        delegated_admin: typing.Optional[builtins.bool] = None,
    ) -> "DeploymentType":
        '''(experimental) StackSets deployed using service managed permissions allow you to deploy StackSet instances to accounts within an AWS Organization.

        Using this module
        AWS Organizations will handle creating the necessary IAM roles and setting up the
        required permissions.

        This model also allows you to enable automated deployments which allows the StackSet
        to be automatically deployed to new accounts that are added to your organization in the future.

        This model requires you to be operating in either the AWS Organizations management account
        or the delegated administrator account

        :param auto_deploy_enabled: (experimental) Whether or not the StackSet should automatically create/remove the Stack from AWS accounts that are added/removed from an organizational unit. This has no effect if {@link StackSetTarget.fromAccounts} is used Default: true
        :param auto_deploy_retain_stacks: (experimental) Whether stacks should be removed from AWS accounts that are removed from an organizational unit. By default the stack will be retained (not deleted) This has no effect if {@link StackSetTarget.fromAccounts} is used Default: true
        :param delegated_admin: (experimental) Whether or not the account this StackSet is deployed from is the delegated admin account. Set this to ``false`` if you are using the AWS Organizations management account instead. Default: true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-concepts.html#stacksets-concepts-stackset-permission-models
        :stability: experimental
        '''
        options = ServiceManagedOptions(
            auto_deploy_enabled=auto_deploy_enabled,
            auto_deploy_retain_stacks=auto_deploy_retain_stacks,
            delegated_admin=delegated_admin,
        )

        return typing.cast("DeploymentType", jsii.sinvoke(cls, "serviceManaged", [options]))


class _DeploymentTypeProxy(DeploymentType):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, DeploymentType).__jsii_proxy_class__ = lambda : _DeploymentTypeProxy


@jsii.interface(jsii_type="cdk-stacksets.IStackSet")
class IStackSet(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a CloudFormation StackSet.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Only available on self managed stacksets.

        The admin role that CloudFormation will use to perform stackset operations.
        This role should only have permissions to be assumed by the CloudFormation service
        and to assume the execution role in each individual account.

        When you create the execution role it must have an assume role policy statement which
        allows ``sts:AssumeRole`` from this admin role.

        To grant specific users/groups access to use this role to deploy stacksets they must have
        a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource.

        :stability: experimental
        '''
        ...


class _IStackSetProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a CloudFormation StackSet.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk-stacksets.IStackSet"

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Only available on self managed stacksets.

        The admin role that CloudFormation will use to perform stackset operations.
        This role should only have permissions to be assumed by the CloudFormation service
        and to assume the execution role in each individual account.

        When you create the execution role it must have an assume role policy statement which
        allows ``sts:AssumeRole`` from this admin role.

        To grant specific users/groups access to use this role to deploy stacksets they must have
        a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStackSet).__jsii_proxy_class__ = lambda : _IStackSetProxy


@jsii.data_type(
    jsii_type="cdk-stacksets.OperationPreferences",
    jsii_struct_bases=[],
    name_mapping={
        "failure_tolerance_count": "failureToleranceCount",
        "failure_tolerance_percentage": "failureTolerancePercentage",
        "max_concurrent_count": "maxConcurrentCount",
        "max_concurrent_percentage": "maxConcurrentPercentage",
        "region_concurrency_type": "regionConcurrencyType",
        "region_order": "regionOrder",
    },
)
class OperationPreferences:
    def __init__(
        self,
        *,
        failure_tolerance_count: typing.Optional[jsii.Number] = None,
        failure_tolerance_percentage: typing.Optional[jsii.Number] = None,
        max_concurrent_count: typing.Optional[jsii.Number] = None,
        max_concurrent_percentage: typing.Optional[jsii.Number] = None,
        region_concurrency_type: typing.Optional["RegionConcurrencyType"] = None,
        region_order: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param failure_tolerance_count: 
        :param failure_tolerance_percentage: 
        :param max_concurrent_count: 
        :param max_concurrent_percentage: 
        :param region_concurrency_type: 
        :param region_order: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__532d2b9ee70ce09bd7372939ac079a6c6398c4b6efbec1cc0787757d79e57be2)
            check_type(argname="argument failure_tolerance_count", value=failure_tolerance_count, expected_type=type_hints["failure_tolerance_count"])
            check_type(argname="argument failure_tolerance_percentage", value=failure_tolerance_percentage, expected_type=type_hints["failure_tolerance_percentage"])
            check_type(argname="argument max_concurrent_count", value=max_concurrent_count, expected_type=type_hints["max_concurrent_count"])
            check_type(argname="argument max_concurrent_percentage", value=max_concurrent_percentage, expected_type=type_hints["max_concurrent_percentage"])
            check_type(argname="argument region_concurrency_type", value=region_concurrency_type, expected_type=type_hints["region_concurrency_type"])
            check_type(argname="argument region_order", value=region_order, expected_type=type_hints["region_order"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if failure_tolerance_count is not None:
            self._values["failure_tolerance_count"] = failure_tolerance_count
        if failure_tolerance_percentage is not None:
            self._values["failure_tolerance_percentage"] = failure_tolerance_percentage
        if max_concurrent_count is not None:
            self._values["max_concurrent_count"] = max_concurrent_count
        if max_concurrent_percentage is not None:
            self._values["max_concurrent_percentage"] = max_concurrent_percentage
        if region_concurrency_type is not None:
            self._values["region_concurrency_type"] = region_concurrency_type
        if region_order is not None:
            self._values["region_order"] = region_order

    @builtins.property
    def failure_tolerance_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("failure_tolerance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def failure_tolerance_percentage(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("failure_tolerance_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrent_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_concurrent_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrent_percentage(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_concurrent_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def region_concurrency_type(self) -> typing.Optional["RegionConcurrencyType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("region_concurrency_type")
        return typing.cast(typing.Optional["RegionConcurrencyType"], result)

    @builtins.property
    def region_order(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("region_order")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperationPreferences(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-stacksets.RegionConcurrencyType")
class RegionConcurrencyType(enum.Enum):
    '''
    :stability: experimental
    '''

    SEQUENTIAL = "SEQUENTIAL"
    '''
    :stability: experimental
    '''
    PARALLEL = "PARALLEL"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk-stacksets.SelfManagedOptions",
    jsii_struct_bases=[],
    name_mapping={
        "admin_role": "adminRole",
        "execution_role_name": "executionRoleName",
    },
)
class SelfManagedOptions:
    def __init__(
        self,
        *,
        admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        execution_role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for StackSets that are not managed by AWS Organizations.

        :param admin_role: (experimental) The admin role that CloudFormation will use to perform stackset operations. This role should only have permissions to be assumed by the CloudFormation service and to assume the execution role in each individual account. When you create the execution role it must have an assume role policy statement which allows ``sts:AssumeRole`` from this admin role. To grant specific users/groups access to use this role to deploy stacksets they must have a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource. Default: - a default role will be created
        :param execution_role_name: (experimental) The name of the stackset execution role that already exists in each target AWS account. This role must be configured with a trust policy that allows ``sts:AssumeRole`` from the ``adminRole``. In addition this role must have the necessary permissions to manage the resources created by the stackset. Default: - AWSCloudFormationStackSetExecutionRole

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1356ba9bc9f7fd56ce4184da84fea18de54beb183391cee5bc3fcd2367944cde)
            check_type(argname="argument admin_role", value=admin_role, expected_type=type_hints["admin_role"])
            check_type(argname="argument execution_role_name", value=execution_role_name, expected_type=type_hints["execution_role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if admin_role is not None:
            self._values["admin_role"] = admin_role
        if execution_role_name is not None:
            self._values["execution_role_name"] = execution_role_name

    @builtins.property
    def admin_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The admin role that CloudFormation will use to perform stackset operations.

        This role should only have permissions to be assumed by the CloudFormation service
        and to assume the execution role in each individual account.

        When you create the execution role it must have an assume role policy statement which
        allows ``sts:AssumeRole`` from this admin role.

        To grant specific users/groups access to use this role to deploy stacksets they must have
        a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource.

        :default: - a default role will be created

        :stability: experimental
        '''
        result = self._values.get("admin_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def execution_role_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the stackset execution role that already exists in each target AWS account.

        This role must be configured with a trust policy that allows ``sts:AssumeRole`` from the ``adminRole``.

        In addition this role must have the necessary permissions to manage the resources created by the stackset.

        :default: - AWSCloudFormationStackSetExecutionRole

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html#stacksets-prereqs-accountsetup
        :stability: experimental
        '''
        result = self._values.get("execution_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfManagedOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-stacksets.ServiceManagedOptions",
    jsii_struct_bases=[],
    name_mapping={
        "auto_deploy_enabled": "autoDeployEnabled",
        "auto_deploy_retain_stacks": "autoDeployRetainStacks",
        "delegated_admin": "delegatedAdmin",
    },
)
class ServiceManagedOptions:
    def __init__(
        self,
        *,
        auto_deploy_enabled: typing.Optional[builtins.bool] = None,
        auto_deploy_retain_stacks: typing.Optional[builtins.bool] = None,
        delegated_admin: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for StackSets that are managed by AWS Organizations.

        :param auto_deploy_enabled: (experimental) Whether or not the StackSet should automatically create/remove the Stack from AWS accounts that are added/removed from an organizational unit. This has no effect if {@link StackSetTarget.fromAccounts} is used Default: true
        :param auto_deploy_retain_stacks: (experimental) Whether stacks should be removed from AWS accounts that are removed from an organizational unit. By default the stack will be retained (not deleted) This has no effect if {@link StackSetTarget.fromAccounts} is used Default: true
        :param delegated_admin: (experimental) Whether or not the account this StackSet is deployed from is the delegated admin account. Set this to ``false`` if you are using the AWS Organizations management account instead. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b12ac336f4c477af06d201780d9fe3e06c8d6537cb54706f909a8e60c18d068)
            check_type(argname="argument auto_deploy_enabled", value=auto_deploy_enabled, expected_type=type_hints["auto_deploy_enabled"])
            check_type(argname="argument auto_deploy_retain_stacks", value=auto_deploy_retain_stacks, expected_type=type_hints["auto_deploy_retain_stacks"])
            check_type(argname="argument delegated_admin", value=delegated_admin, expected_type=type_hints["delegated_admin"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_deploy_enabled is not None:
            self._values["auto_deploy_enabled"] = auto_deploy_enabled
        if auto_deploy_retain_stacks is not None:
            self._values["auto_deploy_retain_stacks"] = auto_deploy_retain_stacks
        if delegated_admin is not None:
            self._values["delegated_admin"] = delegated_admin

    @builtins.property
    def auto_deploy_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not the StackSet should automatically create/remove the Stack from AWS accounts that are added/removed from an organizational unit.

        This has no effect if {@link StackSetTarget.fromAccounts} is used

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_deploy_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_deploy_retain_stacks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether stacks should be removed from AWS accounts that are removed from an organizational unit.

        By default the stack will be retained (not deleted)

        This has no effect if {@link StackSetTarget.fromAccounts} is used

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_deploy_retain_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def delegated_admin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not the account this StackSet is deployed from is the delegated admin account.

        Set this to ``false`` if you are using the AWS Organizations management account instead.

        :default: true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-delegated-admin.html
        :stability: experimental
        '''
        result = self._values.get("delegated_admin")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceManagedOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStackSet)
class StackSet(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-stacksets.StackSet",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        target: "StackSetTarget",
        template: "StackSetTemplate",
        capabilities: typing.Optional[typing.Sequence[Capability]] = None,
        deployment_type: typing.Optional[DeploymentType] = None,
        description: typing.Optional[builtins.str] = None,
        managed_execution: typing.Optional[builtins.bool] = None,
        operation_preferences: typing.Optional[typing.Union[OperationPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param target: (experimental) Which accounts/OUs and regions to deploy the StackSet to.
        :param template: (experimental) The Stack that will be deployed to the target.
        :param capabilities: (experimental) Specify a list of capabilities required by your stackset. StackSets that contains certain functionality require an explicit acknowledgement that the stack contains these capabilities. If you deploy a stack that requires certain capabilities and they are not specified, the deployment will fail with a ``InsufficientCapabilities`` error. Default: - no specific capabilities
        :param deployment_type: (experimental) The type of deployment for this StackSet. The deployment can either be managed by AWS Organizations (i.e. DeploymentType.serviceManaged()) or by the AWS account that the StackSet is deployed from. In order to use DeploymentType.serviceManaged() the account needs to either be the organizations's management account or a delegated administrator account. Default: DeploymentType.selfManaged()
        :param description: (experimental) An optional description to add to the StackSet. Default: - no description
        :param managed_execution: (experimental) If this is ``true`` then StackSets will perform non-conflicting operations concurrently and queue any conflicting operations. This means that you can submit more than one operation per StackSet and they will be executed concurrently. For example you can submit a single request that updates existing stack instances *and* creates new stack instances. Any conflicting operations will be queued for immediate processing once the conflict is resolved. Default: true
        :param operation_preferences: 
        :param stack_set_name: (experimental) The name of the stack set. Default: - CloudFormation generated name

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bb8983a1d8fd24e330d2073844f02b75b6955adbf7f984f5ef22ed13a401a34)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StackSetProps(
            target=target,
            template=template,
            capabilities=capabilities,
            deployment_type=deployment_type,
            description=description,
            managed_execution=managed_execution,
            operation_preferences=operation_preferences,
            stack_set_name=stack_set_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: "StackSetTarget") -> None:
        '''
        :param target: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb8f6c3abd64f0882dce39947103c2fb79452f1b8519b72d961b39469b5a932e)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        return typing.cast(None, jsii.invoke(self, "addTarget", [target]))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Only available on self managed stacksets.

        The admin role that CloudFormation will use to perform stackset operations.
        This role should only have permissions to be assumed by the CloudFormation service
        and to assume the execution role in each individual account.

        When you create the execution role it must have an assume role policy statement which
        allows ``sts:AssumeRole`` from this admin role.

        To grant specific users/groups access to use this role to deploy stacksets they must have
        a policy that allows ``iam:GetRole`` & ``iam:PassRole`` on this role resource.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="cdk-stacksets.StackSetProps",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "template": "template",
        "capabilities": "capabilities",
        "deployment_type": "deploymentType",
        "description": "description",
        "managed_execution": "managedExecution",
        "operation_preferences": "operationPreferences",
        "stack_set_name": "stackSetName",
    },
)
class StackSetProps:
    def __init__(
        self,
        *,
        target: "StackSetTarget",
        template: "StackSetTemplate",
        capabilities: typing.Optional[typing.Sequence[Capability]] = None,
        deployment_type: typing.Optional[DeploymentType] = None,
        description: typing.Optional[builtins.str] = None,
        managed_execution: typing.Optional[builtins.bool] = None,
        operation_preferences: typing.Optional[typing.Union[OperationPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target: (experimental) Which accounts/OUs and regions to deploy the StackSet to.
        :param template: (experimental) The Stack that will be deployed to the target.
        :param capabilities: (experimental) Specify a list of capabilities required by your stackset. StackSets that contains certain functionality require an explicit acknowledgement that the stack contains these capabilities. If you deploy a stack that requires certain capabilities and they are not specified, the deployment will fail with a ``InsufficientCapabilities`` error. Default: - no specific capabilities
        :param deployment_type: (experimental) The type of deployment for this StackSet. The deployment can either be managed by AWS Organizations (i.e. DeploymentType.serviceManaged()) or by the AWS account that the StackSet is deployed from. In order to use DeploymentType.serviceManaged() the account needs to either be the organizations's management account or a delegated administrator account. Default: DeploymentType.selfManaged()
        :param description: (experimental) An optional description to add to the StackSet. Default: - no description
        :param managed_execution: (experimental) If this is ``true`` then StackSets will perform non-conflicting operations concurrently and queue any conflicting operations. This means that you can submit more than one operation per StackSet and they will be executed concurrently. For example you can submit a single request that updates existing stack instances *and* creates new stack instances. Any conflicting operations will be queued for immediate processing once the conflict is resolved. Default: true
        :param operation_preferences: 
        :param stack_set_name: (experimental) The name of the stack set. Default: - CloudFormation generated name

        :stability: experimental
        '''
        if isinstance(operation_preferences, dict):
            operation_preferences = OperationPreferences(**operation_preferences)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4161f9686610a433c925f6372e470f48b6d7120ea7d32a3cbbde55fb7b0c8c26)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument template", value=template, expected_type=type_hints["template"])
            check_type(argname="argument capabilities", value=capabilities, expected_type=type_hints["capabilities"])
            check_type(argname="argument deployment_type", value=deployment_type, expected_type=type_hints["deployment_type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument managed_execution", value=managed_execution, expected_type=type_hints["managed_execution"])
            check_type(argname="argument operation_preferences", value=operation_preferences, expected_type=type_hints["operation_preferences"])
            check_type(argname="argument stack_set_name", value=stack_set_name, expected_type=type_hints["stack_set_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target": target,
            "template": template,
        }
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if deployment_type is not None:
            self._values["deployment_type"] = deployment_type
        if description is not None:
            self._values["description"] = description
        if managed_execution is not None:
            self._values["managed_execution"] = managed_execution
        if operation_preferences is not None:
            self._values["operation_preferences"] = operation_preferences
        if stack_set_name is not None:
            self._values["stack_set_name"] = stack_set_name

    @builtins.property
    def target(self) -> "StackSetTarget":
        '''(experimental) Which accounts/OUs and regions to deploy the StackSet to.

        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast("StackSetTarget", result)

    @builtins.property
    def template(self) -> "StackSetTemplate":
        '''(experimental) The Stack that will be deployed to the target.

        :stability: experimental
        '''
        result = self._values.get("template")
        assert result is not None, "Required property 'template' is missing"
        return typing.cast("StackSetTemplate", result)

    @builtins.property
    def capabilities(self) -> typing.Optional[typing.List[Capability]]:
        '''(experimental) Specify a list of capabilities required by your stackset.

        StackSets that contains certain functionality require an explicit acknowledgement
        that the stack contains these capabilities.

        If you deploy a stack that requires certain capabilities and they are
        not specified, the deployment will fail with a ``InsufficientCapabilities`` error.

        :default: - no specific capabilities

        :stability: experimental
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[Capability]], result)

    @builtins.property
    def deployment_type(self) -> typing.Optional[DeploymentType]:
        '''(experimental) The type of deployment for this StackSet.

        The deployment can either be managed by
        AWS Organizations (i.e. DeploymentType.serviceManaged()) or by the AWS account that
        the StackSet is deployed from.

        In order to use DeploymentType.serviceManaged() the account needs to either be the
        organizations's management account or a delegated administrator account.

        :default: DeploymentType.selfManaged()

        :stability: experimental
        '''
        result = self._values.get("deployment_type")
        return typing.cast(typing.Optional[DeploymentType], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional description to add to the StackSet.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_execution(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If this is ``true`` then StackSets will perform non-conflicting operations concurrently and queue any conflicting operations.

        This means that you can submit more than one operation per StackSet and they will be
        executed concurrently. For example you can submit a single request that updates existing
        stack instances *and* creates new stack instances. Any conflicting operations will be queued
        for immediate processing once the conflict is resolved.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("managed_execution")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def operation_preferences(self) -> typing.Optional[OperationPreferences]:
        '''
        :stability: experimental
        '''
        result = self._values.get("operation_preferences")
        return typing.cast(typing.Optional[OperationPreferences], result)

    @builtins.property
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the stack set.

        :default: - CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("stack_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StackSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StackSetStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-stacksets.StackSetStack",
):
    '''(experimental) A StackSet stack, which is similar to a normal CloudFormation stack with some differences.

    This stack will not be treated as an independent deployment
    artifact (won't be listed in "cdk list" or deployable through "cdk deploy"),
    but rather only synthesized as a template and uploaded as an asset to S3.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asset_bucket_prefix: typing.Optional[builtins.str] = None,
        asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param asset_bucket_prefix: 
        :param asset_buckets: (experimental) A Bucket can be passed to store assets, enabling StackSetStack Asset support. Default: No Bucket provided and Assets will not be supported.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4758df2485abe28fb9e05eccba5e0fae8033263a2a24fb99f3a01767d9a0dbf1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StackSetStackProps(
            asset_bucket_prefix=asset_bucket_prefix, asset_buckets=asset_buckets
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="templateFile")
    def template_file(self) -> builtins.str:
        '''(experimental) The name of the CloudFormation template file emitted to the output directory during synthesis.

        Example value: ``MyStack.template.json``

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "templateFile"))


@jsii.data_type(
    jsii_type="cdk-stacksets.StackSetStackProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset_bucket_prefix": "assetBucketPrefix",
        "asset_buckets": "assetBuckets",
    },
)
class StackSetStackProps:
    def __init__(
        self,
        *,
        asset_bucket_prefix: typing.Optional[builtins.str] = None,
        asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    ) -> None:
        '''(experimental) StackSet stack props.

        :param asset_bucket_prefix: 
        :param asset_buckets: (experimental) A Bucket can be passed to store assets, enabling StackSetStack Asset support. Default: No Bucket provided and Assets will not be supported.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__559cf9ce09d7c5259515cb7e1653fd3b691ad2ea9d3c2616f65e2231ff884d4c)
            check_type(argname="argument asset_bucket_prefix", value=asset_bucket_prefix, expected_type=type_hints["asset_bucket_prefix"])
            check_type(argname="argument asset_buckets", value=asset_buckets, expected_type=type_hints["asset_buckets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_bucket_prefix is not None:
            self._values["asset_bucket_prefix"] = asset_bucket_prefix
        if asset_buckets is not None:
            self._values["asset_buckets"] = asset_buckets

    @builtins.property
    def asset_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("asset_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''(experimental) A Bucket can be passed to store assets, enabling StackSetStack Asset support.

        :default: No Bucket provided and Assets will not be supported.

        :stability: experimental
        '''
        result = self._values.get("asset_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StackSetStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StackSetStackSynthesizer(
    _aws_cdk_ceddda9d.StackSynthesizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-stacksets.StackSetStackSynthesizer",
):
    '''(experimental) Deployment environment for an AWS StackSet stack.

    Interoperates with the StackSynthesizer of the parent stack.

    :stability: experimental
    '''

    def __init__(
        self,
        asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        asset_bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param asset_buckets: -
        :param asset_bucket_prefix: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d0988039aa883385f869265875340f24a3a73c393096bd6f589b2397e68462f)
            check_type(argname="argument asset_buckets", value=asset_buckets, expected_type=type_hints["asset_buckets"])
            check_type(argname="argument asset_bucket_prefix", value=asset_bucket_prefix, expected_type=type_hints["asset_bucket_prefix"])
        jsii.create(self.__class__, self, [asset_buckets, asset_bucket_prefix])

    @jsii.member(jsii_name="addDockerImageAsset")
    def add_docker_image_asset(
        self,
        *,
        source_hash: builtins.str,
        asset_name: typing.Optional[builtins.str] = None,
        directory_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_ssh: typing.Optional[builtins.str] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        docker_cache_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_file: typing.Optional[builtins.str] = None,
        docker_outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.DockerImageAssetLocation:
        '''(experimental) Register a Docker Image Asset.

        Returns the parameters that can be used to refer to the asset inside the template.

        The synthesizer must rely on some out-of-band mechanism to make sure the given files
        are actually placed in the returned location before the deployment happens. This can
        be by writing the instructions to the asset manifest (for use by the ``cdk-assets`` tool),
        by relying on the CLI to upload files (legacy behavior), or some other operator controlled
        mechanism.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_secrets: Build secrets to pass to the ``docker build`` command. Since Docker build secrets are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build secrets are passed
        :param docker_build_ssh: SSH agent socket or keys to pass to the ``docker buildx`` command. Default: - no ssh arg is passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from args are passed
        :param docker_cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to args are passed
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param docker_outputs: Outputs to pass to the ``docker build`` command. Default: - no build args are passed
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param network_mode: Networking mode for the RUN commands during build. *Requires Docker Engine API v1.25+*. Specify this property to build images on a specific networking mode. Default: - no networking mode specified
        :param platform: Platform to build for. *Requires Docker Buildx*. Specify this property to build images on a specific platform. Default: - no platform specified (the current machine architecture will be used)

        :stability: experimental
        '''
        _asset = _aws_cdk_ceddda9d.DockerImageAssetSource(
            source_hash=source_hash,
            asset_name=asset_name,
            directory_name=directory_name,
            docker_build_args=docker_build_args,
            docker_build_secrets=docker_build_secrets,
            docker_build_ssh=docker_build_ssh,
            docker_build_target=docker_build_target,
            docker_cache_from=docker_cache_from,
            docker_cache_to=docker_cache_to,
            docker_file=docker_file,
            docker_outputs=docker_outputs,
            executable=executable,
            network_mode=network_mode,
            platform=platform,
        )

        return typing.cast(_aws_cdk_ceddda9d.DockerImageAssetLocation, jsii.invoke(self, "addDockerImageAsset", [_asset]))

    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(
        self,
        *,
        source_hash: builtins.str,
        deploy_time: typing.Optional[builtins.bool] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[_aws_cdk_ceddda9d.FileAssetPackaging] = None,
    ) -> _aws_cdk_ceddda9d.FileAssetLocation:
        '''(experimental) Register a File Asset.

        Returns the parameters that can be used to refer to the asset inside the template.

        The synthesizer must rely on some out-of-band mechanism to make sure the given files
        are actually placed in the returned location before the deployment happens. This can
        be by writing the instructions to the asset manifest (for use by the ``cdk-assets`` tool),
        by relying on the CLI to upload files (legacy behavior), or some other operator controlled
        mechanism.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.

        :stability: experimental
        '''
        asset = _aws_cdk_ceddda9d.FileAssetSource(
            source_hash=source_hash,
            deploy_time=deploy_time,
            executable=executable,
            file_name=file_name,
            packaging=packaging,
        )

        return typing.cast(_aws_cdk_ceddda9d.FileAssetLocation, jsii.invoke(self, "addFileAsset", [asset]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, session: _aws_cdk_ceddda9d.ISynthesisSession) -> None:
        '''(experimental) Synthesize the associated stack to the session.

        :param session: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2f89c8496872e4a2edad64206237ccda014f80101076e57d23cc9b6c84fac2)
            check_type(argname="argument session", value=session, expected_type=type_hints["session"])
        return typing.cast(None, jsii.invoke(self, "synthesize", [session]))


class StackSetTarget(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-stacksets.StackSetTarget",
):
    '''(experimental) Which organizational units and/or accounts the stack set should be deployed to.

    ``fromAccounts`` can be used to deploy the stack set to specific AWS accounts

    ``fromOrganizationalUnits`` can be used to deploy the stack set to specific organizational units
    and optionally include additional accounts from other OUs, or exclude accounts from the specified
    OUs

    :stability: experimental

    Example::

        # deploy to specific accounts
        StackSetTarget.from_accounts(
            accounts=["11111111111", "22222222222"],
            regions=["us-east-1", "us-east-2"]
        )
        
        # deploy to OUs and 1 additional account
        StackSetTarget.from_organizational_units(
            regions=["us-east-1", "us-east-2"],
            organizational_units=["ou-1111111", "ou-2222222"],
            additional_accounts=["33333333333"]
        )
        
        # deploy to OUs but exclude 1 account
        StackSetTarget.from_organizational_units(
            regions=["us-east-1", "us-east-2"],
            organizational_units=["ou-1111111", "ou-2222222"],
            exclude_accounts=["11111111111"]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAccounts")
    @builtins.classmethod
    def from_accounts(
        cls,
        *,
        accounts: typing.Sequence[builtins.str],
        regions: typing.Sequence[builtins.str],
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> "StackSetTarget":
        '''(experimental) Deploy the StackSet to a list of accounts.

        :param accounts: (experimental) A list of AWS accounts to deploy the StackSet to.
        :param regions: (experimental) A list of regions the Stack should be deployed to. If {@link StackSetProps.operationPreferences.regionOrder } is specified then the StackSet will be deployed sequentially otherwise it will be deployed to all regions in parallel.
        :param parameter_overrides: (experimental) Parameter overrides that should be applied to only this target. Default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental

        Example::

            StackSetTarget.from_accounts(
                accounts=["11111111111", "22222222222"],
                regions=["us-east-1", "us-east-2"]
            )
        '''
        options = AccountsTargetOptions(
            accounts=accounts, regions=regions, parameter_overrides=parameter_overrides
        )

        return typing.cast("StackSetTarget", jsii.sinvoke(cls, "fromAccounts", [options]))

    @jsii.member(jsii_name="fromOrganizationalUnits")
    @builtins.classmethod
    def from_organizational_units(
        cls,
        *,
        organizational_units: typing.Sequence[builtins.str],
        additional_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        regions: typing.Sequence[builtins.str],
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> "StackSetTarget":
        '''(experimental) Deploy the StackSet to a list of AWS Organizations organizational units.

        You can optionally include/exclude individual AWS accounts.

        :param organizational_units: (experimental) A list of organizational unit ids to deploy to. The StackSet will deploy the provided Stack template to all accounts in the OU. This can be further filtered by specifying either ``additionalAccounts`` or ``excludeAccounts``. If the ``deploymentType`` is specified with ``autoDeployEnabled`` then the StackSet will automatically deploy the Stack to new accounts as they are added to the specified ``organizationalUnits``
        :param additional_accounts: (experimental) A list of additional AWS accounts to deploy the StackSet to. This can be used to deploy the StackSet to additional AWS accounts that exist in a different OU than what has been provided in ``organizationalUnits`` Default: - Stacks will only be deployed to accounts that exist in the specified organizationalUnits
        :param exclude_accounts: (experimental) A list of AWS accounts to exclude from deploying the StackSet to. This can be useful if there are accounts that exist in an OU that is provided in ``organizationalUnits``, but you do not want the StackSet to be deployed. Default: - Stacks will be deployed to all accounts that exist in the OUs specified in the organizationUnits property
        :param regions: (experimental) A list of regions the Stack should be deployed to. If {@link StackSetProps.operationPreferences.regionOrder } is specified then the StackSet will be deployed sequentially otherwise it will be deployed to all regions in parallel.
        :param parameter_overrides: (experimental) Parameter overrides that should be applied to only this target. Default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental

        Example::

            StackSetTarget.from_organizational_units(
                regions=["us-east-1", "us-east-2"],
                organizational_units=["ou-1111111", "ou-2222222"]
            )
        '''
        options = OrganizationsTargetOptions(
            organizational_units=organizational_units,
            additional_accounts=additional_accounts,
            exclude_accounts=exclude_accounts,
            regions=regions,
            parameter_overrides=parameter_overrides,
        )

        return typing.cast("StackSetTarget", jsii.sinvoke(cls, "fromOrganizationalUnits", [options]))


class _StackSetTargetProxy(StackSetTarget):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, StackSetTarget).__jsii_proxy_class__ = lambda : _StackSetTargetProxy


class StackSetTemplate(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-stacksets.StackSetTemplate",
):
    '''(experimental) Represents a StackSet CloudFormation template.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromStackSetStack")
    @builtins.classmethod
    def from_stack_set_stack(cls, stack: StackSetStack) -> "StackSetTemplate":
        '''
        :param stack: the stack to use as the base for the stackset template.

        :return: StackSetTemplate

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a35ef13fe0e5fd32912a05b209a5698e2f686aeecf949676b3b00d1b1770aaf6)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast("StackSetTemplate", jsii.sinvoke(cls, "fromStackSetStack", [stack]))

    @builtins.property
    @jsii.member(jsii_name="templateUrl")
    @abc.abstractmethod
    def template_url(self) -> builtins.str:
        '''(experimental) The S3 URL of the StackSet template.

        :stability: experimental
        '''
        ...


class _StackSetTemplateProxy(StackSetTemplate):
    @builtins.property
    @jsii.member(jsii_name="templateUrl")
    def template_url(self) -> builtins.str:
        '''(experimental) The S3 URL of the StackSet template.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "templateUrl"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, StackSetTemplate).__jsii_proxy_class__ = lambda : _StackSetTemplateProxy


@jsii.data_type(
    jsii_type="cdk-stacksets.TargetOptions",
    jsii_struct_bases=[],
    name_mapping={"regions": "regions", "parameter_overrides": "parameterOverrides"},
)
class TargetOptions:
    def __init__(
        self,
        *,
        regions: typing.Sequence[builtins.str],
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Common options for deploying a StackSet to a target.

        :param regions: (experimental) A list of regions the Stack should be deployed to. If {@link StackSetProps.operationPreferences.regionOrder } is specified then the StackSet will be deployed sequentially otherwise it will be deployed to all regions in parallel.
        :param parameter_overrides: (experimental) Parameter overrides that should be applied to only this target. Default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae71f2c3c92f05d32314df3d271970ddbf3f6d937dd13d4333accd290c344ea3)
            check_type(argname="argument regions", value=regions, expected_type=type_hints["regions"])
            check_type(argname="argument parameter_overrides", value=parameter_overrides, expected_type=type_hints["parameter_overrides"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regions": regions,
        }
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides

    @builtins.property
    def regions(self) -> typing.List[builtins.str]:
        '''(experimental) A list of regions the Stack should be deployed to.

        If {@link StackSetProps.operationPreferences.regionOrder } is specified
        then the StackSet will be deployed sequentially otherwise it will be
        deployed to all regions in parallel.

        :stability: experimental
        '''
        result = self._values.get("regions")
        assert result is not None, "Required property 'regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Parameter overrides that should be applied to only this target.

        :default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-stacksets.AccountsTargetOptions",
    jsii_struct_bases=[TargetOptions],
    name_mapping={
        "regions": "regions",
        "parameter_overrides": "parameterOverrides",
        "accounts": "accounts",
    },
)
class AccountsTargetOptions(TargetOptions):
    def __init__(
        self,
        *,
        regions: typing.Sequence[builtins.str],
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        accounts: typing.Sequence[builtins.str],
    ) -> None:
        '''(experimental) Options for deploying a StackSet to a list of AWS accounts.

        :param regions: (experimental) A list of regions the Stack should be deployed to. If {@link StackSetProps.operationPreferences.regionOrder } is specified then the StackSet will be deployed sequentially otherwise it will be deployed to all regions in parallel.
        :param parameter_overrides: (experimental) Parameter overrides that should be applied to only this target. Default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }
        :param accounts: (experimental) A list of AWS accounts to deploy the StackSet to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b80141462b0d2ec29c180d4a361656a4cd373536791c5a4180675d662f58307)
            check_type(argname="argument regions", value=regions, expected_type=type_hints["regions"])
            check_type(argname="argument parameter_overrides", value=parameter_overrides, expected_type=type_hints["parameter_overrides"])
            check_type(argname="argument accounts", value=accounts, expected_type=type_hints["accounts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regions": regions,
            "accounts": accounts,
        }
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides

    @builtins.property
    def regions(self) -> typing.List[builtins.str]:
        '''(experimental) A list of regions the Stack should be deployed to.

        If {@link StackSetProps.operationPreferences.regionOrder } is specified
        then the StackSet will be deployed sequentially otherwise it will be
        deployed to all regions in parallel.

        :stability: experimental
        '''
        result = self._values.get("regions")
        assert result is not None, "Required property 'regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Parameter overrides that should be applied to only this target.

        :default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def accounts(self) -> typing.List[builtins.str]:
        '''(experimental) A list of AWS accounts to deploy the StackSet to.

        :stability: experimental
        '''
        result = self._values.get("accounts")
        assert result is not None, "Required property 'accounts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountsTargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-stacksets.OrganizationsTargetOptions",
    jsii_struct_bases=[TargetOptions],
    name_mapping={
        "regions": "regions",
        "parameter_overrides": "parameterOverrides",
        "organizational_units": "organizationalUnits",
        "additional_accounts": "additionalAccounts",
        "exclude_accounts": "excludeAccounts",
    },
)
class OrganizationsTargetOptions(TargetOptions):
    def __init__(
        self,
        *,
        regions: typing.Sequence[builtins.str],
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        organizational_units: typing.Sequence[builtins.str],
        additional_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for deploying a StackSet to a set of Organizational Units (OUs).

        :param regions: (experimental) A list of regions the Stack should be deployed to. If {@link StackSetProps.operationPreferences.regionOrder } is specified then the StackSet will be deployed sequentially otherwise it will be deployed to all regions in parallel.
        :param parameter_overrides: (experimental) Parameter overrides that should be applied to only this target. Default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }
        :param organizational_units: (experimental) A list of organizational unit ids to deploy to. The StackSet will deploy the provided Stack template to all accounts in the OU. This can be further filtered by specifying either ``additionalAccounts`` or ``excludeAccounts``. If the ``deploymentType`` is specified with ``autoDeployEnabled`` then the StackSet will automatically deploy the Stack to new accounts as they are added to the specified ``organizationalUnits``
        :param additional_accounts: (experimental) A list of additional AWS accounts to deploy the StackSet to. This can be used to deploy the StackSet to additional AWS accounts that exist in a different OU than what has been provided in ``organizationalUnits`` Default: - Stacks will only be deployed to accounts that exist in the specified organizationalUnits
        :param exclude_accounts: (experimental) A list of AWS accounts to exclude from deploying the StackSet to. This can be useful if there are accounts that exist in an OU that is provided in ``organizationalUnits``, but you do not want the StackSet to be deployed. Default: - Stacks will be deployed to all accounts that exist in the OUs specified in the organizationUnits property

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86f6824f0a2fbea9562beddf80d6f0110789fae217a0cfd1452623d3e3d17e5b)
            check_type(argname="argument regions", value=regions, expected_type=type_hints["regions"])
            check_type(argname="argument parameter_overrides", value=parameter_overrides, expected_type=type_hints["parameter_overrides"])
            check_type(argname="argument organizational_units", value=organizational_units, expected_type=type_hints["organizational_units"])
            check_type(argname="argument additional_accounts", value=additional_accounts, expected_type=type_hints["additional_accounts"])
            check_type(argname="argument exclude_accounts", value=exclude_accounts, expected_type=type_hints["exclude_accounts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regions": regions,
            "organizational_units": organizational_units,
        }
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides
        if additional_accounts is not None:
            self._values["additional_accounts"] = additional_accounts
        if exclude_accounts is not None:
            self._values["exclude_accounts"] = exclude_accounts

    @builtins.property
    def regions(self) -> typing.List[builtins.str]:
        '''(experimental) A list of regions the Stack should be deployed to.

        If {@link StackSetProps.operationPreferences.regionOrder } is specified
        then the StackSet will be deployed sequentially otherwise it will be
        deployed to all regions in parallel.

        :stability: experimental
        '''
        result = self._values.get("regions")
        assert result is not None, "Required property 'regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Parameter overrides that should be applied to only this target.

        :default: - use parameter overrides specified in {@link StackSetProps.parameterOverrides }

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def organizational_units(self) -> typing.List[builtins.str]:
        '''(experimental) A list of organizational unit ids to deploy to.

        The StackSet will
        deploy the provided Stack template to all accounts in the OU.
        This can be further filtered by specifying either ``additionalAccounts``
        or ``excludeAccounts``.

        If the ``deploymentType`` is specified with ``autoDeployEnabled`` then
        the StackSet will automatically deploy the Stack to new accounts as they
        are added to the specified ``organizationalUnits``

        :stability: experimental
        '''
        result = self._values.get("organizational_units")
        assert result is not None, "Required property 'organizational_units' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def additional_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of additional AWS accounts to deploy the StackSet to.

        This can be
        used to deploy the StackSet to additional AWS accounts that exist in a
        different OU than what has been provided in ``organizationalUnits``

        :default:

        - Stacks will only be deployed to accounts that exist in the
        specified organizationalUnits

        :stability: experimental
        '''
        result = self._values.get("additional_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exclude_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of AWS accounts to exclude from deploying the StackSet to.

        This can
        be useful if there are accounts that exist in an OU that is provided in
        ``organizationalUnits``, but you do not want the StackSet to be deployed.

        :default:

        - Stacks will be deployed to all accounts that exist in the OUs
        specified in the organizationUnits property

        :stability: experimental
        '''
        result = self._values.get("exclude_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationsTargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountsTargetOptions",
    "Capability",
    "DeploymentType",
    "IStackSet",
    "OperationPreferences",
    "OrganizationsTargetOptions",
    "RegionConcurrencyType",
    "SelfManagedOptions",
    "ServiceManagedOptions",
    "StackSet",
    "StackSetProps",
    "StackSetStack",
    "StackSetStackProps",
    "StackSetStackSynthesizer",
    "StackSetTarget",
    "StackSetTemplate",
    "TargetOptions",
]

publication.publish()

def _typecheckingstub__532d2b9ee70ce09bd7372939ac079a6c6398c4b6efbec1cc0787757d79e57be2(
    *,
    failure_tolerance_count: typing.Optional[jsii.Number] = None,
    failure_tolerance_percentage: typing.Optional[jsii.Number] = None,
    max_concurrent_count: typing.Optional[jsii.Number] = None,
    max_concurrent_percentage: typing.Optional[jsii.Number] = None,
    region_concurrency_type: typing.Optional[RegionConcurrencyType] = None,
    region_order: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1356ba9bc9f7fd56ce4184da84fea18de54beb183391cee5bc3fcd2367944cde(
    *,
    admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    execution_role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b12ac336f4c477af06d201780d9fe3e06c8d6537cb54706f909a8e60c18d068(
    *,
    auto_deploy_enabled: typing.Optional[builtins.bool] = None,
    auto_deploy_retain_stacks: typing.Optional[builtins.bool] = None,
    delegated_admin: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bb8983a1d8fd24e330d2073844f02b75b6955adbf7f984f5ef22ed13a401a34(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    target: StackSetTarget,
    template: StackSetTemplate,
    capabilities: typing.Optional[typing.Sequence[Capability]] = None,
    deployment_type: typing.Optional[DeploymentType] = None,
    description: typing.Optional[builtins.str] = None,
    managed_execution: typing.Optional[builtins.bool] = None,
    operation_preferences: typing.Optional[typing.Union[OperationPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8f6c3abd64f0882dce39947103c2fb79452f1b8519b72d961b39469b5a932e(
    target: StackSetTarget,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4161f9686610a433c925f6372e470f48b6d7120ea7d32a3cbbde55fb7b0c8c26(
    *,
    target: StackSetTarget,
    template: StackSetTemplate,
    capabilities: typing.Optional[typing.Sequence[Capability]] = None,
    deployment_type: typing.Optional[DeploymentType] = None,
    description: typing.Optional[builtins.str] = None,
    managed_execution: typing.Optional[builtins.bool] = None,
    operation_preferences: typing.Optional[typing.Union[OperationPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4758df2485abe28fb9e05eccba5e0fae8033263a2a24fb99f3a01767d9a0dbf1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asset_bucket_prefix: typing.Optional[builtins.str] = None,
    asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__559cf9ce09d7c5259515cb7e1653fd3b691ad2ea9d3c2616f65e2231ff884d4c(
    *,
    asset_bucket_prefix: typing.Optional[builtins.str] = None,
    asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d0988039aa883385f869265875340f24a3a73c393096bd6f589b2397e68462f(
    asset_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    asset_bucket_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2f89c8496872e4a2edad64206237ccda014f80101076e57d23cc9b6c84fac2(
    session: _aws_cdk_ceddda9d.ISynthesisSession,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a35ef13fe0e5fd32912a05b209a5698e2f686aeecf949676b3b00d1b1770aaf6(
    stack: StackSetStack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae71f2c3c92f05d32314df3d271970ddbf3f6d937dd13d4333accd290c344ea3(
    *,
    regions: typing.Sequence[builtins.str],
    parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b80141462b0d2ec29c180d4a361656a4cd373536791c5a4180675d662f58307(
    *,
    regions: typing.Sequence[builtins.str],
    parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    accounts: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86f6824f0a2fbea9562beddf80d6f0110789fae217a0cfd1452623d3e3d17e5b(
    *,
    regions: typing.Sequence[builtins.str],
    parameter_overrides: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    organizational_units: typing.Sequence[builtins.str],
    additional_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    exclude_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
