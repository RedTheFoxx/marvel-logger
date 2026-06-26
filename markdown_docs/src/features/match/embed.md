## FunctionDef build_no_registration_embed
**build_no_registration_embed**: The function of build_no_registration_embed is to generate a Discord embed object that informs users they have not linked their Tracker.gg account and provides instructions on how to do so.

**parameters**: This function does not accept any parameters.

**Code Description**: The function constructs and returns a discord.Embed instance configured with an orange color, a French title indicating the absence of a linked username, and a description guiding the user to either use the /register slash command or supply a username argument directly. Within the project architecture, this embed is utilized by the _resolve_username helper function in src/features/match/command.py. When _resolve_username is invoked without an explicit username argument and the user's account lacks a registered Tracker.gg link in the RegistrationStore, this function is called to generate the feedback message. The resulting embed is then dispatched as an ephemeral interaction response, ensuring only the invoking user sees the notification while gracefully terminating the username resolution process by returning None.

**Note**: The text content of the embed is hardcoded in French; ensure your bot's localization strategy aligns with this or adapt the strings if multilingual support is required. The function relies on the discord library being properly initialized and imported, as it directly instantiates discord.Embed and discord.Color. Since it returns a newly created object each time, it can be safely called multiple times without state leakage.

**Output Example**: 
{
  "title": "Aucun pseudo lié",
  "description": "Liez d'abord un pseudo Tracker.gg avec **/register**, ou précisez un `username` dans la commande.",
  "color": 16766720,
  "type": "rich"
}
## FunctionDef build_no_matches_embed(username)
**build_no_matches_embed**: The function generates a Discord embed message indicating that no recent ranked matches were found for a specified player in the current season.
**parameters**: 
· username: A string representing the player's display name or identifier used to personalize the embed description.
**Code Description**: This function constructs and returns a discord.Embed object specifically designed to communicate an empty result state during a ranked match lookup process. It sets the embed title to "Aucun match classé récent", formats the description to include the provided username in bold markdown, and specifies that no current season matches were found. The embed is styled with an orange color (discord.Color.orange()) to visually indicate an informational or warning state rather than a critical error. Within the project architecture, this function is exclusively invoked by the match slash command handler located in src/features/match/command.py. When the underlying tracker returns an empty match bundle for a resolved username, the caller triggers this function to generate feedback and sends it as an ephemeral followup message directly to the user. The function itself handles only the visual composition of the message; visibility scope and network transmission are managed by the calling command logic.
**Note**: The text content within the embed is hardcoded in French and does not adapt to user locale settings. The function strictly returns a discord.Embed instance and does not perform any API calls, logging, or message sending operations itself. Consumers of this function must ensure that the provided username parameter is properly formatted if markdown rendering is expected within Discord embeds.
**Output Example**: 
Title: Aucun match classé récent
Description: Aucune partie classée récente trouvée pour **PlayerName** sur la saison courante.
Color: Orange (RGB approx. 255, 165, 0)
Visibility: Ephemeral (handled by caller)
## FunctionDef _outcome_label(outcome)
**_outcome_label**: The function of _outcome_label is to translate a match outcome string into a French label indicating either victory or defeat.
**parameters**: The parameters of this Function.
· outcome: A string representing the result of a match, typically expected to be "win" or another value indicating a loss.
**Code Description**: This function implements a direct conditional mapping to convert game match outcomes into French terminology. It evaluates whether the input string exactly matches "win"; if true, it returns "Victoire". For any other input value, it defaults to returning "Défaite". Within the project architecture, this helper serves as a centralized localization utility for match results. It is functionally integrated into two key components: _match_field_value utilizes it to format the outcome text within the detailed description field of a Discord embed, while build_match_picker_embed calls it directly when constructing the names of individual match entries in a dropdown menu. This shared usage ensures consistent French terminology across all UI display layers without duplicating translation logic or introducing formatting inconsistencies.
**Note**: The function relies on exact string matching and does not perform case-insensitive comparisons or handle additional game states such as draws, cancellations, or pending results. Any input value other than the lowercase string "win" will be treated as a loss. Developers should ensure that the incoming data strictly follows the expected format before passing it to this function to prevent unintended defaulting to "Défaite".
**Output Example**: 
Input: outcome = "win" -> Output: "Victoire"
Input: outcome = "loss" -> Output: "Défaite"
## FunctionDef _format_played(entry)
**_format_played**: The function of _format_played is to convert an optional datetime timestamp from a match entry into a standardized UTC date and time string, or return a placeholder if the timestamp is unavailable.

