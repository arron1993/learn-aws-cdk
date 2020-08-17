#!/usr/bin/env python3

from aws_cdk import core

from load_balanced_ecs.load_balanced_ecs_stack import LoadBalancedEcsStack


app = core.App()
LoadBalancedEcsStack(app, "load-balanced-ecs")

app.synth()
