#!/usr/bin/env python3

from aws_cdk import core

from new_bucket.new_bucket_stack import NewBucketStack


app = core.App()
NewBucketStack(app, "new-bucket")

app.synth()
