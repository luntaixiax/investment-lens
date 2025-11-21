from functools import wraps
from typing import Callable, Any, Type
from pydantic import BaseModel


def deserialize_cached_model(model_class: Type[BaseModel]):
    """Decorator to deserialize cached Pydantic models from dict.
    
    When using @cached decorator with Pydantic models, the cache may return
    a dict instead of the model instance. This decorator automatically
    deserializes dict results back to the appropriate Pydantic model.
    
    Usage:
        @deserialize_cached_model(Account)
        @cached(cache=cache, ...)
        async def get_account(self, ...) -> Account:
            ...
    
    For lists:
        @deserialize_cached_model(Account)
        @cached(cache=cache, ...)
        async def list_accounts(self, ...) -> list[Account]:
            ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            
            # If result is already the correct type, return it
            if not isinstance(result, (dict, list)):
                return result
            
            # Handle list of models
            if isinstance(result, list):
                return [
                    model_class.model_validate(item) if isinstance(item, dict) else item
                    for item in result
                ]
            
            # Handle single model
            if isinstance(result, dict):
                return model_class.model_validate(result)
            
            return result
        
        return wrapper
    return decorator