**parameters**: The parameters of this Function.
· entry: MatchListEntry - A structured data object representing a single match record, which contains the `played_at` attribute holding the optional UTC timestamp of when the match occurred.

**Code Description**: This function serves as a dedicated formatting utility for extracting and presenting temporal metadata from match records. It accepts a `MatchListEntry` instance and safely accesses its `played_at` attribute. If the attribute contains a valid `datetime.datetime` object, the function applies the `strftime` method with the format string `"%d/%m/%Y %H:%M UTC"` to produce a fixed-width, human-readable timestamp. When the `played_at` attribute is `None`, the function returns an em dash (`"—"`) as a visual placeholder to maintain consistent layout alignment in downstream displays. The function is exclusively invoked by `_match_field_value` within the same module, where its output is concatenated to the end of a multi-line match summary string. This integration ensures that temporal context is consistently appended to match metadata without disrupting the existing formatting logic or introducing null reference errors. By centralizing timestamp formatting in this utility, the codebase avoids repetitive datetime handling across multiple display components and guarantees uniform temporal representation in UI embeds and logs.

**Note**: Consumers must ensure that the `entry` object passed to this function is properly initialized and contains valid internal references, as accessing `played_at` on a malformed entry will raise an AttributeError. The function does not perform timezone conversion; it assumes the input timestamp is already in UTC, as indicated by the hardcoded suffix in the format string. The fallback placeholder `"—"` is intentionally chosen to occupy approximately the same visual width as the formatted timestamp, preventing layout shifts in fixed-width UI components like Discord embeds or terminal outputs. Direct modification of the format string should be avoided unless a global temporal display standard is updated across the project.

