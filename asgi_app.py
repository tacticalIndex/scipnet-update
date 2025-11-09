import asyncio
import logging

from utils.api import api  # FastAPI app already defined in utils.api

# Import the bot instance and configured token from erm.py
# Importing erm will construct the Bot object but will not call run()
import scipnet

logger = logging.getLogger(__name__)


async def _start_discord_bot():
    """Start the discord bot as a background task when the ASGI app starts.

    This lets a single uvicorn process serve FastAPI and run the discord client.
    """
    token = getattr(scipnet, "bot_token", None)
    if not token:
        logger.error("No Discord bot token configured (bot_token). Discord bot will not start.")
        return

    # Run the bot in the existing event loop as a background task. bot.start() is a long
    # running coroutine that only returns on disconnect; create_task keeps it running.
    try:
        scipnet.bot._bg_task = asyncio.create_task(scipnet.bot.start(token))
        logger.info("Discord bot background task started.")
    except Exception:
        logger.exception("Failed to start Discord bot background task.")


async def _stop_discord_bot():
    """Attempt a graceful shutdown of the discord bot when ASGI shuts down."""
    try:
        task = getattr(scipnet.bot, "_bg_task", None)
        if task and not task.done():
            task.cancel()
        # Ensure bot connection is closed
        if scipnet.bot.is_closed() is False:
            await scipnet.bot.close()
        logger.info("Discord bot shut down cleanly.")
    except Exception:
        logger.exception("Error while shutting down Discord bot.")


# `on_event` decorators may be flagged in some versions; register handlers explicitly
api.add_event_handler("startup", _start_discord_bot)
api.add_event_handler("shutdown", _stop_discord_bot)


# Expose the FastAPI app as the ASGI application object expected by uvicorn
app = api
