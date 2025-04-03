"""
Account model for GabeGardener.

This module defines the Account class which represents a Steam account.
"""
from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, Field

class Account(BaseModel):
    """
    Steam account model.
    
    This class represents a Steam account with all its configuration options.
    """
    username: str
    password: str
    shared_secret: str = ""
    visible: bool = True
    games: List[Union[str, int]] = Field(default_factory=list)
    auto_reply: Optional[str] = "I am currently AFK. This is an automated message."
    receive_messages: bool = True
    save_messages: bool = True
    game_rotation: bool = False
    rotation_interval: Optional[int] = None
    
    # Runtime properties (not stored in config)
    session: Any = None
    status: str = "offline"
    current_games: List[int] = Field(default_factory=list)
    login_key: Optional[str] = None
    last_rotation: int = 0
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the account to a dictionary for configuration storage.
        
        Returns:
            Dict[str, Any]: Account configuration dictionary
        """
        return {
            "username": self.username,
            "password": self.password,
            "shared_secret": self.shared_secret,
            "visible": self.visible,
            "games": self.games,
            "auto_reply": self.auto_reply,
            "receive_messages": self.receive_messages,
            "save_messages": self.save_messages,
            "game_rotation": self.game_rotation,
            "rotation_interval": self.rotation_interval
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """
        Create an Account instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Account configuration dictionary
            
        Returns:
            Account: New Account instance
        """
        return cls(**data)
