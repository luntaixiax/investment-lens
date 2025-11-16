import asyncio
import os
from functools import lru_cache
from pathlib import Path
import tomli
import hvac

ENV = os.environ.get("ENV", "dev")

def get_vault_resp(mount_point: str, path: str) -> dict:
    """
    Get response from vault
    Args:
        mount_point: The mount point of the vault
        path: The path of the secret
    Returns:
        The response from the vault
    Raises:
        PermissionError: If the vault permission is not correct
    """
    with open((Path(__file__).resolve().parent.parent.parent.parent.parent / "secrets.toml").resolve(), mode="rb") as fp:
        config = tomli.load(fp)
        
    vault_config = config['vault']
    
    client = hvac.Client(
        url = f"{vault_config['endpoint']}:{vault_config['port']}",
        token = vault_config['token']
    )
    if client.is_authenticated():
        response = client.secrets.kv.read_secret_version(
            mount_point=mount_point,
            path=path,
            raise_on_deleted_version=True
        )['data']['data']
        return response
    else:
        raise PermissionError("Vault Permission Error")
    
@lru_cache()
def get_secret() -> dict:
    """
    Get all secrets from vault
    """
    VAULT_MOUNT_POINT = "investlens"
    VAULT_MOUNT_PATH = {
        'database' : f"{ENV}/database",
        'auth': f"{ENV}/auth",
        'mailbox': f"{ENV}/mailbox",
    }
    
    database = get_vault_resp(
        mount_point = VAULT_MOUNT_POINT,
        path = VAULT_MOUNT_PATH['database'],
    )
    auth = get_vault_resp(
        mount_point = VAULT_MOUNT_POINT,
        path = VAULT_MOUNT_PATH['auth'],
    )
    mailbox = get_vault_resp(
        mount_point = VAULT_MOUNT_POINT,
        path = VAULT_MOUNT_PATH['mailbox'],
    )
    
    return {
        'database' : database,
        'auth': auth,
        'mailbox': mailbox
    }
    
    
async def get_async_db_url(db: str) -> str:
    
    config = (await asyncio.to_thread(get_secret))['database']
    db_url = f"{config['async_driver']}://{config['username']}:{config['password']}@{config['hostname']}:{config['port']}/{db}"
    return db_url

def get_sync_db_url(db: str) -> str:
    config = get_secret()['database']
    db_url = f"{config['sync_driver']}://{config['username']}:{config['password']}@{config['hostname']}:{config['port']}/{db}"
    return db_url