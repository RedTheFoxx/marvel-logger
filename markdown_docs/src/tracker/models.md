## ClassDef StatValue
**StatValue**: The function of StatValue is to encapsulate a statistical metric alongside its optional percentile ranking for structured data handling and UI rendering.
**attributes**: The attributes of this Class.
· display: A string representing the formatted or raw textual value of the statistic.
· percentile: An optional floating-point number indicating the percentile rank of the statistic, defaulting to None.
**Code Description**: The StatValue class serves as a lightweight data model designed to store and structure statistical information within the tracker module. It consists of two primary attributes: display, which holds the textual representation of the stat value, and percentile, which optionally stores a float indicating where this value ranks relative to a distribution. This class is instantiated by the _stat_value function in src/tracker/parser.py, which extracts relevant data from raw dictionaries and maps them into StatValue instances. Once created, these instances are attached to the PlayerProfile model as optional fields for metrics such as kda, win_pct, wins, mvp_pct, and svp_pct. Downstream components like _percentile_badge in src/features/stats/embed.py consume the percentile attribute to dynamically generate contextual badges (e.g., Top X% or Bottom X%) for user interface rendering. The design ensures that statistical data remains decoupled from raw parsing logic while providing a consistent structure for profile aggregation and embed generation.
**Note**: When using StatValue, developers should account for the optional nature of the percentile field by implementing appropriate null checks before performing mathematical operations or comparisons. The display attribute is expected to contain pre-formatted text, so direct numerical parsing from this field is not recommended. Instances are typically created through the parser module rather than instantiated directly, ensuring consistent data validation and extraction across the application.
## ClassDef RankInfo
**RankInfo**: The function of RankInfo is to serve as a structured data model representing a player's competitive rank, including tier details, rating score, visual assets, and seasonal context.

**attributes**: The attributes of this Class.
· tier_name: str - The full display name of the rank tier.
· tier_short: str - The abbreviated or short form of the tier name.
· rs: str - The numerical rating score associated with the rank, stored as a formatted string.
· icon_url: str | None - Optional URL pointing to an image representing the tier's icon.
· color: str | None - Optional hexadecimal color code used for visual styling of the tier.
· season_label: str | None - Optional label identifying the specific season during which this rank was achieved or is active.

**Code Description**: The RankInfo class acts as a lightweight data container for competitive ranking information within the application. It is primarily instantiated by parsing functions in src/tracker/parser.py, specifically _rank_from_stat and _rank_from_peak_entry, which extract relevant metadata from raw API responses or data dictionaries. These parsers map source fields like tierName, tierShortName, rating values, iconUrl, color, and seasonal identifiers directly to the corresponding attributes of RankInfo. Once populated, instances are stored within the PlayerProfile model in src/tracker/models.py as current_rank, season_peak, lifetime_peak, and season_peaks. This enables centralized management of rank data across different profile states. Downstream, the _rank_line function in src/features/stats/embed.py consumes RankInfo instances to generate formatted text strings for display purposes, utilizing tier_name, rs, and optionally season_label to construct readable rank representations. The class effectively bridges raw data ingestion, model storage, and presentation layers without implementing business logic or validation methods itself.

**Note**: Points to note about the use of the code
- All attributes except tier_name, tier_short, and rs are optional and default to None. Downstream consumers must handle potential None values appropriately before accessing icon_url, color, or season_label.
- The rs attribute is explicitly typed as a string, indicating that rating scores should be formatted (e.g., with commas or specific precision) during parsing rather than stored as raw numeric types.
- When parsing data, fallback logic in the parser functions guarantees that tier_name and tier_short are never empty strings, but optional fields like icon_url and color may remain None if the source data lacks them.
- The class relies on external formatting utilities for display generation; it does not contain methods for string conversion or validation itself.
## ClassDef RoleStats
**RoleStats**: The function of RoleStats is to serve as a data model for storing and representing aggregated performance metrics associated with a specific player role in a game session or season.

