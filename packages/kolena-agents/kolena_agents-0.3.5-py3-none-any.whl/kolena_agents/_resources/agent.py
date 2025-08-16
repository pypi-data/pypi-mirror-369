import kolena_agents.types.agent as agent_types
from kolena_agents._generated.openapi_client import ApiClient  # type: ignore
from kolena_agents._generated.openapi_client.api import ClientApi  # type: ignore


class Agent:
    def __init__(self, client: ApiClient) -> None:
        """Initialize the Agent resource.

        Args:
            client: The configured API client instance.
        """
        self._api = ClientApi(client)

    def get(self, agent_id: int) -> agent_types.Agent:
        """Get details of a specific agent.

        Args:
            agent_id: The ID of the agent
        """
        return self._api.get_agent_api_v1_client_agents_agent_id_get(agent_id=agent_id)

    def list(
        self, page_number: int = 0, page_size: int = 50
    ) -> agent_types.ListAgentsResponse:
        """Get a paginated list of agents.

        Args:
            page_number: Page number for pagination (default: 0)
            page_size: Number of items per page (default: 50, max: 1000)
        """
        return self._api.list_agents_api_v1_client_agents_get(
            page_number=page_number, page_size=page_size
        )
