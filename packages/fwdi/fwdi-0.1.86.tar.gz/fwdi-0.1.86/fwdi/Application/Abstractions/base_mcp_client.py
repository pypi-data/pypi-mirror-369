from abc import ABC, abstractmethod
from fastmcp.resources import Resource
from fastmcp.tools.tool import Tool
from fastmcp.prompts.prompt import Prompt
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents

class BaseMCPClient(ABC):
    def __init__(self):
        super().__init__()
        self.tools:list[Tool] = []
        self.prompts:list[Prompt] = []
        self.resources:list[Resource] = []

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
