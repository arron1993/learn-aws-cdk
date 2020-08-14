#!/usr/bin/env python3

from aws_cdk import core

from new_instance.new_instance_stack import NewInstanceStack


app = core.App()
NewInstanceStack(app, "new-instance")

app.synth()
