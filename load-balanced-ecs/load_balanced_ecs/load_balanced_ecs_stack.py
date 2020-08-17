from aws_cdk import (
    core,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns
)


class LoadBalancedEcsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "CDK-LB",
            max_azs=2
        )

        cluster = ecs.Cluster(self, "CDK-Cluster", vpc=vpc)

        cluster.add_capacity(
            "DefaultAutoScalingGroup",
            instance_type=ec2.InstanceType("t3.nano"))

        task_definition = ecs.Ec2TaskDefinition(
            self, "nginx-awsvpc",
            network_mode=ecs.NetworkMode.BRIDGE,
        )

        container = task_definition.add_container(
            "nginx",
            image=ecs.ContainerImage.from_registry("nginx:latest"),
            cpu=100,
            memory_limit_mib=256,
            essential=True
        )
        port_mapping = ecs.PortMapping(
            container_port=80,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(port_mapping)

        ecs_service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "EC2-Service",
            cluster=cluster,
            memory_limit_mib=512,
            task_definition=task_definition,
            listener_port=80
        )

        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=ecs_service.load_balancer.load_balancer_dns_name
        )
