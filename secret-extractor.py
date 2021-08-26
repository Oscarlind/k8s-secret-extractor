#!/usr/bin/python3

# Simple script to extract secret values in K8s/OCP

# Imports
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import urllib3
import inquirer
import base64
#
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def list_secrets(v1):
    namespace = (input("Which namespace do you want to extract secrets from?\n"))
    secret_list = []
    secrets = v1.list_namespaced_secret(namespace, watch=False).items
    if secrets == []:
        print("Namespace not found or no secrets in the namespace")
        exit()
    for secret in secrets:
        secret_list.append(secret)
    print("\nNamespace - " '\033[1m', namespace, '\033[0m' "\n")
    return secret_list


def choose_secret(v1):
    secret_list = list_secrets(v1)
    secret_names = []
    for secret in secret_list:
        secret_names.append(secret.metadata.name)
        namespace = secret.metadata.namespace
    questions = [
        inquirer.List('secret',
                      message="Choose your secret",
                      choices=secret_names
                    ),
    ]
    answers = inquirer.prompt(questions)
    secret = v1.read_namespaced_secret(answers['secret'], namespace)
    return secret


def return_secret_data(v1):
    secret = choose_secret(v1)
    data_keys = []
    for key in secret.data.keys():
        data_keys.append(key)
    questions = [
        inquirer.List('data',
                      message='Choose data entry to decode',
                      choices=data_keys
                      )
    ]
    answers = inquirer.prompt(questions)
    decoded_value = base64.b64decode(secret.data[answers['data']])
    print(f"The key:" '\033[1m', answers['data'], '\033[0m' "has the following value:\n")
    print(decoded_value.decode('utf-8'))
 
 

def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    v1=client.CoreV1Api()
    return_secret_data(v1)




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("User interuption")
        exit()
    except ApiException as e:
        if "Forbidden" or "Unauthorized" in e:
            print("Forbidden, please log in to the cluster and ensure privileged permissions")
            exit()