**Output Example**: `24/05/2024 14:30 UTC` (when played_at is valid) or `—` (when played_at is None).
## FunctionDef _match_field_value(entry)
**_match_field_value**: The function of _match_field_value is to format a structured match record into a multi-line, rich-text string containing outcome, score, game mode, map, hero performance, rank details, and timestamp for display in Discord embeds.
**parameters**: The parameters of this Function.
· entry: MatchListEntry - A structured data object representing a single match record, containing metadata, player statistics, hero information, rank snapshot, and optional timestamps.
**Code Description**: This function acts as a dedicated formatter that aggregates various attributes from a MatchListEntry instance into a cohesive, visually structured string. It begins by translating the raw match outcome into localized French terminology via _outcome_label. It then extracts the hero's display name and rank snapshot from the entry. Conditional logic is applied to safely construct rank-related metadata, appending the rating score (RS) and rating delta only if the rank object and its respective attributes exist. The core return value concatenates multiple formatted segments: the bolded outcome and final score, the game mode alongside the bolded map name with an optional location suffix, the hero name paired with a bolded KDA ratio followed by raw kill/death/assist counts, the previously constructed rank metadata, and finally the formatted timestamp generated by _format_played. The resulting string uses Discord-compatible markdown formatting to enhance readability within embed field constraints. Functionally, this utility bridges raw parsed match data and UI presentation layers. It is exclusively invoked by build_match_picker_embed, which iterates over a collection of matches and assigns the returned string as the value parameter for each dropdown menu entry in a Discord interaction embed. By centralizing the formatting logic here, the codebase ensures consistent layout, safe attribute access, and uniform presentation across all match list displays without duplicating string construction patterns.
**Note**: The function assumes that entry.hero and entry.rank are initialized objects; accessing .name or .rs on uninitialized nested attributes will raise an AttributeError. The conditional checks for rank and its attributes prevent null reference errors but do not validate the underlying data types. String concatenation relies on exact attribute names as defined in MatchListEntry; any schema changes to the data model require corresponding updates here. The output strictly uses Discord-compatible markdown formatting, so consumers should avoid passing this string to contexts that do not support rich text rendering. Additionally, the function does not handle missing or malformed map locations gracefully beyond omitting the parentheses; it simply skips the suffix if entry.map_location is falsy.
**Output Example**: 
**Victoire** · 1-0
Competitive · **Ascent** (Mid)
Phoenix · KDA **3.5** (7/2/4) · 1850 RS (+25)
24/05/2024 14:30 UTC
## FunctionDef build_match_picker_embed(bundle)
**build_match_picker_embed**: The function of build_match_picker_embed is to construct a Discord embed message that displays a list of recent ranked matches for a specified player, serving as an interactive picker for detailed scoreboard viewing.
**parameters**: The parameters of this Function.
· bundle: MatchBundle - A data container holding the tracked player's username, optional season identifier, and a list of match preview entries to be rendered in the embed.
**Code Description**: This function generates a structured Discord embed designed to present a list of recent ranked matches. It begins by constructing a dynamic URL pointing to the player's match history on an external tracker service, optionally appending a season query parameter if a season_id is present in the bundle. The core embed is initialized with a French title indicating "Recent Ranked Matches," a description prompting the user to select a match from a dropdown menu below, a predefined color constant, and the generated tracker URL. The function then iterates over the entries list within the provided MatchBundle, using enumerate with a 1-based index to format each match entry. For each entry, it appends a field to the embed where the name combines the match number, the localized outcome label via _outcome_label, and the final score, while the value is populated by _match_field_value, which formats detailed match metadata including hero performance, rank information, map details, and timestamp. After processing all entries, it attaches a footer referencing "Tracker.gg · Marvel Rivals" and sets the embed's timestamp to the current UTC time before returning the completed discord.Embed object. Functionally, this utility acts as the primary UI renderer for the match picker feature, bridging raw scraped match data with Discord's rich message format. It is directly invoked by the /match slash command handler in src/features/match/command.py, which passes the fetched bundle to this function after confirming that match data exists. The embed is subsequently paired with a MatchPickerView instance and sent as an ephemeral followup response, enabling users to interactively select matches for detailed analysis.
**Note**: The function assumes that bundle.entries contains valid MatchListEntry objects compatible with _outcome_label and _match_field_value. It does not implement pagination or field count validation; if the entry list exceeds Discord's platform constraints, the embed may fail to render correctly. The function relies on external constants (TRACKER_MATCHES_URL, DEFAULT_EMBED_COLOR) and helper functions that must be properly imported in the module scope. The timestamp generation uses datetime.timezone.utc to ensure consistent time representation regardless of server locale. Developers should verify that the caller ensures bundle.entries is non-empty before invocation, as an empty list will result in an embed with no match fields, which may appear incomplete to end users.
**Output Example**: 
Title: Derniers matchs classés — PlayerName123
Description: Choisissez un match dans le **menu déroulant** ci-dessous pour afficher le scoreboard détaillé.
Fields:
#1 · Victoire · 1-0
Competitive · **Ascent** (Mid)
Phoenix · KDA **3.5** (7/2/4) · 1850 RS (+25)
24/05/2024 14:30 UTC

#2 · Défaite · 0-1
Competitive · **Haven** 
Sage · KDA **2.1** (4/3/6) · 1780 RS (-15)
24/05/2024 14:15 UTC

