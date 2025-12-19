# All imports at the top
import os

from vanna import Agent
from vanna import AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import RequestContext
from vanna.core.user import User
from vanna.core.user import UserResolver
from vanna.integrations.anthropic import AnthropicLlmService
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.mysql import MySQLRunner  # Changed from SqliteRunner
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.tools import RunSqlTool
from vanna.tools import VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool
from vanna.tools.agent_memory import SaveTextMemoryTool
from vanna.tools.agent_memory import SearchSavedCorrectToolUsesTool

from system_prompt import \
    CustomSystemPromptBuilder  # Import your custom system prompt

# Configure your LLM
llm = AnthropicLlmService(model="claude-sonnet-4-5", api_key=os.getenv("ANTHROPIC_API_KEY"))

# Configure your MySQL database connection
# Using environment variables from .env file
db_config = {
    "host": os.getenv("MYSQL_HOST", "db"),  # "db" is the service name in docker-compose
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "vanna_user"),
    "password": os.getenv("MYSQL_PASSWORD", "vanna_password"),
    "database": os.getenv("MYSQL_DATABASE", "my_production_db"),
}

# Configure your database tool with MySQL
db_tool = RunSqlTool(
    sql_runner=MySQLRunner(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
    )
)

# Configure your agent memory
agent_memory = DemoAgentMemory(max_items=1000)


# Configure user authentication
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie("vanna_email") or "guest@example.com"
        group = "admin" if user_email == "admin@example.com" else "user"
        return User(id=user_email, email=user_email, group_memberships=[group])


user_resolver = SimpleUserResolver()

# Create your agent
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=["admin", "user"])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"])
tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin", "user"])
tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "user"])
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    system_prompt_builder=CustomSystemPromptBuilder(),
    config=AgentConfig(max_tool_iterations=20),
)

# Run the server
server = VannaFastAPIServer(agent)

if __name__ == "__main__":
    # Access at http://localhost:8000
    server.run()
