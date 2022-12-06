from pprint import pprint as pp
import pytest
from boto3.session import Session


def cloutsearch_client():
    session = Session(profile_name="study")
    return session.client(service_name="cloudsearch", region_name="ap-northeast-1")

def test_cloudsearch_created_domain():
    session = Session()
    client = cloutsearch_client()
    status = False
    if "senju-sec-qa" in  client.list_domain_names()["DomainNames"].keys():
        status = True
    assert status

def ssm_client():
    session = Session(profile_name="study")
    return session.client(service_name="ssm", region_name="ap-northeast-1")

def test_cloudsearch_ssm():
    session = Session()
    client = ssm_client()
    status = False
    names=["/osanai/1", "/osanai/2"]
    pp(client.get_parameters(Names=names)["Parameters"])
    remote_names = []
    for row in client.get_parameters(Names=names)["Parameters"]:
        remote_names.append(row["Name"])
    assert (set(names) == set(remote_names))