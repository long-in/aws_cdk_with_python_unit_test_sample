from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    CfnOutput as output,
)


class Ec2Rds(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db_pass = self.node.try_get_context("dbpass")

        """
        VPC作成
        """
        vpc = ec2.Vpc(
            self,
            id="vpc",
            cidr="172.32.0.0/16",
            max_azs=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
            nat_gateways=1,
        )

        """
        RDS作成
        """
        db_sg = ec2.SecurityGroup(
            self,
            id="db-sg",
            security_group_name="blog-db-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )

        rds_instance = rds.DatabaseInstance(
            self,
            id="db",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_30
            ),
            # t3.micro
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO,
            ),
            credentials=rds.Credentials.from_generated_secret(
                username="blog_db_user",
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            ),
            security_groups=[db_sg],
        )
        rds_instance.node.add_dependency(vpc)

        """
        EC2(Web)作成
        """
        web_sg = ec2.SecurityGroup(
            self,
            id="web-sg",
            security_group_name="blog-web-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        web_sg.add_ingress_rule(
           peer=ec2.Peer.any_ipv4(),
           connection=ec2.Port.tcp(22),
           description="SSH",
        )
        web_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="HTTP",
        )
        web_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS",
        )

        ec2_instance = ec2.Instance(
            self,
            id="web",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            ),
            vpc=vpc,
            key_name="blog-ssh-key",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=web_sg,
        )
        ec2_instance.node.add_dependency(rds_instance)

        iam_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["rds:*"],
            resources=[rds_instance.instance_arn],
        )
        ec2_instance.role.add_to_principal_policy(iam_policy)

        """
        セキュリティグループ設定
        """
        lookup_db_sg = ec2.SecurityGroup.from_security_group_id(
            self, id="lookup-db-sg", security_group_id=db_sg.security_group_id
        )
        lookup_db_sg.add_ingress_rule(
            peer=ec2.Peer.security_group_id(web_sg.security_group_id),
            connection=ec2.Port.tcp(3306),
            description="DB Security Group",
        )

        """
        出力
        """
        output(
            self,
            id="output_ec2_public_ipaddress",
            value=ec2_instance.instance_public_ip,
        )
        output(
            self,
            id="output_db_endpoint",
            value=rds_instance.db_instance_endpoint_address,
        )
