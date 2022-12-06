import aws_cdk as cdk
from aws_cdk import assertions
import re

from stacks.ec2_rds import Ec2Rds


def test_snapshot(snapshot):
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    assert template.to_json() == snapshot


def test_vpc_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::EC2::VPC",
        {
            "CidrBlock": "172.32.0.0/16",
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True,
        },
    )


def test_vpc_resource_count():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::EC2::VPC", 1)


def test_vpc_subnet_resource_count():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::EC2::Subnet", 4)


def test_ec2_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::EC2::Instance",
        {
            "AvailabilityZone": {"Fn::Select": [0, assertions.Match.any_value()]},
            "IamInstanceProfile": {"Ref": assertions.Match.any_value()},
            "ImageId": {"Ref": assertions.Match.any_value()},
            "InstanceType": "t2.micro",
            "KeyName": assertions.Match.any_value(),
            "SecurityGroupIds": [
                {"Fn::GetAtt": [assertions.Match.any_value(), "GroupId"]}
            ],
            "SubnetId": {"Ref": assertions.Match.any_value()},
        },
    )


def test_ec2_resource_count():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::EC2::Instance", 1)


def test_security_group_ingress_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::EC2::SecurityGroup",
        {
            "SecurityGroupIngress": assertions.Match.array_with(
                [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "SSH",
                        "FromPort": 22,
                        "IpProtocol": "tcp",
                        "ToPort": 22,
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "HTTP",
                        "FromPort": 80,
                        "IpProtocol": "tcp",
                        "ToPort": 80,
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "HTTPS",
                        "FromPort": 443,
                        "IpProtocol": "tcp",
                        "ToPort": 443,
                    },
                ]
            )
        },
    )


def test_security_group_egress_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::EC2::SecurityGroup",
        {
            "SecurityGroupEgress": assertions.Match.array_with(
                [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Allow all outbound traffic by default",
                        "IpProtocol": "-1",
                    }
                ]
            )
        },
    )


def test_security_group_ingress_database_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::EC2::SecurityGroupIngress",
        assertions.Match.object_equals(
            {
                "Description": "DB Security Group",
                "FromPort": 3306,
                "GroupId": {"Fn::GetAtt": [assertions.Match.any_value(), "GroupId"]},
                "IpProtocol": "tcp",
                "SourceSecurityGroupId": {
                    "Fn::GetAtt": [assertions.Match.any_value(), "GroupId"]
                },
                "ToPort": 3306,
            },
        ),
    )


def test_database_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::RDS::DBInstance",
        {
            "DBInstanceClass": "db.t3.micro",
            "Engine": "mysql",
            "EngineVersion": "8.0.30",
            "StorageType": "gp2",
            "PubliclyAccessible": False,
        },
    )


def test_database_resource_count():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::RDS::DBInstance", 1)


def test_ec2_iam_policy_resource_properties():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::IAM::Policy",
        assertions.Match.object_equals(
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": "rds:*",
                            "Effect": "Allow",
                            "Resource": {"Fn::Join": assertions.Match.any_value()},
                        }
                    ],
                    "Version": "2012-10-17",
                },
                "PolicyName": assertions.Match.any_value(),
                "Roles": [{"Ref": assertions.Match.any_value()}],
            },
        ),
    )


def test_ec2_iam_policy_resource_count():
    app = cdk.Stack()
    stack = Ec2Rds(app, construct_id="blog")

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::IAM::Policy", 1)