Footer: Tracker.gg · Marvel Rivals
Timestamp: 2024-05-24T14:35:00+00:00
URL: https://tracker.gg/marvel-rivals/profile/...?season=1
## FunctionDef _badge_prefix(player)
**_badge_prefix**: The function of _badge_prefix is to determine and return the appropriate award badge prefix string based on a player's MVP or SVP status within a match context.
**parameters**: The parameters of this Function.
· player: MatchPlayerRow - A structured data model encapsulating a single player's comprehensive statistics, identity, and match context, specifically providing the `is_mvp` and `is_svp` boolean flags used for award evaluation.
**Code Description**: This function operates as a conditional formatter that evaluates the award status of a provided player instance. It sequentially checks the `player.is_mvp` attribute; if true, it returns "MVP ". If false, it evaluates `player.is_svp`; if true, it returns "SVP ". If neither condition is satisfied, it returns an empty string. The function is directly invoked by `_compact_player_line` to prepend award labels to a player's username when constructing condensed scoreboard lines for Discord embeds. The trailing space included in the returned badge strings ensures correct visual spacing during string interpolation without introducing leading whitespace in standard cases. The logic relies entirely on the boolean flags populated during the match parsing phase, which extract raw API response data and map it into the `MatchPlayerRow` schema before downstream UI rendering consumes it.
**Note**: The function assumes that `player.is_mvp` and `player.is_svp` are valid boolean values as defined in the `MatchPlayerRow` model. The sequential evaluation order safely handles award prioritization, ensuring MVP status is recognized first if both flags were somehow true (though they are typically mutually exclusive in practice). When no award is present, the empty string return value prevents unwanted spacing artifacts in the final formatted output. Developers integrating this function should ensure that the input object originates from the standard match parsing pipeline to guarantee attribute availability and consistent type safety.
**Output Example**: 
- Returns `"MVP "` when `player.is_mvp` is True.
- Returns `"SVP "` when `player.is_svp` is True and `player.is_mvp` is False.
- Returns `""` when both flags are False.
## FunctionDef _compact_player_line(player)
**_compact_player_line**: The function of _compact_player_line is to format a single player's match statistics into a condensed, Discord-compatible string line containing award status, username, KDA ratio, kill/death/assist counts, damage dealt, and rank rating changes.
**parameters**: The parameters of this Function.
· player: MatchPlayerRow - A structured data model encapsulating the player's identity, match performance metrics, and optional rank progression data.
**Code Description**: This function constructs a single-line summary string by aggregating key player statistics into a list of formatted components. It begins by prepending an award badge (MVP or SVP) to the bolded username using `_badge_prefix`. It then appends the KDA ratio and the raw kill/death/assist tally. If the `damage` attribute is present, it adds the damage dealt metric. For rank information, it checks for a rating delta (`rs_delta`) first, falling back to the base rating change (`rs`) if available, and appends the corresponding RS value. All collected components are joined using a middle dot separator (` · `). Finally, the resulting string is strictly truncated to a maximum length of 1024 characters to comply with Discord embed field constraints. The function operates as a core formatting utility within the match embedding pipeline, directly invoked by `_team_block` to generate individual roster entries for team-based scoreboard displays. Its reliance on `MatchPlayerRow` ensures type-safe access to statistical fields, while its conditional logic gracefully handles optional metrics without raising errors.
**Note**: The function assumes that all accessed attributes on the `player` object are properly initialized by the upstream match parser. Optional fields like `damage` and `rank` must be explicitly checked before use, which this function correctly implements. The 1024-character truncation is a hard limit imposed by Discord's embed field size restrictions; developers should be aware that further truncation may occur at the `_team_block` level if multiple player lines exceed the total block limit. The middle dot separator and markdown bold syntax are specifically chosen for Discord rendering compatibility.
**Output Example**: `MVP **PlayerName** 3.5 KDA · 12/4/8 · 45000 dmg · +25 RS`
## FunctionDef _team_block(players)
**_team_block**: The function of _team_block is to aggregate and format a list of player statistics into a single, Discord-compatible string block representing a team's roster summary.
**parameters**: The parameters of this Function.
· players: list[MatchPlayerRow] - A collection of MatchPlayerRow instances containing individual player match data, including identity, performance metrics, and rank information.
**Code Description**: This function processes a sequence of player records by invoking _compact_player_line on each element to generate condensed statistical lines. These individual lines are concatenated using newline characters to form a cohesive roster block. If the input list is empty or yields no valid lines, the function defaults to returning an em-dash character to maintain visual consistency in the UI. To ensure compatibility with Discord embed field constraints, the resulting string is evaluated against a 1024-character threshold; exceeding this limit triggers a truncation to 1020 characters followed by an ellipsis suffix. The function operates as a critical aggregation step within the match embedding pipeline, directly invoked by build_match_detail_embed to supply the formatted value for team-specific embed fields. Its design ensures that downstream Discord rendering remains stable while preserving the core statistical data provided by _compact_player_line.
**Note**: Developers should be aware that the 1024-character limit is a hard constraint imposed by Discord's API for embed field values. Truncation may result in the loss of trailing player statistics, so prioritizing critical metrics in _compact_player_line is recommended. The function assumes that MatchPlayerRow instances are fully populated by upstream parsers and that _compact_player_line handles all necessary conditional formatting safely. Empty or malformed input lists will gracefully fallback to the em-dash placeholder rather than raising exceptions.
**Output Example**: MVP **Alpha** 3.5 KDA · 12/4/8 · 45000 dmg · +25 RS\nSVP **Beta** 2.1 KDA · 8/6/10 · 32000 dmg\n— **Gamma** 1.8 KDA · 5/7/12
## FunctionDef _player_detail_block(player)
**_player_detail_block**: The function of _player_detail_block is to format a player's comprehensive match statistics and identity into a structured, multi-line string for Discord embed rendering.
**parameters**: The parameters of this Function.
· player: MatchPlayerRow - An instance containing the player's username, hero roster, combat metrics, rank data, and other match-specific attributes.
**Code Description**: This function accepts a single MatchPlayerRow object and constructs a formatted string representation of that player's performance. It begins by extracting the player's username and joining their played heroes' names into a comma-separated list, defaulting to an em-dash if empty. The core structure includes the KDA ratio alongside raw kill, death, and assist counts. Subsequent lines are conditionally appended based on the presence of specific metrics: solo_head_last for combat highlights, damage (with optional per-minute rate), blocked (with optional per-minute rate), healing (with optional per-minute rate), and accuracy. Rank information is also conditionally rendered by accessing nested attributes from the MatchRankSnapshot object, including tier name, rating points, and delta changes. All statistical values are bolded where applicable, and metric labels use French terminology. The function returns a single string with each metric on a new line, designed specifically for Discord embed field values. It is invoked by build_match_detail_embed to populate the "Votre performance" section when a specific player's match data is queried. The function relies entirely on the MatchPlayerRow model, which aggregates raw API data into typed fields, ensuring that all accessed attributes are either guaranteed to exist or safely handled through conditional checks and default string representations.
**Note**: The function assumes that numeric statistics within MatchPlayerRow are already formatted as strings by the upstream parser. Optional metrics like damage, healing, and rank may be None; the function safely skips rendering these sections if the corresponding attributes are falsy or missing. All metric labels are hardcoded in French, and the output string contains Discord-compatible markdown formatting (bold text and line breaks). Direct instantiation of this function outside the embed generation pipeline is unnecessary, as it serves strictly as a presentation-layer utility for Discord UI components.
**Output Example**: 
**PlayerName** · Hero1, Hero2
KDA **3.5** · 12 / 4 / 8
Solo / Head / Last · 5/3/10
Dégâts · **15420** (650/min)
Bloqués · **3200** (135/min)
Soins · **8900** (375/min)
Précision · 78%
Rang · Grandmaster · 5200 RS (-45)
## FunctionDef build_match_detail_embed(detail)
**build_match_detail_embed**: The function of build_match_detail_embed is to construct and return a formatted Discord embed object that visually represents the detailed statistics, team rosters, and outcome of a specific match based on provided MatchDetail data.

