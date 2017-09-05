from __future__ import absolute_import
import hashlib
import logging
import os
import re
from django.conf import settings
from ..core.HotDockerExecutor import HotDockerExecutor
from ..core.DjangoCacheStreamer import DjangoCacheStreamer

LOG = logging.getLogger("estate")

PLAN = """#!/bin/bash +ex
terraform init {TERRAFORM_EXTRA_ARGS} {TERRAFORM_INIT_EXTRA_ARGS}
terraform plan {TERRAFORM_EXTRA_ARGS} {TERRAFORM_PLAN_EXTRA_ARGS}
"""

APPLY = """#!/bin/bash +ex
terraform apply {TERRAFORM_EXTRA_ARGS} {TERRAFORM_APPLY_EXTRA_ARGS} plan
"""

HAS_EXT = re.compile(".*\.([a-zA-Z]+)")


class TerraformStreamer(DjangoCacheStreamer):
    def __init__(self, action, slug, *args, **kwargs):
        super(TerraformStreamer, self).__init__("terraform", action + "_" + slug, *args, **kwargs)

    def get_plan_key(self, plan_hash):
        return self.namespace_slug + "_" + plan_hash

    def get_plan(self, plan_hash):
        return self.cache.get(self.get_plan_key(plan_hash))

    def save_plan(self, plan_hash, plan_data):
        self.state["output"] += ["\nPlan Hash: " + plan_hash]
        self.state["plan_hash"] = plan_hash
        self.set(self.state, None)
        self.cache.set(self.get_plan_key(plan_hash), plan_data, None)


class Terraform(HotDockerExecutor):

    def __init__(self, action, namespace, plan_hash=None, state_obj=None):
        self.action = action
        self.namespace = namespace
        self.plan_hash = plan_hash
        self.state_obj = state_obj
        config = {
            "docker_image": settings.TERRAFORM_DOCKER_IMAGE,
            "name": self.namespace.slug,
            "streamer": TerraformStreamer(action, self.namespace.slug)
        }
        if action == "plan":
            config["command"] = PLAN
        else:
            config["command"] = APPLY
        config["command"] = config["command"].format(
            TERRAFORM_EXTRA_ARGS=settings.TERRAFORM_EXTRA_ARGS,
            TERRAFORM_INIT_EXTRA_ARGS=settings.TERRAFORM_INIT_EXTRA_ARGS,
            TERRAFORM_PLAN_EXTRA_ARGS=settings.TERRAFORM_PLAN_EXTRA_ARGS,
            TERRAFORM_APPLY_EXTRA_ARGS=settings.TERRAFORM_APPLY_EXTRA_ARGS,
        )
        config["command"] = config["command"].format(NAMESPACE=self.namespace.slug)
        super(Terraform, self).__init__(config=config)

    def run(self, *args, **kwargs):
        self.streamer.clear_cache()
        super(Terraform, self).run(*args, **kwargs)

    def write_files(self):
        LOG.info("[Terraform] Preparing Namespace '{0}' for action '{1}'".format(self.namespace.title, self.action))
        if self.action == "plan":
            if self.state_obj:
                LOG.info("[Terraform] Writing terraform statefile")
                path = os.path.join(self.workdir, "terraform.tfstate")
                with open(path, "wb") as f:
                    f.write(self.state_obj.content)
            for item in self.namespace.terraform_files:
                path = os.path.join(self.workdir, str(item.pk) + "_" + item.slug + ".tf")
                has_ext = HAS_EXT.search(item.title)
                if has_ext:
                    path = os.path.join(self.workdir, item.title)
                LOG.info("[Terraform] Writing file: {0}".format(path))
                with open(path, "wb") as f:
                    f.write(item.content)
        if self.action == "apply":
            if self.plan_hash is None:
                raise Exception("Unable to perform action 'apply' no plan was found!")
            if self.state_obj:
                LOG.info("[Terraform] Writing terraform statefile")
                path = os.path.join(self.workdir, "terraform.tfstate")
                with open(path, "wb") as f:
                    f.write(self.state_obj.content)
            path = os.path.join(self.workdir, "plan.tar.gz")
            plan_data = self.streamer.get_plan(self.plan_hash)
            if plan_data is None:
                raise Exception("Unable to find plan data!")
            with open(path, "wb") as f:
                f.write(plan_data)
            exit_code, _ = self.execute_command(["tar", "-xzvf", path, "-C", self.workdir])
            if exit_code != 0:
                raise Exception("Unable to unpack plan file!")

    def finish(self):
        if self.action == "plan" and self.exit_code == 2:
            path = os.path.join(self.workdir, "plan.tar.gz")
            exit_code, output = self.execute_command(["tar", "-czvf", path, "./plan"])
            if exit_code != 0:
                raise Exception("Unable to save plan file!\n" + output)
            with open(path, "rb") as f:
                plan_data = f.read()
            plan_hash = hashlib.md5(plan_data).hexdigest()
            self.streamer.save_plan(plan_hash, plan_data)
        if self.action == "apply" and self.exit_code == 0:
            path = os.path.join(self.workdir, "terraform.tfstate")
            exit_code, output = self.execute_command(["cat", path])
            if exit_code != 0:
                raise Exception("Failed to save the terraform state!\n" + output)
            LOG.info("[Terraform] Saving Terraform State - \n" + output)
            self.state_obj.content = output
            self.state_obj.save()

    def get_stream(self):
        return self.streamer.get()
