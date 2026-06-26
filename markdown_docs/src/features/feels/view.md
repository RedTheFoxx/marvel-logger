## FunctionDef _build_raw_snapshot(bundle, entry)
**_build_raw_snapshot**: The function of _build_raw_snapshot is to generate a JSON-formatted string containing either raw API match details or structured match list entry data, depending on data availability.
**parameters**: The parameters of this Function.
· bundle: MatchBundle - A unified data container that aggregates season context and preloaded match information, specifically providing access to raw detail payloads via the details_raw attribute.
· entry: MatchListEntry - A structured summary of a single match containing metadata, player performance statistics, and contextual information for display and processing.
**Code Description**: This function constructs a serialized snapshot of match data by evaluating the availability of preloaded raw API responses within the provided bundle. It first attempts to retrieve the original JSON payload for the specific match using the entry's match_id from bundle.details_raw. If this raw data exists, it packages it into a dictionary with the source identifier "tracker_match_detail". If the raw detail is unavailable, it falls back to converting the structured MatchListEntry object into a standard Python dictionary using dataclasses.asdict(), labeling the source as "match_list_entry". The resulting payload dictionary is then serialized into a JSON string using json.dumps with ensure_ascii=False to preserve Unicode characters and default=str to handle non-serializable types gracefully. Within the project architecture, this function is exclusively invoked by build_feels_record to populate the raw_snapshot_json field of MatchFeelsRecord objects. This integration ensures that when users submit match ratings or feedback, the system captures a deterministic snapshot of the underlying match data at that exact moment, preserving either the original API response or the parsed summary for audit, debugging, or downstream analytics purposes.
**Note**: The function relies on bundle.details_raw being properly initialized; consumers should ensure the tracker scraping phase has completed before calling this method to avoid unexpected fallback behavior. The use of default=str in json.dumps prevents serialization errors when nested objects contain datetime instances or custom types that lack native JSON support. Since the payload source field explicitly indicates which data layer was used, downstream parsers should validate the source key before interpreting the data structure. Direct modification of the returned JSON string is discouraged as it represents a point-in-time snapshot.
**Output Example**: 
{
  "source": "tracker_match_detail",
  "data": {
    "match_id": "1234567890",
    "players": [...],
    "scoreboard": {...}
  }
}
## FunctionDef build_feels_record(bundle, entry)
**build_feels_record**: The function of build_feels_record is to aggregate contextual match metadata, user-provided rating inputs, and raw snapshot data into a structured MatchFeelsRecord instance for subsequent database persistence.
**parameters**: The parameters of this Function.
· bundle: MatchBundle - A unified data container providing season context, the tracked username, and preloaded raw match payloads.
· entry: MatchListEntry - A structured summary of a specific match containing performance statistics, metadata, and rank information.
· discord_user_id: int - The unique identifier of the Discord user submitting the rating (keyword-only parameter).
· rating: int - The discrete numerical score assigned by the user to the match (keyword-only parameter).
**Code Description**: This function operates as a data aggregation and mapping layer within the feels feature module. It extracts relevant fields from the provided MatchBundle and MatchListEntry objects, safely handling optional rank attributes by applying conditional checks before assignment. The function delegates JSON serialization of the underlying match context to _build_raw_snapshot, ensuring a deterministic point-in-time snapshot is captured alongside the subjective rating. Once all attributes are resolved, it instantiates and returns a MatchFeelsRecord object. Functionally, this record serves as the bridge between the interactive UI layer and the persistence layer. It is exclusively invoked by FeelsRatingView._on_rating_select following a successful Discord interaction callback. Upon receiving the constructed record, the caller immediately passes it to the database store for insertion, while also using the surrounding context to render updated visualizations and confirmation embeds. The separation of concerns ensures that match data extraction, user input validation, and snapshot generation remain decoupled from the actual database operations.
**Note**: The function relies on entry.rank being potentially None; consumers must ensure rank attributes are accessed conditionally as demonstrated. The keyword-only syntax for discord_user_id and rating enforces explicit argument passing during invocation, reducing positional parameter errors in Discord interaction handlers. Since raw_snapshot_json depends on _build_raw_snapshot, the underlying bundle.details_raw dictionary must be properly initialized prior to calling this function to avoid fallback behavior that may alter snapshot structure. All statistical fields extracted from entry are preserved as strings per their source typing; downstream database operations should handle type casting or validation if numeric comparisons are required. The rating field strictly expects an integer value, aligning with discrete scoring systems rather than floating-point averages.
**Output Example**: 
MatchFeelsRecord(
    discord_user_id=123456789012345678,
    tracker_username="ExamplePlayer",
    match_id="9876543210",
    season_id=42,
    rating=8,
    played_at=datetime.datetime(2023, 10, 15, 18, 30, 0),
    hero_name="Soldier: 76",
    map_name="Dorado",
    game_mode="Competitive",
    outcome="Victory",
    score="4-2",
    kills="24",
    deaths="12",
    assists="8",
    kda_ratio="2.67",
    rs="3500",
    rs_delta="+25",
    raw_snapshot_json='{"source": "tracker_match_detail", "data": {...}}',
    rated_at=None
)
## ClassDef FeelsRatingView
**FeelsRatingView**: The function of FeelsRatingView is to provide an interactive Discord UI component that allows users to select an unrated match from a list and assign a numerical rating between 1 and 10 to it.