**parameters**: The parameters of this Function.
· detail: MatchDetail - An instance containing comprehensive match metadata, including score, map information, duration, timestamp, team rosters, and the queried player's identity and outcome.

**Code Description**: This function orchestrates the visual presentation of match data by translating structured MatchDetail model attributes into a Discord-compatible discord.Embed object. It begins by evaluating the queried_outcome attribute to assign a contextual color (green for wins, red for losses, or a default fallback). A dynamic header string is assembled using the game mode, map name with an optional location suffix, final score, match duration, and UTC-formatted timestamp. The embed is initialized with a title referencing the queried username, the constructed description, the determined color, and the direct match URL. If team data exists, a visual separator field is inserted. The function then iterates through each MatchTeam in the detail object, appending a field for the team label (with an optional score suffix) populated by the _team_block utility, which aggregates individual player statistics into a condensed roster string. Subsequently, it searches all team rosters to locate the specific MatchPlayerRow instance matching the queried username. Upon finding this player, it appends a dedicated "Votre performance" field formatted via the _player_detail_block utility, which expands individual combat metrics, hero selections, and rank data into a detailed multi-line string. A final separator is added before setting the embed footer to "Tracker.gg · Marvel Rivals" and applying the match timestamp if available. Functionally, this object acts as the primary rendering bridge between the backend MatchDetail data model and the frontend Discord UI. It is directly invoked by the MatchPickerView._on_select handler in src/features/match/view.py when a user selects a match from an interactive picker view. The function relies on _team_block for roster aggregation and _player_detail_block for individual performance expansion, ensuring consistent formatting, safe handling of optional metrics, and strict adherence to Discord's embed field constraints.

