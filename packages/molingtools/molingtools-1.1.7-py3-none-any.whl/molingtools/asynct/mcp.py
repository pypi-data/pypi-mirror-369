from pydantic import BaseModel
import json
import warnings
try:
    from mcp import ClientSession, StdioServerParameters
    from openai import AsyncOpenAI
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install mcp openai')
from typing import AsyncIterator, Literal
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client 
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message_function_tool_call import ChatCompletionMessageFunctionToolCall
from openai.types.chat.chat_completion_message_custom_tool_call import ChatCompletionMessageCustomToolCall


class Messager(BaseModel):
    role: Literal['system', 'assistant', 'user', 'tool']
    content: str
    name: str|None = None
    args: dict|list|None = None
    tool_call_id: str|None = None
    tool_calls: list[ChatCompletionMessageFunctionToolCall|ChatCompletionMessageCustomToolCall]|None = None
    
    @property
    def is_tool_messager(self)->bool:
        return self.role == 'tool' or self.tool_calls
    
class MCPClient:
    def __init__(self, base_url, model, api_key='EMPTY'):
        self.exit_stack = AsyncExitStack()
        self.model = model
        self.aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.server_session:dict[str, ClientSession] = {}  # 存储多个服务端会话
        self.available_tools = []
        self.tool_session = {}
        
    async def _connect_to_server(self, server_name, session:ClientSession, debug_list_tools:bool=False):
        await session.initialize()
        self.server_session[server_name]=session
        # 更新工具映射
        response = await session.list_tools()
        for tool in response.tools:
            if debug_list_tools:
                print({"name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema})
            # 构建统一的工具列表
            self.available_tools.append({
                                    "type": "function",
                                    "function": {
                                        "name": tool.name,
                                        "description": tool.description,
                                        "input_schema": tool.inputSchema
                                        }
                                    })
            self.tool_session[tool.name] = session
        print(f"已连接到 MCP 服务器 {server_name}")
        
    async def connect_to_stdio_server(self, server_name:str, command:str, *args: str, env:dict=None, debug_list_tools=False):
        server_params = StdioServerParameters(command=command, args=args, env=env)
        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self._connect_to_server(server_name, session, debug_list_tools=debug_list_tools)

    async def connect_to_sse_server(self, server_name:str, url:str, debug_list_tools=False):
        read_stream, write_stream = await self.exit_stack.enter_async_context(sse_client(url))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self._connect_to_server(server_name, session, debug_list_tools=debug_list_tools)
    
    async def connect_to_config(self, config_or_path:dict|str, debug_list_tools=False):
        if isinstance(config_or_path, str):
            with open(config_or_path, encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = config_or_path
        for server_name, server_config in config['mcpServers'].items():
            if server_config.get("command"):
                await self.connect_to_stdio_server(server_name, server_config["command"], *server_config.get("args",[]), 
                                                   env=server_config.get("env"), debug_list_tools=debug_list_tools)
            elif server_config.get("url"):
                await self.connect_to_sse_server(server_name, server_config["url"], debug_list_tools=debug_list_tools)
            else:
                warnings.warn(f"未指定command或url, 无法连接到 MCP 服务器 {server_name}")
        
    async def chat(self, messages:list[Messager|dict], max_tool_num=3, **kwargs)->AsyncIterator[Messager]:
        """调用大模型处理用户查询，并根据返回的 tools 列表调用对应工具。
        支持多次工具调用，直到所有工具调用完成。
        流式输出
        Args:
            query (str): 查询
            max_num (int, optional): 最大工具调用次数. Defaults to 3.
        Yields:
            str: 结果词语
        """
        kwargs.pop('stream', None)
        messages = [m.model_dump(exclude_none=True) for m in messages] if messages and isinstance(messages[0], Messager) else messages.copy()
        # 循环处理工具调用
        for _ in range(max_tool_num):
            # 使用工具的请求无法进行流式输出
            response:ChatCompletion = await self.aclient.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.available_tools,
                **kwargs,
                stream=False
            )
            content = response.choices[0].message.content
            message = Messager(role="assistant", content=content, tool_calls=response.choices[0].message.tool_calls)
            yield message
            messages.append(message.model_dump(exclude_none=True))
            # 处理返回的内容
            if message.tool_calls:
                # 执行工具调用
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    # 根据工具名称找到对应的服务端
                    session:ClientSession = self.tool_session[tool_name]
                    result = await session.call_tool(tool_name, tool_args)
                    # 将工具调用的结果添加到 messages 中
                    tmessage = Messager(role="tool", content=result.content[0].text, name=tool_name, args=tool_args, tool_call_id=tool_call.id)
                    yield tmessage
                    messages.append(tmessage.model_dump(exclude_none=True))
            else:
                break
        if not content: warnings.warn('已超出最大工具调用次数...')
        
    async def close(self):
        await self.exit_stack.aclose()
        self.server_session.clear()
        

# mcper = MCPClient(AI_URL, AI_MODEL, AI_KEY)

# async def main():
#     await mcper.connect_to_stdio_server('local','bash','-c','source ./.venv/bin/activate && python test4.py')
#     async for result in mcper.chat([Messager(role='user',content='你好, 今天星期几')]):
#         print(result)
#     await mcper.close()
    
# asyncio.run(main())