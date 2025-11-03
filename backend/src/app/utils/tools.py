import re
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def id_generator(prefix: str, length: int = 8, existing_list: list[str] | None = None, 
                 only_alpha_numeric: bool = False) -> str:
    """Generate a unique ID with a prefix and optional length.
    
    Args:
        prefix (str): The prefix for the ID.
        length (int): The length of the ID.
        existing_list (list[str]): A list of existing IDs to avoid duplicates.
        only_alpha_numeric (bool): Whether to only allow alpha-numeric characters.
        
    Returns:
        str: A unique ID with the specified prefix and length.
    """
    new_id = prefix + str(uuid.uuid4())[:length]
    if existing_list:
        if new_id in existing_list:
            new_id = id_generator(prefix, length, existing_list, only_alpha_numeric)
    if only_alpha_numeric:
        new_id = re.sub(r'[^a-zA-Z0-9]', '', new_id)
    return new_id