**attributes**: The attributes of this Class.
· name: str - Represents the identifier or display name of the role.
· win_pct: str - Stores the win percentage formatted as a string.
· wins: str - Records the total number of matches won in this role.
· kda: str - Holds the Kill/Death/Assist ratio value.
· kills: str - Captures the total kill count.
· deaths: str - Captures the total death count.
· assists: str - Captures the total assist count.

**Code Description**: RoleStats is a lightweight typed class designed exclusively as a data container for role-specific gameplay statistics. It does not contain any business logic or methods, adhering to a pure data model pattern. Within the project architecture, this class is instantiated during the profile parsing phase in parse_profile, where raw API segments of type hero-role are processed. The parser extracts metadata and combat statistics from these segments and maps them directly to the corresponding attributes of RoleStats. These instances are subsequently aggregated into a list assigned to the roles attribute of the PlayerProfile class, which acts as the central model for user profile data. Downstream, the _role_field_value function in embed.py consumes individual RoleStats objects to construct formatted display strings for UI embeds, utilizing attributes like win_pct, wins, and combat metrics to generate human-readable output. The use of string types for all numeric fields indicates that the class is optimized for direct presentation layer consumption rather than mathematical computation.

**Note**: Points to note about the use of the code
- All statistical values are stored as strings, which implies they may already contain formatting (e.g., percentage signs or localized decimal separators) and should not be used directly in arithmetic operations without parsing.
- The class relies on external parsers to populate its fields; attempting to instantiate it with missing or incorrectly typed data will result in type mismatches downstream.
- It is strictly tied to the hero-role data segments from the source API, meaning it only represents role-specific aggregated statistics rather than individual match events.
- When extending or modifying this model, ensure that corresponding updates are made to parse_profile for data ingestion and _role_field_value for display formatting to maintain consistency across the pipeline.
## ClassDef HeroStats
**HeroStats**: The function of HeroStats is to serve as a structured data model representing aggregated performance statistics for a specific game hero within a player's profile.

**attributes**: The attributes of this Class.
· name: str - The display name of the hero.
· image_url: str | None - The URL pointing to the hero's portrait or icon image, which may be null if unavailable.
· win_pct: str - The win rate percentage for this hero, formatted as a string.
· record: str - The match record (wins-losses-ties) for this hero, formatted as a string.
· kda: str - The Kill/Death/Assist ratio, formatted as a string.
· kills: str - The total number of kills achieved with this hero.
· deaths: str - The total number of deaths incurred while playing this hero.
· assists: str - The total number of assists provided while playing this hero.
· matches_played: float - The total number of matches played with this hero, defaulting to 0.0.

**Code Description**: The HeroStats class acts as a data transfer object that encapsulates combat and performance metrics for individual heroes. It is instantiated within the parse_profile function in src/tracker/parser.py, where raw API response segments filtered by type "hero" are processed. During instantiation, the parser extracts metadata such as the hero name and image URL, alongside statistical values like win percentage, match record, KDA ratio, and absolute kill/death/assist counts. The matches_played value is explicitly cast to a float from the raw data source. Instances are filtered to exclude heroes with fewer than 0.5 matches played, sorted in descending order by matches_played, and the top three instances are assigned to the top_heroes list attribute of the PlayerProfile class. Functionally, these populated HeroStats objects are subsequently consumed by the _hero_field_value function in src/features/stats/embed.py, which formats their attributes into a concise, emoji-prefixed string representation for display in a Discord embed field. The class relies on strict type hints to enforce data consistency across the parsing and presentation layers of the application, ensuring that statistical values remain compatible with downstream string formatting operations.

