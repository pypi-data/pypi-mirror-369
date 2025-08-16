"""
Project settings management module for Alignerr.

This module contains methods for configuring various project settings
outside of the core project management functionality.
"""

from typing import Any, Dict

import labelbox as lb


def set_ai_critic_settings(
    client: lb.Client, project_id: str, code_enabled: bool, grammar_enabled: bool
) -> Any:
    """
    Set AI critic settings for a project.

    This method is only valid for projects where the media type is:
    - MediaType.Conversational
    - MediaType.LLMPromptResponseCreation

    Args:
        client: GQL client instance
        project_id: The project ID to update
        code_enabled: Whether code critic is enabled
        grammar_enabled: Whether grammar critic is enabled

    Returns:
        Dict containing the mutation result:
        {
            "upsertProjectAiCriticConfig": {
                "projectId": str,
                "codeCriticIsEnabled": bool,
                "grammarCriticIsEnabled": bool
            }
        }
    """
    try:
        project = client.get_project(project_id)
        media_type = project.media_type
    except Exception as e:
        raise ValueError(f"Failed to get project: {e}")

    if media_type not in [
        lb.MediaType.Conversational,
        lb.MediaType.LLMPromptResponseCreation,
    ]:
        raise ValueError(
            "This method is only valid for projects where the media type is: "
            "Conversational or LLMPromptResponseCreation"
        )

    query = """
    mutation UpsertAiCriticConfigAlnrPyApi($input: UpdateProjectAiCriticConfigInput!) {
      upsertProjectAiCriticConfig(input: $input) {
        projectId
        codeCriticIsEnabled
        grammarCriticIsEnabled
      }
    }
    """
    variables = {
        "input": {
            "projectId": project_id,
            "codeCriticIsEnabled": code_enabled,
            "grammarCriticIsEnabled": grammar_enabled,
        }
    }
    return client.execute(query, variables, experimental=True)


def get_ai_critic_settings(client: lb.Client, project_id: str) -> Dict[str, bool]:
    """
    Get AI critic settings for a project.

    Args:
        client: Labelbox client instance
        project_id: The project ID to query

    Returns:
        Dict containing the AI critic configuration:
        {
            "codeCriticIsEnabled": bool,
            "grammarCriticIsEnabled": bool
        }

        Returns empty dict if no AI critic config is found.
    """
    query = """
    query GetAiCriticConfig($projectId: ID!) {
      project(where: { id: $projectId }) {
        aiCriticConfig {
          projectId
          codeCriticIsEnabled
          grammarCriticIsEnabled
        }
      }
    }
    """
    variables = {"projectId": project_id}

    result = client.execute(query, variables, experimental=True)

    # Extract just the aiCriticConfig data, removing GraphQL wrapper
    if (
        result.get("data")
        and result["data"].get("project")
        and result["data"]["project"].get("aiCriticConfig")
    ):
        config = result["data"]["project"]["aiCriticConfig"]
        # Return only the boolean settings, excluding projectId and __typename
        return {
            "codeCriticIsEnabled": config.get("codeCriticIsEnabled", False),
            "grammarCriticIsEnabled": config.get("grammarCriticIsEnabled", False),
        }

    # Return empty dict if no config found
    return {}
