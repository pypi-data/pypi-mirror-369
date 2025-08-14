from abc import ABC, abstractmethod
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents

class BaseMCPClient(ABC):

    @classmethod
    async def create(cls, host:str='127.0.0.1', port:int=5000, path:str='/mcp'):
        ...

    @abstractmethod
    async def check_avaible(self):
        ...
    
    @abstractmethod
    async def load_env(self)->bool:
        ...

    @abstractmethod
    async def call_tool(self, name_fn:str, param:dict)->CallToolResult:
        ...

    @abstractmethod
    async def read_resource(self, uri:str)->list[TextResourceContents | BlobResourceContents]:
        ...

    @abstractmethod
    async def get_prompt(self, name:str, param:dict)->GetPromptResult:
        ...
