from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    core)

from aws_cdk.aws_s3_assets import Asset


class NewInstanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        vpc = ec2.Vpc(self,
                      "NewInstanceVPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public",
                          subnet_type=ec2.SubnetType.PUBLIC
                      )]
                      )

        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        role = iam.Role(self, "InstanceSSM",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AmazonEC2RoleforSSM"))

        instance = ec2.Instance(
            self,
            "CDKNewInstance",
            instance_type=ec2.InstanceType("t3.nano"),
            key_name="arronmoore_com_v2",
            machine_image=amzn_linux,
            vpc=vpc,
            security_group=self.configure_security_group(vpc),
            role=role)

        asset = Asset(self, "NewInstanceConfigureScript",
                      path="./new_instance/configure.sh")

        local_path = instance.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )

        instance.user_data.add_execute_file_command(
            file_path=local_path
        )

    def configure_security_group(self, vpc):
        sg = ec2.SecurityGroup(
            self, "HttpSshIn", vpc=vpc)

        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP In"
        )
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH In"
        )
        return sg