**Note**: Points to note about the use of the code
- All statistical fields (win_pct, record, kda, kills, deaths, assists) are typed as strings to accommodate formatted values or placeholder characters like "—" when data is missing from the source API.
- The matches_played field defaults to 0.0 but is dynamically populated during parsing; ensure downstream consumers handle float formatting appropriately if integer display is required for UI rendering.
- The class does not contain business logic, validation methods, or serialization routines; it strictly functions as a passive data container between the parser and the embed generator.
- When extending or modifying this model, maintain compatibility with the string-based statistical fields to prevent type errors in the _hero_field_value formatter, which directly accesses these attributes without intermediate conversion.
## ClassDef MatchHero
**MatchHero**: The function of MatchHero is to represent a hero character played during a match, storing its display name and an optional icon image URL.
**attributes**: The attributes of this Class.
· name: str - The textual identifier or display name of the hero.
· image_url: str | None - The URL pointing to the hero's icon or portrait image. Defaults to None when no image data is available.
**Code Description**: This class serves as a lightweight data model for encapsulating hero metadata within match-related structures. It contains only two fields: a required string for the hero name and an optional string for the associated image URL. Functionally, MatchHero acts as a bridge between raw API/metadata payloads and higher-level match visualization models. In the project architecture, it is instantiated by parser functions such as `_heroes_from_meta` and `parse_recent_matches`, which extract hero information from unstructured dictionary responses and map them into typed objects. Once constructed, MatchHero instances are consumed by two primary data models: `MatchListEntry` uses a single instance to display the primary or first hero in a match summary list view, while `MatchPlayerRow` aggregates multiple instances into a list to represent all heroes played by a specific player in a detailed scoreboard. This design ensures consistent hero data representation across both aggregated match lists and granular player statistics without duplicating parsing logic.
**Note**: When instantiating this class, the `name` attribute must always be provided, as it is required for identification. The `image_url` attribute is optional; consumers should implement null checks or fallback placeholders when rendering UI components or processing data, as missing image links are common in raw metadata responses. Ensure that downstream parsers validate the source dictionary keys (`name`, `imageUrl`, or `image`) before instantiation to prevent unexpected type mismatches.
## ClassDef MatchRankSnapshot
**MatchRankSnapshot**: The function of MatchRankSnapshot is to store and represent a player's rank information at the time of a specific match, including tier details, rating score, score change, and visual icon reference.
**attributes**: The attributes of this Class.
· tier_name: str - The full display name of the player's rank tier during the match.
· tier_short: str - A shortened code or abbreviation representing the rank tier.
· rs: str - The raw or displayed rating score associated with the rank at match time.
· rs_delta: str | None - The numerical change in the rating score resulting from the match, formatted as a signed string (e.g., "+15", "-8"), or None if unavailable.
· icon_url: str | None - The URL pointing to an image asset representing the rank tier, or None if no icon is provided.
**Code Description**: This class serves as a structured data model for capturing rank-related metadata during match processing. It is instantiated exclusively by the `_rank_from_match_stats` parser function, which extracts ranked mode information from raw match statistics dictionaries. The parser calculates the rating delta by parsing numeric values and formatting them with appropriate signs, then maps the tier name, short name, rating score, calculated delta, and icon URL into this structure. Once created, `MatchRankSnapshot` instances are attached to higher-level display models: `MatchListEntry` uses it to provide rank context in match list summaries, while `MatchPlayerRow` incorporates it into detailed player scoreboard rows. This design ensures consistent rank data propagation from raw statistical inputs through parsing logic to final UI representation layers without duplicating rank formatting logic across different view models.
**Note**: The `rs_delta` and `icon_url` fields are optional and default to None when the underlying match statistics do not contain ranked mode data or when delta/icon information is missing. Consumers of this class should handle potential None values appropriately, particularly when rendering UI components that expect string inputs for rating changes or image sources. Direct instantiation outside the parser should be avoided unless explicitly constructing test fixtures or mock data.
## ClassDef RatingChartPoint
**RatingChartPoint**: The function of RatingChartPoint is to represent a single data point on a ranked rating evolution chart following a rated match.
**attributes**: The attributes of this Class.
· rs: int - The player's rating score after the match.
· rs_delta: int | None - The change in rating score for this specific match, or None if unavailable.
· outcome: MatchOutcome | None - The result of the match, or None if not recorded.
· played_at: datetime.datetime | None - The timestamp when the match was played, or None if unknown.
· match_id: str - The unique identifier for the match.
**Code Description**: RatingChartPoint is a data class designed to encapsulate all necessary information for tracking and visualizing a player's rating progression over time. Each instance corresponds to a single rated match, storing the final rating score, the delta applied during that match, the match outcome, the exact timestamp of play, and the match identifier. In the project architecture, instances of this class are primarily constructed by the build_rating_chart function in src/tracker/parser_matches.py, which parses raw match list entries and populates the fields accordingly. The resulting list of RatingChartPoint objects is stored within the PlayerProfile.rating_chart field. Downstream, these points are consumed by the chart rendering pipeline in src/features/stats/chart.py. Functions such as _chart_axis_data extract rating values and timestamps for axis configuration, _plot_outcome_markers uses the outcome field to color-code markers on the graph, _resolve_total_delta aggregates individual deltas or calculates net change from the first and last points, and _plot_last_point highlights the most recent rating value. The class supports optional fields (rs_delta, outcome, played_at) to accommodate incomplete match data gracefully, ensuring robust chart generation even when certain metadata is missing.
**Note**: When using this class, ensure that the list of points passed to chart rendering functions is not empty, as it will raise a ValueError. The order of points in the list typically reflects chronological or sequential match progression, which directly impacts the x-axis mapping and delta calculations. Optional fields should be handled with conditional checks during custom processing to avoid attribute access errors on None values. All instances are primarily used as read-only data carriers within the tracking and visualization modules, and their structure is optimized for direct iteration and unpacking in plotting routines.
## ClassDef MatchPlayerRow
**MatchPlayerRow**: The function of MatchPlayerRow is to encapsulate a single player's comprehensive statistics, identity, and match context within a detailed scoreboard structure.
**attributes**: The attributes of this Class.
· username: str - The unique identifier or display name of the player.
· is_mvp: bool = False - Indicates whether the player received the Most Valuable Player award for the match.
· is_svp: bool = False - Indicates whether the player received the Second Most Valuable Player award.
· heroes: list[MatchHero] - A collection of MatchHero instances representing the characters played by this player during the match.
· rank: MatchRankSnapshot | None = None - Optional rank metadata captured at the time of the match, including tier and rating changes.
· kda_ratio: str = "—" - The calculated kill-death-assist ratio formatted as a string.
· kills: str = "0" - Total number of kills achieved by the player.
· deaths: str = "0" - Total number of times the player was eliminated.
· assists: str = "0" - Total number of assists provided by the player.
· solo_head_last: str | None = None - Additional combat metric tracking solo eliminations, headshots, or last hits.
· damage: str | None = None - Total damage dealt by the player.
· damage_per_min: str | None = None - Average damage dealt per minute.
· blocked: str | None = None - Total damage blocked or mitigated by the player.
· blocked_per_min: str | None = None - Average damage blocked per minute.
· healing: str | None = None - Total amount of healing provided by the player.
· healing_per_min: str | None = None - Average healing provided per minute.
· accuracy: str | None = None - Hit accuracy percentage or related metric.
· outcome: MatchOutcome | None = None - The match result (win/loss) for this specific player.
**Code Description**: This class serves as a structured data model for aggregating granular player statistics and contextual metadata during match processing. It is instantiated exclusively by the _parse_player_row parser function, which extracts raw statistical values from unstructured API responses and maps them into typed fields. The class relies on MatchHero to represent the roster of characters played by the user and MatchRankSnapshot to store rank progression data at the match timestamp. Once constructed, MatchPlayerRow instances are aggregated into MatchTeam collections for team-based organization. Downstream presentation logic in src/features/match/embed.py consumes these instances to generate formatted Discord embeds: _badge_prefix applies MVP/SVP labels, _compact_player_line and _team_block render condensed roster summaries, while _player_detail_block expands individual metrics like damage, healing, blocking, and rank changes. The parser also utilizes MatchPlayerRow directly via _player_roster_sort_key to prioritize players by award status and kill count, and parse_match_detail queries the object to determine the outcome for a specific requested username. This design centralizes player data representation, ensuring consistent formatting and metric propagation from raw parsing through team aggregation to final UI rendering.
**Note**: All statistical fields default to string representations of zero or em-dashes to prevent null reference errors during UI rendering. Optional fields such as rank, damage, healing, and accuracy may remain None if the source data lacks corresponding metrics; consumers must implement conditional checks before accessing nested attributes like rs_delta or icon_url. When instantiating this class, ensure that numeric strings are properly formatted by the parser to maintain consistency across embed layouts. Direct construction outside the parsing pipeline should be reserved for testing or mock data generation.
## ClassDef MatchTeam
**MatchTeam**: The function of MatchTeam is to encapsulate the metadata and aggregated player roster for a single team within a match scoreboard structure.
**attributes**: The attributes of this Class.
· label: str - The display name or identifier assigned to the team, such as "Équipe gagnante" or "Équipe perdante".
· won: bool - A boolean flag indicating whether the team secured victory in the match.
· score: int | None = None - The numerical score achieved by the team, which may remain unset during initial construction.
· players: list[MatchPlayerRow] = field(default_factory=list) - A collection of MatchPlayerRow instances representing the individual statistics and identity of each player on the roster.
**Code Description**: This class serves as a structured data model for aggregating team-level context alongside granular player statistics during match processing. It is primarily instantiated by the _build_teams parser function, which groups parsed MatchPlayerRow objects by team identifier, determines victory status based on match metadata and individual player outcomes, and assigns contextual labels. The parser dynamically calculates the won flag and attempts to parse the final score from display strings after instantiation. Once constructed, MatchTeam instances are collected into a list and attached to the teams attribute of the MatchDetail class, which represents the complete match scoreboard. This design enables downstream presentation logic to iterate over team rosters, apply sorting rules based on player metrics, and render condensed or detailed match summaries without directly handling raw parsing data. The class relies entirely on MatchPlayerRow for individual performance data and operates as a bridge between low-level parser outputs and high-level match context representation.
**Note**: The score attribute defaults to None and is only populated if the source display string contains valid integer values separated by a colon; consumers should handle potential None values during UI rendering. The players list uses a dataclass default factory to ensure safe mutability across instances. Team labels and win status are determined algorithmically by the parser based on available metadata, so direct instantiation outside the parsing pipeline is not recommended for production use. Ensure that numeric strings passed to score parsers are properly formatted to prevent silent failures during assignment.
## ClassDef MatchDetail
**MatchDetail**: The function of MatchDetail is to encapsulate the complete metadata and aggregated scoreboard structure for a single match, including team rosters, match statistics, and the queried player's specific outcome.
**attributes**: The attributes of this Class.
· match_id: str - The unique identifier assigned to the match.
· match_url: str - The direct URL linking to the detailed match page on the tracking service.
· game_mode: str - The specific game mode in which the match was played.
· map_name: str - The name of the map where the match occurred.
· map_location: str - Additional contextual location or variant information for the map.
· score: str - The final match score formatted as a string.
· duration: str | None - The total duration of the match, or None if unavailable.
· played_at: datetime.datetime | None - The exact timestamp when the match was played, or None.
· teams: list[MatchTeam] - A collection of MatchTeam instances representing the scoreboard data for both competing teams.
· queried_username: str - The username that was originally searched to retrieve this match data.
· queried_outcome: MatchOutcome | None = None - The result (win, loss, or draw) for the queried player in this match, or None if not applicable.
**Code Description**: This class serves as a structured data model that aggregates high-level match metadata alongside granular team and player statistics. It is primarily instantiated by the parse_match_detail function, which processes raw API responses to extract match attributes, format temporal and scoring data, parse individual player rows into MatchTeam objects, and determine the queried player's outcome. Once constructed, MatchDetail instances are stored within a MatchBundle object in the TrackerScraper client for caching and retrieval. Downstream presentation logic, specifically the build_match_detail_embed function, consumes this class to generate Discord embeds. The embed builder utilizes attributes such as game_mode, map_name, score, duration, played_at, and teams to dynamically format match summaries, apply conditional coloring based on queried_outcome, and highlight the specific performance metrics of the queried player within the team rosters. This design decouples raw data parsing from UI rendering by providing a unified, type-safe representation of match context.
**Note**: The score attribute is stored as a string rather than an integer to preserve original formatting from the source display. Both duration and played_at may be None if the source data lacks temporal information, requiring consumers to implement safe fallbacks during rendering. The queried_outcome field defaults to None and must be explicitly validated before use in conditional UI logic. The teams list relies on MatchTeam for roster aggregation, so modifications to team-level data should occur within the parsing pipeline rather than post-instantiation. Ensure that map_location is handled gracefully when empty, as it may not always contain valid contextual data.
## ClassDef MatchListEntry
**MatchListEntry**: The function of MatchListEntry is to represent a structured summary of a single match, aggregating metadata, player performance statistics, and contextual information for display in match list views and downstream processing features.
**attributes**: The attributes of this Class.
· match_id: str - The unique identifier for the match.
· match_url: str - The direct external URL linking to the full match details.
· outcome: MatchOutcome - The result or status of the match (e.g., win, loss).
· played_ago: str - A human-readable relative time string indicating when the match occurred.
· game_mode: str - The specific game mode in which the match was played.
· map_name: str - The name of the map used during the match.
· map_location: str - Additional contextual location or variant information for the map.
· score: str - The final score or result string associated with the match.
· hero: MatchHero - An instance containing the primary hero's display name and optional icon URL.
· rank: MatchRankSnapshot - An instance storing the player's rank tier, rating score, delta change, and icon reference at match time.
· kills: str - The number of kills achieved by the player, formatted as a string.
· deaths: str - The number of deaths experienced by the player, formatted as a string.
· assists: str - The number of assists recorded for the player, formatted as a string.
· kda_ratio: str - The calculated or raw KDA ratio presented as a string.
· played_at: datetime.datetime | None = None - The exact UTC timestamp of when the match was played, optional by default.
· season_id: int | None = None - The identifier of the competitive season associated with the match, optional by default.
**Code Description**: This class serves as a core data model that consolidates parsed match information into a single, structured object. It is primarily instantiated by the parse_recent_matches function in src/tracker/parser_matches.py, which extracts raw metadata and statistics from external API responses and maps them into typed fields. The class relies on two nested models: MatchHero for hero-specific metadata and MatchRankSnapshot for rank-related context, both of which are populated during the parsing phase. Once constructed, MatchListEntry instances are distributed across multiple feature modules. In the rating system (src/features/feels/embed.py and src/features/feels/view.py), they provide the necessary context to generate Discord embeds for match rating prompts, saved ratings, and raw data snapshots, as well as to construct interactive views and persist user feedback records via build_feels_record. In the match detail module (src/features/match/embed.py), they supply formatted values for display fields, played timestamps, and fallback embeds when detailed scoreboards are unavailable. Additionally, MatchListEntry objects are aggregated within MatchBundle to manage collections of matches per user and season, and are processed by build_rating_chart to extract rating points and timestamps for performance graphing. This architecture ensures that raw parsed data is consistently transformed into a unified representation before being consumed by UI rendering, persistence, or analytics components.
**Note**: Several attributes (played_at, season_id) are optional and default to None; consumers must implement null checks before accessing or formatting these values. The statistical fields (kills, deaths, assists, kda_ratio) are typed as strings rather than integers, indicating they may contain formatted placeholders or localized text; numeric operations require explicit parsing. Direct instantiation of this class outside the designated parser functions should be avoided unless constructing test fixtures or mock data. When accessing nested attributes like hero.name or rank.rs, downstream code should verify that the nested objects are properly initialized to prevent runtime errors, as they are expected to be present in production workflows but may lack validation in edge cases.
## ClassDef MatchBundle
**MatchBundle**: The function of MatchBundle is to serve as a unified data container that aggregates a user's season context, lightweight match previews, and preloaded detailed match information for efficient downstream processing and UI rendering.
**attributes**: The attributes of this Class.
· username: str - The tracked player's username on the external service.
· season_id: int - The identifier for the competitive season associated with the fetched data.
· entries: list[MatchListEntry] - A collection of structured match summaries used for list views and quick previews.
· details: dict[str, MatchDetail] - A dictionary mapping match IDs to fully parsed detailed match objects containing scoreboard and team data.
· details_raw: dict[str, dict[str, Any]] - A dictionary mapping match IDs to their original raw JSON payloads, defaulting to an empty dictionary.
**Code Description**: This class functions as an aggregate root and data transfer object within the tracker module, bridging the scraping layer and the feature/UI layer. It is instantiated by the `_bundle_from_raw` method in `TrackerScraper`, which processes raw API responses to populate match previews via `parse_recent_matches` and detailed scoreboards via `parse_match_detail`. The resulting `MatchBundle` is returned by `fetch_match_bundle` and utilized across multiple downstream components. In the rating feature, it supplies season context and entry lists to `build_feels_overview_embed` for generating overview displays, while `build_feels_record` and `_build_raw_snapshot` extract specific match data and raw payloads to construct user feedback records. In the match picker feature, it provides the entry list and username to `build_match_picker_embed` and initializes `MatchPickerView` with interactive options. The separation of `entries` (optimized for iteration) and `details` (optimized for lookup by match ID) ensures efficient memory usage and rapid access patterns for both list rendering and detailed scoreboard generation.
**Note**: The `details_raw` attribute relies on `field(default_factory=dict)` to prevent mutable default argument pitfalls, ensuring each instance maintains an independent dictionary. Consumers accessing `details` or `details_raw` should verify key existence using `match_id` before retrieval, as not all entries may have corresponding detailed data available in the cache or API response. The `entries` list and `details` dictionary are populated during the scraping phase; direct modification of these collections post-instantiation is discouraged to maintain data consistency across UI components and caching mechanisms. Type annotations enforce strict typing, requiring downstream code to handle potential missing keys gracefully when mapping match previews to their corresponding detailed objects.
## ClassDef PlayerProfile
**PlayerProfile**: The function of PlayerProfile is to serve as a comprehensive data model that aggregates and structures all statistical, ranking, and metadata information for a specific player's game profile.

