import asyncio
import os
import sys

py313 = sys.version_info >= (3, 13)
py312 = sys.version_info >= (3, 12)
py311 = sys.version_info >= (3, 11)
py310 = sys.version_info >= (3, 10)
py39 = sys.version_info >= (3, 9)


def default_server_port() -> int:
    policy = asyncio.get_event_loop_policy()
    base_port = 3130 if py313 else 3120 if py312 else 3110 if py311 else 3100 if py310 else 3900
    if os.name == 'nt':
        if isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            return base_port + 10
        if isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
            return base_port + 11
        return base_port + 12
    if isinstance(policy, asyncio.DefaultEventLoopPolicy):
        return base_port
    return base_port + 1


def default_client_port() -> int:
    policy = asyncio.get_event_loop_policy()
    base_port = 31100 if py311 else 31000 if py310 else 39000 if py39 else 38000
    if os.name == 'nt':
        if isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            return base_port + 100
        if isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
            return base_port + 110
        return base_port + 120
    if isinstance(policy, asyncio.DefaultEventLoopPolicy):
        return base_port
    else:
        return base_port + 10
