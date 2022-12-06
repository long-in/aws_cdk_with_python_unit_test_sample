#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.ec2_rds import Ec2Rds

app = cdk.App()

Ec2Rds(app, construct_id="blog")

app.synth()