**Note**: Developers should ensure that the MatchDetail instance passed to this function contains fully populated team rosters and player data, as missing or malformed attributes may result in empty fields or unexpected formatting. The function strictly adheres to Discord's API limits; while _team_block handles the 1024-character truncation for roster strings, downstream consumers should verify that detail.teams and detail.played_at are handled gracefully when null. The color logic explicitly checks for "win" and "loss" strings, so any deviation in the queried_outcome value will trigger the default embed color. Additionally, the function assumes French localization for specific UI labels (e.g., "Votre performance") as dictated by its dependent formatting utilities. Direct instantiation outside the embed generation pipeline is unnecessary, as it serves strictly as a presentation-layer utility for Discord UI components.

**Output Example**: 
Title: Match — PlayerName123
Description: **Competitive** · King's Row · 4/3 · 18:42
15/03/2024 14:30 UTC
Fields:
[Team Alpha (2)]
MVP **HeroA** 4.2 KDA · 15/3/9 · 42k dmg
SVP **HeroB** 2.8 KDA · 8/5/12
[Team Beta (3)]
**HeroC** 3.1 KDA · 10/6/7
**HeroD** 1.9 KDA · 4/8/11
[Votre performance]
**PlayerName123** · HeroA, HeroB
KDA **4.2** · 15 / 3 / 9
Dégâts · **42000** (2250/min)
Rang · Grandmaster · 5150 RS (+12)
Footer: Tracker.gg · Marvel Rivals
Timestamp: 15/03/2024 14:30 UTC
## FunctionDef build_match_detail_unavailable_embed(entry, username)
**build_match_detail_unavailable_embed**: The function of build_match_detail_unavailable_embed is to construct a Discord embed message that informs users when detailed match scoreboard data cannot be loaded, providing a fallback link to an external tracker website.
**parameters**: The parameters of this Function.
· entry: An instance of MatchListEntry containing structured match metadata, specifically the direct external URL linking to the full match details.
· username: A string representing the player's display name or identifier used for contextualizing the embed message.
**Code Description**: This function generates a fallback Discord Embed object when comprehensive match statistics are unavailable. It utilizes the discord.Embed class to format a warning-style notification, setting the title to indicate unavailability alongside the provided username, and populating the description with a localized French message explaining the loading failure along with a clickable link to Tracker.gg derived from entry.match_url. The embed is styled with an orange color to visually distinguish it as a fallback or informational state rather than a standard success response. Functionally, this component serves as a critical error-handling and user-experience bridge within the match detail feature. It is invoked by the MatchPickerView._on_select method in src/features/match/view.py when a user selects a specific match from a list but the system lacks the detailed scoreboard data for that entry. In such cases, instead of failing silently or returning an empty response, the view delegates to this function to render a graceful fallback UI element. The function depends on MatchListEntry from src/tracker/models.py, which supplies the necessary match_url attribute and other contextual metadata. By extracting only the required URL field, it maintains a loose coupling while ensuring that external tracking links remain functional even when internal parsing fails.
**Note**: The embed text is hardcoded in French; ensure this aligns with your application's localization strategy or parameterize it for multi-language support. The function assumes entry.match_url is a valid, non-empty string; downstream validation should verify its presence before invocation to prevent broken links. As it returns a discord.Embed object, consumers must ensure the Discord.py library is properly initialized and that the embed is passed to an appropriate interaction response method. The orange color choice explicitly signals a partial success or fallback state, which should be documented in UI guidelines to maintain consistency across the application.
**Output Example**: 
Embed(title='Détail indisponible — PlayerOne', description='Impossible de charger le scoreboard pour **PlayerOne**.\n[Voir sur Tracker.gg](https://tracker.gg/valorant/matches/abc123)', color=0xFFA500, url='https://tracker.gg/valorant/matches/abc123')