**attributes**:
· bundle: MatchBundle - Contains the fetched match data, season identifier, and username for context.
· unrated_entries: list[MatchListEntry] - List of matches retrieved from the tracker that have not yet been rated by the user.
· feels_store: FeelsStore - Database interface used to persist ratings, check for duplicates, and retrieve season records.
· author_id: int - Discord user ID of the command initiator, used to enforce access control.
· _entries_by_id: dict[int, MatchListEntry] - Internal dictionary mapping match IDs to their corresponding entry objects for O(1) lookup during selection.
· _selected_entry: MatchListEntry | None - Tracks the currently selected match during the rating workflow before submission.

**Code Description**:
FeelsRatingView extends discord.ui.View and implements a two-step interactive workflow for collecting match ratings. During initialization, it constructs a dropdown menu populated with all unrated matches from the provided bundle. Each dropdown option displays a truncated label (match rank, win/loss outcome, score, map name) and a description (hero name, KDA ratio, game mode), with strings capped at 100 characters to comply with Discord API limits. The view enforces strict access control via interaction_check, ensuring only the original command author can interact with it; unauthorized attempts trigger an ephemeral error message. When a match is selected through _on_match_select, the component updates its internal state, clears the current dropdown, and injects a new rating dropdown containing options from 1 to 10. It simultaneously edits the original message embed to display detailed information about the selected match. Upon selecting a rating in _on_rating_select, the view defers the response, constructs a rating record, and persists it to the FeelsStore. Duplicate rating attempts are handled gracefully by catching sqlite3.IntegrityError and logging a warning. After successful storage, the view fetches updated season records, renders a chart image synchronously via asyncio.to_thread to avoid blocking the event loop, and updates the original message with a confirmation embed and the generated chart file before stopping itself. The on_timeout method handles expiration by disabling all interactive components and attempting to update the message state. This class is instantiated within the feels command when unrated matches are detected, serving as the primary interface for collecting user feedback on past performances. The caller assigns the returned message object to view.message to enable proper timeout handling and state synchronization.

**Note**:
· The view enforces a timeout period defined by _VIEW_TIMEOUT; interactions after expiration will be ignored unless the UI components are manually re-enabled.
· Only the user who triggered the /feels command can interact with this view; other users will receive an ephemeral error message and cannot modify the state.
· Duplicate rating submissions for the same match and user are safely handled via database constraint catching, preventing crashes while logging the event.
· The chart rendering is offloaded to a thread pool to prevent blocking the Discord bot's main event loop during synchronous image generation.
· The view must be assigned the returned message object (view.message = message) by the caller to enable proper timeout handling and state updates.

