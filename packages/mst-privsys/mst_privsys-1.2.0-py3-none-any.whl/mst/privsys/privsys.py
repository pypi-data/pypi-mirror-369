"""
privsys

Privsys namespace
"""

# Disable E1102 due to the way ttl_cache overwrites itself to be callable
# pylint: disable=E1102
import re
import time
import ttl_cache
from mst.core import LogAPIUsage, local_env
from mst.simplerpc import SimpleRPCClient

DEFAULT_TTL = 60
PUBLIC_RPC = None

privcache = {}


def simple_public_rpc():
    """setup RPC connection for calls

    Returns:
        SimpleRPCClient: RPC Client
    """
    global PUBLIC_RPC
    LogAPIUsage()

    if PUBLIC_RPC is not None:
        return PUBLIC_RPC

    rpchost = "https://privsys.apps.mst.edu"
    env = local_env()

    if env == "test":
        rpchost = "https://privsys.apps-test.mst.edu"
    elif env == "dev":
        rpchost = "https://privsys.apps-dev.mst.edu"

    PUBLIC_RPC = SimpleRPCClient(base_url=f"{rpchost}/api-bin/latest")
    return PUBLIC_RPC


def check_priv(user, code):
    """checks if "user" has priv grants to "code"

    Args:
        user (str): user to be checked
        code (str): priv code to be checked

    Returns:
        bool: true or false
    """
    LogAPIUsage()

    privs = fetch_privs(user)
    return code in privs


@ttl_cache(DEFAULT_TTL)
def check_priv_regex(user, regex):
    """checks if "user" has any priv grants that match "regex"

    Args:
        user (str): user to be checked
        regex (str): regular expression used in searching in the priv code list that user has access

    Returns:
        bool: true or false
    """
    LogAPIUsage()

    privs = fetch_privs(user)
    privs.extend(fetch_privs("public"))

    for priv in privs:
        if _ := re.search(regex, priv):
            return True

    return False


def fetch_privs(user):
    """grabs all privs "user" has currently granted

    Args:
        user (str): user granted the privs

    Returns:
        tuple: list of privs
    """
    LogAPIUsage()

    # use cached set if "recent"
    cached = privcache.get(user)
    if cached and time.time() - cached["time"] < DEFAULT_TTL:
        return cached["privs"]

    # fetch + cache priv set
    rpc = simple_public_rpc()
    privs = rpc.FetchPrivs(user=user)
    privcache[user] = {"time": time.time(), "privs": privs}
    return privs


@ttl_cache(DEFAULT_TTL)
def fetch_users(code):
    """Returns list of users with priv code

    Args:
        code (str): priv code to be checked

    Returns:
        list: list of users
    """
    LogAPIUsage()

    rpc = simple_public_rpc()
    [result] = rpc.FetchUsers(code=code)
    return result[code]
