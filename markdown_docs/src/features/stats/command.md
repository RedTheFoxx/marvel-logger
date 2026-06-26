## FunctionDef register_stats_command(tree, tracker)
**register_stats_command**: The function of register_stats_command is to register a Discord slash command that retrieves and displays Marvel Rivals player statistics from Tracker.gg.
**parameters**: The parameters of this Function.
· tree: An instance of app_commands.CommandTree used to bind the new slash command to the Discord bot's application routing system.
· tracker: An instance of TrackerScraper responsible for asynchronously fetching, caching, and parsing player profile data from Tracker.gg.
**Code Description**: This function defines and registers a /stats slash command within the provided command tree. It accepts a username string parameter and orchestrates the complete lifecycle of a statistics request. Upon invocation, it logs the request, validates the input format via validate_tracker_username, and immediately responds with an ephemeral error embed if validation fails. For valid inputs, it defers the interaction response to accommodate the latency of external API calls. It then delegates data acquisition to tracker.fetch_profile(username), which handles network requests, rate limiting, and cache management. The function constructs a statistics embed using build_stats_embed and conditionally generates a rating chart image in a background thread pool via asyncio.to_thread if historical rating data is available. The final response is dispatched as a followup message containing the embed and optional chart file. Comprehensive exception handling captures ProfileNotFoundError, TrackerRateLimitError, TrackerScraperError, and generic exceptions, routing each to appropriate ephemeral error responses with contextual logging. This function is invoked during bot initialization within MarvelLoggerBot.setup_hook in app.py, where it binds the command to the application tree prior to global or guild synchronization.
**Note**: The function itself returns None, as its sole purpose is command registration. It depends on external helper functions (validate_tracker_username, build_stats_embed, build_error_embed, render_rating_chart) that must be imported in the same module. Interaction deferral is strictly required to prevent Discord's 3-second timeout during asynchronous scraping operations. All error responses are ephemeral and visible only to the command requester. The rating chart generation executes in a synchronous thread pool to avoid blocking the main asyncio event loop. The tracker instance must have its underlying browser session explicitly started before this function is called, as fetch_profile relies on an active AsyncStealthySession.
**Output Example**: Since the function returns None, the following represents the expected Discord response structure generated when the registered /stats command executes successfully:
{
  "embed": {
    "title": "Marvel Rivals Stats",
    "description": "Season 12 - Diamond III",
    "fields": [
      {"name": "Rating Points", "value": "4500"},
      {"name": "Rating Chart", "value": "[View Chart](attachment://rating_chart.png)"}
    ],
    "color": 16776960
  },
  "files": ["rating_chart.png"]
}
### FunctionDef stats(interaction, username)
**stats**: The function of stats is to handle the `/stats` slash command by validating user input, fetching external player profile data, and generating a comprehensive statistical overview embed with an optional rating progression chart for Discord display.

**parameters**: The parameters of this Function.
· interaction: discord.Interaction - The Discord interaction object representing the slash command invocation, used to manage response timing, send ephemeral messages, and access user metadata.
· username: str - The target player's username as provided by the command invoker, which will be stripped of leading and trailing whitespace before validation and profile lookup.

**Code Description**: This async function serves as the primary command handler for retrieving and displaying competitive gaming statistics. It begins by capturing execution timing and logging the request details using structured formatting. The raw username input is sanitized via whitespace stripping and passed to a centralized validation utility that enforces character whitelist rules and length constraints; any validation failure immediately halts execution and returns an ephemeral error embed to the user. Upon successful validation, the function defers the Discord interaction response to prevent timeout penalties while initiating background processing. It then attempts to retrieve the player's aggregated profile data through an external tracker client method. Once the profile is obtained, a structured Discord embed is constructed containing rank information, combat metrics, win percentages, role/hero statistics, and seasonal peaks. If the profile contains chronological rating progression data, the function asynchronously delegates chart rendering to a background thread using asyncio.to_thread, generates a PNG image buffer, and wraps it in a Discord file attachment. The final response is dispatched via followup message, carrying both the statistical embed and the optional chart image. Throughout execution, the handler implements granular exception management: it specifically catches profile-not-found conditions, API rate-limiting delays, scraper/network failures, and unexpected runtime errors, each triggering appropriate warning logs and user-facing ephemeral error messages. The function relies heavily on modular utilities for input sanitization, embed construction, chart generation, and standardized error formatting, ensuring separation of concerns between command routing, data fetching, and UI presentation.

**Note**: Points to note about the use of the code
- The interaction must be deferred immediately after validation to comply with Discord's 3-second response timeout requirement for slash commands.
- Chart rendering is offloaded to a background thread via asyncio.to_thread to prevent blocking the bot's event loop during CPU-intensive matplotlib operations.
- Validation errors, rate limits, and missing profiles are handled as ephemeral messages visible only to the command invoker, while scraper failures may expose broader error details depending on the underlying exception.
- The function assumes the tracker client instance is properly initialized and accessible in the surrounding scope; it does not instantiate or manage the client lifecycle itself.
- Logging uses structured formatting with elapsed time tracking for performance monitoring, which should be preserved for operational diagnostics.
- The rating chart attachment uses a fixed filename and relies on Discord's attachment protocol; callers must ensure the file buffer is properly managed to avoid resource leaks.

**Output Example**: Mock up a possible appearance of the code's return value.
A Discord followup message containing a rich embed titled "PlayerName — Marvel Rivals Overview" with sections displaying KDA ratio, win percentage, current rank (e.g., Grandmaster · 4850 RS), combat/impact statistics, top roles, and top heroes. Below the embed fields, an inline image displays a line chart tracking rating progression over time, annotated with total matches played, net rating change, and current tier background bands. The embed footer indicates the current season and tracker attribution, while the timestamp reflects the UTC generation time. In failure scenarios, the output is replaced by a red-bordered ephemeral embed displaying messages such as "Profile not found on Tracker.gg", "Rate limit reached. Retry in X min Y s.", or "Unexpected scraper error occurred."
***