**Output Example**:
Embed Title: Match Rating Saved
Embed Description: You rated match #1234567890 with a score of 8/10.
Attachments: feels_chart.png (PNG image displaying the user's rating trend for the current season)
UI State: All interactive components disabled, view stopped.
### FunctionDef __init__(self, bundle, unrated_entries, feels_store, author_id)
**__init__**: The function of __init__ is to initialize the FeelsRatingView instance by configuring internal state, constructing a Discord dropdown menu from unrated match entries, and wiring it to handle user selection events.
**parameters**: The parameters of this Function.
· bundle: MatchBundle - A container holding season context, preloaded match details, and user metadata required for downstream processing.
· unrated_entries: list[MatchListEntry] - A collection of structured match summaries that have not yet been submitted for rating.
· feels_store: FeelsStore - The asynchronous data access layer responsible for persisting, retrieving, and managing match rating records in a SQLite database.
· author_id: int - The Discord user identifier of the message author who will interact with this view.
**Code Description**: This method initializes the interactive Discord view by first invoking the parent discord.ui.View constructor with a predefined timeout value. It stores references to the provided bundle, feels_store, and author_id for later use in rating submission and context retrieval. The method constructs an in-memory dictionary named _entries_by_id that maps each match's unique identifier to its corresponding MatchListEntry object, enabling efficient O(1) lookups during subsequent interaction handling. A _selected_entry attribute is initialized as None to track the user's active choice throughout the view's lifecycle.

The core initialization logic iterates through the unrated_entries list, generating a discord.SelectOption for each entry. Each option's label is formatted with an index number, outcome abbreviation (V for win, D for draw/loss), match score, and map name. The description includes the primary hero name, KDA ratio, and game mode. Both fields are programmatically truncated to 97 characters if they exceed the Discord API limit of 100 characters to prevent runtime errors. These formatted options populate a discord.ui.Select component configured to accept exactly one value. The select component's placeholder is set to prompt match selection, and its callback is explicitly bound to the _on_match_select method. Finally, the completed select component is attached to the view via add_item, making it visible and interactive when the associated Discord message is rendered. Functionally, this initialization phase bridges raw match data from MatchBundle and FeelsStore with Discord's interactive UI framework, preparing the state machine for the subsequent rating selection workflow handled by _on_match_select.
**Note**: Points to note about the use of the code
- The method strictly adheres to Discord API character limits; exceeding 100 characters in labels or descriptions will cause silent failures or API errors, which is mitigated by the explicit truncation logic.
- If the unrated_entries list is empty, the resulting dropdown will contain no options and may render incorrectly or fail to trigger interaction events.
- The _entries_by_id dictionary is critical for the subsequent _on_match_select callback; any mismatch between stored match IDs and interaction payloads will result in failed lookups.
- View state such as _selected_entry is managed entirely in memory during the message's active lifespan; persistence to FeelsStore occurs only after successful user interaction and validation.
- The timeout parameter is inherited from an external _VIEW_TIMEOUT constant; once elapsed, Discord automatically disables all interactive components on the message.
- Callback binding must occur before add_item execution to ensure proper event routing within Discord's component lifecycle.
***
### FunctionDef interaction_check(self, interaction)
**interaction_check**: The function of interaction_check is to verify whether the user triggering an interaction is authorized to do so by checking if they match the original command author, returning a boolean result accordingly.
**parameters**: 
· interaction: A discord.Interaction object representing the user's interaction with the view component.
**Code Description**: This asynchronous method evaluates the authorization status of a Discord user interacting with a specific view component. It compares the unique identifier of the user who triggered the interaction (interaction.user.id) against a stored author identifier (self._author_id). If the identifiers match, the method immediately returns True, permitting the interaction to proceed. If the identifiers do not match, the method triggers an ephemeral response via interaction.response.send_message(), delivering a localized notification in French stating that only the original command author is permitted to rate the matches. Following this notification, the method returns False, effectively blocking further processing of the unauthorized interaction. The use of async ensures non-blocking execution within the Discord.py event loop, and the explicit type hinting clarifies the expected input and output types.
**Note**: The authorization check relies on a pre-initialized instance variable _author_id, which must be correctly set during view instantiation. The response message is ephemeral, meaning it will only be visible to the user who triggered the interaction and will automatically disappear after a short duration. The French text in the response should be localized or translated if the bot supports multiple languages. This method is typically integrated into a discord.ui.View subclass to enforce per-user restrictions on interactive components like buttons or select menus.
**Output Example**: 
- When the interacting user matches the command author: True
- When the interacting user does not match the command author: False (accompanied by an ephemeral message visible only to that user)
***
### FunctionDef _on_match_select(self, interaction)
**_on_match_select**: The function of _on_match_select is to handle the user's selection of a specific match from an interactive dropdown, validate the selection, replace the initial menu with a rating selector, and update the Discord message with a contextual embed prompting for a score.
**parameters**: The parameters of this Function.
· interaction: discord.Interaction - The Discord interaction object triggered when a user selects a match option from the initial dropdown menu.
**Code Description**: This asynchronous method serves as the event handler for the initial match selection phase within the FeelsRatingView workflow. Upon invocation, it extracts the selected match identifier from the interaction payload and retrieves the corresponding MatchListEntry instance from the internal _entries_by_id dictionary. If the entry does not exist, it immediately responds with an ephemeral error message ("Match introuvable.") and terminates execution. When a valid entry is found, the method stores it in the view's _selected_entry attribute for subsequent steps. It then clears all existing interactive components from the view using clear_items() to prepare for the next stage of the workflow. A new discord.ui.Select component is instantiated to allow users to choose a rating between 1 and 10, dynamically generating options based on the _RATING_LABELS mapping. The callback for this new selector is explicitly bound to the _on_rating_select method. After adding the rating selector to the view, the method updates the original interaction message by calling build_feels_rating_prompt_embed with the selected entry to generate a detailed embed containing match statistics and outcome information. The updated embed and the modified view are applied to the message via edit_message. This function acts as the critical bridge between match identification and rating submission, ensuring state consistency across the interactive component lifecycle. It is initially wired as the callback for the primary match selection dropdown during FeelsRatingView.__init__, and it directly invokes build_feels_rating_prompt_embed to format the updated message content before returning control to the Discord API event loop.
**Note**: Points to note about the use of the code
- The method relies on self._entries_by_id being properly initialized during FeelsRatingView.__init__; if this dictionary is empty or malformed, valid selections will fail silently or trigger the error path.
- Discord API constraints require that edit_message be called within the interaction response window; the method correctly uses interaction.response.edit_message to comply with timeout limits.
- The view state is mutated in-place (clear_items and add_item); this permanently alters the message's interactive components, making the initial match selector unrecoverable without creating a new view instance.
- The callback assignment rating_select.callback = self._on_rating_select must occur before adding the item to ensure proper event routing when the user interacts with the rating dropdown.
- All localized strings and labels are hardcoded in French; locale changes require externalizing these constants.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: interaction.data["values"][0] = "match_abc123"
- Output: None (The method updates the original Discord message in-place, replacing the match selection dropdown with a rating dropdown labeled "Choisir une note de 1 à 10…", and displays an embed titled "Quelle note pour ce match ?" containing the selected match's outcome, score, map, hero, KDA, and a prompt to select a rating.)
***
### FunctionDef _on_rating_select(self, interaction)
**_on_rating_select**: The function of _on_rating_select is to process a user's rating selection from a Discord dropdown menu, persist the rating to the database, generate a seasonal performance chart, and update the interaction response with a confirmation embed and image.
**parameters**: The parameters of this Function.
· interaction: discord.Interaction - The Discord interaction object triggered by the user selecting a rating value from the interactive dropdown component.
**Code Description**: This asynchronous method serves as the core callback handler for the rating selection workflow within the FeelsRatingView class. Upon invocation, it first validates that a match entry has been previously selected via the parent view's internal state; if missing, it sends an ephemeral error message and terminates early. It extracts the integer rating value from the interaction payload and immediately defers the response to comply with Discord API timeout constraints. The method then delegates data aggregation to build_feels_record, which combines the current match bundle, selected entry metadata, user ID, and chosen rating into a structured MatchFeelsRecord. This record is passed to FeelsStore.add_rating for asynchronous database persistence, wrapped in a try-except block to gracefully handle unique constraint violations (duplicate ratings) by logging a warning. Following successful or skipped persistence, the method retrieves the user's complete seasonal history via FeelsStore.list_for_season, passing the author ID, normalized tracker username, and season ID. The retrieved records are offloaded to a background thread using asyncio.to_thread for CPU-intensive chart generation via render_feels_chart. Finally, the method halts further view interactions with self.stop(), constructs a Discord file from the rendered PNG bytes, and updates the original interaction message by replacing the interactive view with a static confirmation embed generated by build_feels_saved_embed. The entire workflow is orchestrated by FeelsRatingView._on_match_select, which initially populates the view's state, configures the dropdown options, and assigns this method as the selection callback.
**Note**: Points to note about the use of the code
- The method must be awaited within an asynchronous context; calling it synchronously will result in a coroutine object that never executes.
- Discord API requires a response within 3 seconds; interaction.response.defer() is critical here to prevent interaction timeout errors while database queries and chart rendering complete.
- The duplicate rating check relies on SQLite's unique constraint handling at the caller level, as the persistence method itself does not suppress IntegrityError exceptions.
- Chart rendering is intentionally offloaded to a thread pool via asyncio.to_thread to prevent blocking the main event loop during matplotlib figure generation.
- Calling self.stop() permanently disables all interactive components in the view after execution; subsequent attempts to interact with the message will fail until a new view instance is created.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: interaction.data["values"][0] = "8"
- Output: None (The method updates the original Discord message in-place, replacing the interactive dropdown with a static embed titled "Note enregistrée : 8/10", displaying match details and seasonal statistics, and attaching a rendered bar chart image named "feels_chart.png".)
***
### FunctionDef on_timeout(self)
**on_timeout**: The function of on_timeout is to handle the expiration event of a Discord UI view by disabling all interactive components and updating the associated message state.
**parameters**: This function does not accept any explicit parameters. It operates implicitly on the instance (`self`) containing the view's children and attached message reference.
**Code Description**: The method executes automatically when the parent `discord.ui.View` reaches its configured timeout duration. It first iterates through all child components stored in `self.children`, setting their `disabled` attribute to `True` to prevent further user interaction. Following this, it verifies whether a Discord message is currently linked to the view via `self.message`. If a message exists, the method attempts to synchronize the updated component states by calling `await self.message.edit(view=self)`. This operation updates the original message in real-time with the newly disabled buttons or selectors. The update attempt is wrapped in a try-except block that catches `discord.HTTPException`, which typically occurs when the target message has been deleted, permissions are insufficient, or rate limits are triggered. Any caught exception is silently ignored to ensure the application continues running without interruption.
**Note**: This method is automatically invoked by the Discord.py framework upon view expiration and should not be called manually. Ensure that `self.message` remains a valid reference to an existing Discord message before timeout occurs, as the edit operation will fail gracefully if the message is removed or inaccessible. The silent exception handling means that update failures will not raise errors but also will not notify the user; consider logging these events in production environments if necessary.
***
