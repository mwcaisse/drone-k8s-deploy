#!/usr/bin/env python3

import base64
import os
import re
import subprocess


def main():
    """
        what do we need in here?
        
        environment variables to deploy X
        environment variables for the template X

        # need to configure k8s X
        # parse our deployment template, add varaibles X

        # deploy out to k8s X
        # wait for deployment to be ready?
    """

    config = parse_configuration()
    k8s_opts = get_kubernetes_options(config)
    deployment_file = create_deployment_file(config)
    deploy_app(config, k8s_opts, deployment_file)


def parse_configuration():
    print("Parsing configuration")
    if "PLUGIN_TEMPLATE" not in os.environ:
        print("Template setting must be specified.")
        exit(1)

    if "PLUGIN_SERVER" not in os.environ:
        print("Server setting must be specified.")
        exit(1)

    if "PLUGIN_TOKEN" not in os.environ:
        print("Token setting must be specified.")
        exit(1)

    if "PLUGIN_CA" not in os.environ:
        print("CA setting must be specified.")
        exit(1)

    config = {
        "template": os.getenv("PLUGIN_TEMPLATE"),
        "server": os.getenv("PLUGIN_SERVER"),
        "token": os.getenv("PLUGIN_TOKEN"),
        "ca": os.getenv("PLUGIN_CA"),
    }

    if "PLUGIN_NAMESPACE" in os.environ:
        config["namespace"] = os.environ.get("PLUGIN_NAMESPACE")

    # parse the template variables, we assume they have a prefix of PLUGIN_TV
    template_variables = {}

    for name in os.environ:
        if not name.startswith("PLUGIN_TV_"):
            continue
        token_name = name.replace("PLUGIN_TV_", "").lower()
        template_variables[token_name] = os.environ.get(name)

    if template_variables:
        config["template_variables"] = template_variables

    return config


def create_kubernetes_cert_file(config, path="/tmp/k8s_ca.pem"):
    certificate = config.get("ca")

    with open(path, "w") as ca_file:
        ca_file.write(certificate)

    return path


def get_kubernetes_options(config):
    print("Building kubectl options")
    ca_file_path = create_kubernetes_cert_file(config)

    k8s_opts = [
        "--certificate-authority={file}".format(file=ca_file_path),
        "--server={server}".format(server=config.get("server")),
        "--token={token}".format(token=config.get("token"))
    ]

    if "namespace" in config:
        k8s_opts.append("--namespace={namespace}".format(namespace=config.get("namespace")))

    return k8s_opts


def create_deployment_file(config, path="/tmp/deployment.yml"):
    print("Processing deployment file template")
    replace_tokens_in_file(config["template"], config.get("template_variables", {}), path)
    return path


def deploy_app(config, k8s_opts, deployment_file):
    print("Deploying application to K8S...")
    command = "kubectl {opts} apply -f {deployment_file}".format(
        opts=" ".join(k8s_opts),
        deployment_file=deployment_file
    )
    res = subprocess.run(command, shell=True)

    if res.returncode == 0:
        print("Application deployed")
    else:
        print("Application failed to deploy. Exit status {status}".format(status=res.returncode))
        exit(res.returncode)


TOKEN_REGEX = re.compile(r"\[\[.+?\]\]")


def replace_tokens_in_file(in_file, tokens, out_file=None, delete_after=False):
    if not out_file:
        out_file = in_file
    with open(in_file, "r") as file:
        content = file.read()

    content_replaced = replace_tokens_in_string(content, tokens)

    # if the outfile exists, replace it
    if os.path.isfile(out_file):
        os.remove(out_file)

    with open(out_file, "w") as file:
        file.write(content_replaced)

    if delete_after:
        os.remove(in_file)

    return True


def replace_tokens_in_string(string, tokens):
    for match in re.findall(TOKEN_REGEX, string):
        key = remove_delimiters_from_key(match).lower()
        if key not in tokens:
            raise Exception("Unknown key: " + key)

    return TOKEN_REGEX.sub(lambda x: str(tokens[remove_delimiters_from_key(x.group())]), string)


def remove_delimiters_from_key(key):
    return key.replace("[[", "").replace("]]", "")


if __name__ == "__main__":
    main()
