import asyncio

import click
from websockets.exceptions import ConnectionClosed

from exponent.commands.settings import use_settings
from exponent.commands.shell_commands import LiveView
from exponent.commands.theme import get_theme
from exponent.commands.types import exponent_cli_group
from exponent.core.config import Settings
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.subscriptions import INDENT_CHAT_EVENT_STREAM_SUBSCRIPTION


@exponent_cli_group(hidden=True)
def listen_cli() -> None:
    pass


@listen_cli.command()
@click.option("--chat-id", help="ID of the chat to listen to", required=True)
@click.option(
    "--known-event-uuids",
    help="Comma-separated list of known event UUIDs to skip",
    default="",
)
@use_settings
def listen(settings: Settings, chat_id: str, known_event_uuids: str) -> None:
    """Listen to events from an indent chat session."""
    api_key = settings.api_key
    if not api_key:
        raise click.UsageError("API key is not set")

    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    gql_client = GraphQLClient(api_key, base_api_url, base_ws_url)

    # Parse known event UUIDs
    known_uuids = []
    if known_event_uuids:
        known_uuids = [
            uuid.strip() for uuid in known_event_uuids.split(",") if uuid.strip()
        ]

    # Set up the live view with theme
    theme = get_theme(settings.options.use_default_colors)
    live_view = LiveView(theme, render_user_messages=True)

    asyncio.run(_listen(gql_client, chat_id, known_uuids, live_view))


async def _listen(
    gql_client: GraphQLClient,
    chat_id: str,
    known_event_uuids: list[str],
    live_view: LiveView,
) -> None:
    """Internal listen function that handles the WebSocket subscription."""
    while True:
        try:
            variables = {
                "chatUuid": chat_id,
                "lastKnownFullEventUuid": known_event_uuids[-1]
                if known_event_uuids
                else None,
            }

            async for response in gql_client.subscribe(
                INDENT_CHAT_EVENT_STREAM_SUBSCRIPTION, variables
            ):
                event = response["indentChatEventStream"]
                kind = event["__typename"]

                # Handle different event types
                if kind in ["UserEvent", "AssistantEvent", "SystemEvent"]:
                    live_view.render_event(kind, event)
                elif kind == "Error":
                    print(f"Error: {event.get('message', 'Unknown error')}")
                elif kind == "UnauthenticatedError":
                    print(
                        f"Authentication error: {event.get('message', 'Unauthenticated')}"
                    )
                    break
                else:
                    print(f"Unknown event type: {kind}")

        except ConnectionClosed:
            print("WebSocket disconnected, reconnecting...")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)
