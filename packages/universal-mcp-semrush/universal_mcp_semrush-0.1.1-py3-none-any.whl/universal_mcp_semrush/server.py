
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_semrush.app import SemrushApp

env_store = EnvironmentStore()
# "name" used in AgentRIntegration should match the actual name from the backend
integration_instance = AgentRIntegration(name="semrush", store=env_store)
app_instance = SemrushApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()