**attributes**: The attributes of this Class.
· username: str - The player's unique identifier or display name.
· avatar_url: str | None - Optional URL pointing to the player's avatar image.
· profile_url: str - The direct link to the player's external profile page.
· season_id: int - The numerical identifier for the current game season.
· season_name: str - The display name of the current season.
· matches_played: str - The total number of matches played, formatted as a string.
· time_played: str - The cumulative playtime, formatted as a string.
· current_rank: RankInfo | None - Optional structured data representing the player's active competitive rank.
· season_peak: RankInfo | None - Optional structured data for the highest rank achieved in the current season.
· lifetime_peak: RankInfo | None - Optional structured data for the highest rank achieved across all seasons.
· season_peaks: list[RankInfo] - A list of historical peak ranks achieved during previous seasons.
· kda: StatValue | None - Optional Kill/Death/Assist ratio with an optional percentile ranking.
· win_pct: StatValue | None - Optional win percentage with an optional percentile ranking.
· wins: StatValue | None - Optional total win count with an optional percentile ranking.
· mvp_pct: StatValue | None - Optional Most Valuable Player percentage with an optional percentile ranking.
· kd_ratio: str | None - Optional raw or formatted Kill/Death ratio string.
· kills: str | None - Optional total kill count string.
· deaths: str | None - Optional total death count string.
· assists: str | None - Optional total assist count string.
· last_kills: str | None - Optional recent kill metric string.
· svp_pct: str | None - Optional Second Most Valuable Player percentage string.
· damage: str | None - Optional total damage dealt string.
· healing: str | None - Optional total healing provided string.
· damage_blocked: str | None - Optional total damage blocked or mitigated string.
· max_kill_streak: str | None - Optional longest consecutive kill streak string.
· mvps: str | None - Optional total MVP count string.
· svps: StatValue | None - Optional Second Most Valuable Player count with an optional percentile ranking.
· roles: list[RoleStats] - A list of aggregated performance statistics for each played role.
· top_heroes: list[HeroStats] - A list of the player's most frequently or successfully played heroes, typically limited to the top three.
· embed_color: int | None - Optional integer representation of a hexadecimal color code derived from the current rank, used for UI styling.
· rating_chart: list[RatingChartPoint] - A chronological list of data points tracking the player's rating progression over time.
· rating_chart_delta: int | None - The net change in rating score across the tracked chart period.

**Code Description**: The PlayerProfile class functions as the central aggregation container within the tracker module, bridging raw API data ingestion and downstream presentation layers. It is primarily instantiated and populated by the parse_profile function in src/tracker/parser.py, which extracts metadata, combat statistics, rank information, and role/hero performance from structured API responses. The parser maps external data fields to corresponding attributes, utilizing helper classes such as StatValue for metrics requiring percentile context (kda, win_pct, wins, mvp_pct, svps), RankInfo for competitive tier details (current_rank, season_peak, lifetime_peak, season_peaks), RoleStats and HeroStats for aggregated gameplay statistics, and RatingChartPoint for historical rating tracking. Following initial population, the apply_rating_chart function in src/tracker/parser_matches.py appends chronological match data to the rating_chart list and calculates the net delta for rating_chart_delta. Downstream consumers rely heavily on this model for UI generation. The build_stats_embed function in src/features/stats/embed.py consumes nearly all attributes to construct a multi-section Discord embed, dynamically routing StatValue instances to percentile badge generators, RankInfo objects to rank formatting utilities, and string-based statistics to combat/impact/honors fields. The rating_chart and rating_chart_delta fields are processed by _rating_chart_summary to generate progression text, while basic identifiers like username and profile_url are utilized in build_register_success_embed for account linking confirmations. The embed_color attribute is derived from the current rank's color field to maintain visual consistency across generated interfaces.

**Note**: Points to note about the use of the code
- All statistical metrics typed as str (e.g., kd_ratio, kills, damage) are pre-formatted for direct display and should not be parsed for mathematical operations without explicit conversion.
- Attributes utilizing StatValue carry an optional percentile field; downstream UI components must implement null checks before accessing or rendering percentile badges to prevent runtime errors.
- Rank-related attributes (current_rank, season_peak, lifetime_peak) are optional and may contain None values if the player has not participated in rated matches; consumers must validate their presence before accessing nested fields like tier_name or rs.
- The roles and top_heroes lists are populated during parsing with strict filtering criteria (e.g., excluding heroes with fewer than 0.5 matches played); these collections should be treated as read-only data carriers for UI iteration.
- The rating_chart list may be empty if no match history is available; chart rendering functions expect non-empty sequences and will raise errors if passed an empty list without prior validation.
- The class contains no business logic, validation methods, or serialization routines; it strictly enforces type consistency to ensure seamless data flow between the parser module and the embed generation pipeline.
