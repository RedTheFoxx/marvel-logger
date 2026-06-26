## FunctionDef _segment(segments, seg_type, season, mode)
**_segment**: The function of _segment is to locate and return a specific data segment dictionary from a list based on its type, season, and mode attributes, or return None if no match is found.
**parameters**: The parameters of this Function.
· segments: A list of dictionaries containing raw segment data retrieved from an API response.
· seg_type: A string specifying the exact type identifier to filter by (e.g., "overview" or "ranked-peaks").
· season: An integer representing the target season ID that must match the segment's attributes.
· mode: A string indicating the game mode to match within the segment's attributes, defaulting to "all".
**Code Description**: The function iterates sequentially through the provided list of segment dictionaries. For each item, it first verifies if the dictionary's "type" key matches the provided seg_type parameter. If the type does not match, the iteration continues to the next item. When a matching type is found, the function applies conditional logic based on the seg_type value. Specifically, if seg_type is exactly "ranked-peaks", the function immediately returns the current segment without further attribute validation. For all other types, it extracts the "attributes" dictionary (defaulting to an empty dictionary if missing) and checks whether both the "season" and "mode" keys match the provided season and mode parameters respectively. If both attributes align, the matching segment is returned. If the loop completes without finding a valid match, the function returns None. Within the project, this utility is exclusively utilized by the parse_profile function to extract critical data blocks from the raw API payload. It isolates the "overview" segment for current season statistics and the "ranked-peaks" segment for historical peak data, which are subsequently processed by helper functions like _stat and _rank_from_stat to populate the final PlayerProfile object.
**Note**: Points to note about the use of the code
- The function relies on exact string matching for the "type" field, so incorrect seg_type values will result in a None return.
- The special handling for "ranked-peaks" bypasses season and mode checks, which means it returns the first encountered segment of that type regardless of its attributes.
- Missing or null "attributes" keys are safely handled by defaulting to an empty dictionary, preventing KeyError exceptions during attribute lookup.
**Output Example**: Mock up a possible appearance of the code's return value.
{
  "type": "overview",
  "attributes": {
    "season": 1234567890,
    "mode": "all"
  },
  "metadata": { ... },
  "value": [ ... ]
}
## FunctionDef _stat(segment, key)
**_stat**: The function of _stat is safely extracting a specific statistic value from a nested dictionary structure while handling potential None values to prevent runtime errors.
**parameters**: The parameters of this Function.
· segment: A dictionary representing a data segment, or None. It is expected to contain a "stats" key mapping to another dictionary.
· key: A string representing the name of the specific statistic to retrieve from the nested stats dictionary.
**Code Description**: The description of this Function.
This function implements a null-safe accessor for deeply nested configuration or data dictionaries. It first evaluates the segment parameter; if it is None or falsy, the function immediately returns None. If the segment exists, it safely retrieves the "stats" dictionary using the .get() method, defaulting to an empty dictionary if the key is absent or evaluates to None. It then performs a second safe lookup for the specified key within that stats dictionary and returns the resulting value. Within the project architecture, _stat acts as a core utility for data parsing. It is uniformly called by internal helper functions such as _combat_line and _hero_record, as well as the primary parse_profile function. These callers rely on _stat to fetch raw statistical objects related to combat metrics (kills, deaths, assists), match outcomes (matchesWon, matchesPlayed), and ranking tiers without risking KeyError or AttributeError exceptions. By centralizing this access pattern, the parser module maintains clean caller logic while ensuring robust handling of incomplete or malformed API responses.
**Note**: Points to note about the use of the code
The function strictly returns raw dictionary objects or None; it does not perform type conversion, validation, or formatting. Callers must explicitly check for None before accessing nested attributes such as .get("value") or .get("metadata"). The segment parameter must conform to an internal schema where the "stats" key maps to a dictionary of statistic entries. If the API response structure changes, this function will silently return None rather than raising an exception, which requires callers to implement appropriate fallback logic.
**Output Example**: Mock up a possible appearance of the code's return value.
{
    "value": 1500,
    "metadata": {
        "seasonShortName": "S3"
    }
}
## FunctionDef _display(stat)
**_display**: The function of _display is to extract a formatted or fallback string representation from a statistical data dictionary.
**parameters**: 
· stat: A dictionary containing statistical data, potentially including keys like "displayValue" and "value", or None if no data is available.
**Code Description**: This utility function processes a raw statistical dictionary to produce a consistent string output suitable for display purposes. It first checks if the input stat is valid; if it is falsy (None or empty), it immediately returns None. If the dictionary contains a "displayValue" key with a truthy value, that value is returned directly. Otherwise, it falls back to retrieving the "value" key and converting it to a string, defaulting to an empty string if the key is absent. This function serves as a standardized extraction layer across the tracker module, used by _stat_value, _rank_from_stat, _combat_line, and parse_profile to safely retrieve formatted metrics such as rank scores, combat statistics (kills/deaths/assists), win percentages, damage totals, and time played without repeatedly handling dictionary key existence checks or type conversions.
**Note**: The function relies on the presence of either "displayValue" or "value" keys in the input dictionary. If both are missing or falsy, it returns an empty string via the fallback mechanism. Callers should be aware that numeric values will be converted to strings, and no additional formatting (like percentage signs or thousand separators) is applied internally; such formatting must be handled by the caller if required.
**Output Example**: "2,450" (when stat contains {"displayValue": "2,450"}), "15.7" (when stat contains {"value": 15.7}), or None (when stat is None).
## FunctionDef _percentile(stat)
**_percentile**: The function of _percentile is to safely extract and convert the percentile metric from a statistical dictionary into a floating-point number, returning None when the input or data is unavailable.
**parameters**: The parameters of this Function.
· stat: A dictionary containing statistical metrics or None.
**Code Description**: This function accepts an optional dictionary named `stat` as its sole argument. It first evaluates the truthiness of `stat`; if the dictionary is empty, falsy, or explicitly None, the function immediately returns None. When a valid dictionary is provided, it attempts to retrieve the value associated with the key "percentile" using the `.get()` method. If this key exists and its value is not None, the function casts the retrieved value to a float and returns it. Otherwise, it returns None. Within the project structure, this function serves as a helper utility for `_stat_value`. The caller `_stat_value` invokes `_percentile(stat)` to populate the `percentile` attribute of a `StatValue` instance. This design ensures that statistical data processing remains consistent and prevents type errors by centralizing the extraction and conversion logic for percentile metrics before they are assigned to structured data objects.
**Note**: The input dictionary must contain a numeric value under the "percentile" key to yield a non-None result. If the value exists but is not a valid numeric type, a TypeError will be raised during the float conversion. The function gracefully handles missing keys and None inputs without raising exceptions.
**Output Example**: 0.85
## FunctionDef _stat_value(stat)
**_stat_value**: The function of _stat_value is to safely transform a raw statistical dictionary into a structured StatValue object containing display text and an optional percentile rank, or return None if the input data is invalid or missing.
**parameters**: The parameters of this Function.
· stat: A dictionary containing raw statistical metrics (potentially including keys like "displayValue", "value", and "percentile") or None.
**Code Description**: This function acts as a validation and transformation layer for statistical data within the tracker module. It first verifies that the input `stat` dictionary is not empty or None; if it is, the function immediately returns None to prevent downstream errors. Upon receiving valid input, it delegates string extraction to `_display`, which retrieves either a pre-formatted "displayValue" or converts a raw numeric "value" into a string. If this display extraction yields an empty or falsy result, the function short-circuits and returns None. When both conditions pass, it invokes `_percentile` to safely extract and cast the percentile metric from the same dictionary to a float (or None). Finally, it instantiates and returns a `StatValue` object populated with the extracted display string and percentile value. Within the project architecture, this function is exclusively called by `parse_profile` in `src/tracker/parser.py`. The caller passes raw stat dictionaries retrieved via `_stat(overview, "metric_name")` for metrics such as kdaRatio, matchesWinPct, matchesWon, totalMvpPct, and totalSvp. This design centralizes data validation and formatting logic, ensuring that optional profile fields receive consistently structured objects or None values without requiring repetitive error handling in the main parsing routine.
**Note**: The function strictly requires a non-empty dictionary with at least one valid display source ("displayValue" or "value") to produce a `StatValue` instance. If the input dictionary exists but lacks these keys, or if they evaluate to falsy values, the function will return None rather than an object with empty strings. Developers consuming the output must account for the possibility of None and handle the optional percentile field appropriately before performing numerical comparisons.
**Output Example**: StatValue(display="24.5", percentile=87.3) or None
## FunctionDef _rank_from_stat(stat, season_label)
**_rank_from_stat**: The function of _rank_from_stat is to parse a raw statistical dictionary containing rank metadata and convert it into a structured RankInfo object representing a player's competitive tier, rating score, and seasonal context.
**parameters**: 
· stat: A dictionary containing rank-related data, potentially including a "metadata" sub-dictionary with tier identifiers and visual assets, or None if no data is available.
· season_label: An optional string providing explicit seasonal context; if omitted, the function attempts to derive it from the stat's metadata fields.
**Code Description**: This utility function processes a raw statistical dictionary to produce a structured RankInfo instance suitable for profile display and styling. It first validates the input stat; if stat is None or empty, it returns None immediately. The function extracts the tier identifier using a strict fallback chain: it checks stat.metadata.tierName first, then falls back to stat.displayName, defaulting to an empty string. If the resulting tier string is empty, the function returns None to indicate invalid rank data. Next, it retrieves the rating score by calling _display(stat), which safely extracts either a pre-formatted displayValue or converts a numeric value to a string, defaulting to an empty string if neither exists. Finally, it instantiates and returns a RankInfo object, mapping tier_name to the resolved tier string, tier_short to metadata.tierShortName (or tier_name as fallback), rs to the formatted rating score, and optionally passing icon_url and color from metadata. The season_label field prioritizes the explicit function parameter, then falls back to metadata.seasonShortName or metadata.seasonName. Functionally, this parser is invoked by parse_profile to extract current_rank, season_peak, and lifetime_peak data from raw API responses. It bridges unstructured dictionary payloads into a consistent model format that downstream components consume for embedding generation, color extraction, and profile rendering without duplicating fallback logic.
**Note**: Points to note about the use of the code
- The function returns None if stat is falsy or lacks a valid tier identifier, requiring callers to handle potential None values before accessing RankInfo attributes.
- Fallback mechanisms guarantee that tier_name and tier_short are never empty strings in the returned object, but icon_url and color may remain None if the source metadata omits them.
- The rs attribute is explicitly typed as a string due to _display handling; callers should expect pre-formatted rating scores rather than raw numeric types.
- season_label resolution follows a strict priority order: explicit parameter > metadata.seasonShortName > metadata.seasonName, ensuring consistent seasonal context across different API response formats.
**Output Example**: RankInfo(tier_name="Gold", tier_short="GOLD", rs="2,450", icon_url="https://example.com/icon.png", color="#FFA500", season_label="Season 12")
## FunctionDef _rank_from_peak_entry(entry)
**_rank_from_peak_entry**: The function of _rank_from_peak_entry is to parse a single dictionary entry representing a peak competitive rank and convert it into a structured RankInfo object, or return None if critical tier information is missing.
**parameters**: The parameters of this Function.
· entry: dict[str, Any] - A dictionary containing metadata and numerical/string values for a specific peak rank tier.
**Code Description**: This function extracts competitive ranking details from a raw data entry typically sourced from an API response or profile statistics payload. It first isolates the metadata dictionary and validates the presence of a tier name; if absent, it safely returns None to prevent downstream errors. The function then processes the associated value field, formatting numeric ratings as comma-separated strings while preserving non-numeric values as-is. Finally, it instantiates a RankInfo object by mapping source keys such as tierName, tierShortName, iconUrl, color, and seasonal identifiers directly to the corresponding model attributes. Within the project architecture, this parser is invoked exclusively by parse_profile during the processing of peak tier statistics. It iterates through up to four tier entries, filters out invalid data, and populates the season_peaks list within the PlayerProfile model. The resulting RankInfo instances are subsequently utilized by downstream presentation layers to render formatted rank displays, bridging raw data ingestion with structured profile storage and UI rendering without implementing validation or business logic itself.
**Note**: Points to note about the use of the code
- The function strictly requires a valid tierName within the entry's metadata; otherwise, it returns None, acting as a built-in filter for incomplete rank data.
- Numeric values are explicitly cast to integers and formatted with thousand separators before being stored in the rs attribute, ensuring consistent string representation across the application.
- Optional fields like icon_url, color, and season_label may remain None if the source entry lacks corresponding metadata keys; downstream consumers must handle these potential None values appropriately.
- The function operates as a pure data transformer with no side effects, relying entirely on external formatting rules and model definitions provided by RankInfo.
**Output Example**: Mock up a possible appearance of the code's return value.
RankInfo(
    tier_name="Grandmaster",
    tier_short="GM",
    rs="10,500",
    icon_url="https://example.com/icons/gm.png",
    color="#FF4500",
    season_label="Season 8"
)
## FunctionDef _combat_line(segment)
**_combat_line**: The function of _combat_line is safely extracting and formatting kills, deaths, and assists statistics from a given data segment while providing a default fallback value.
**parameters**: The parameters of this Function.
· segment: A dictionary representing a data segment containing statistical information, or None. It is expected to follow an internal schema where nested "stats" dictionaries hold combat metrics.
**Code Description**: This utility function processes a raw data segment to extract three core combat metrics: kills, deaths, and assists. It leverages the _stat helper to safely navigate the nested dictionary structure and retrieve the raw statistical objects for each metric. The output of _stat is then passed to _display, which converts the raw data into a consistent string representation suitable for UI rendering. If any of these formatted values are falsy (e.g., None or an empty string), the function explicitly substitutes them with the string "0" to ensure predictable output. Finally, it returns the three processed values as a tuple (kills, deaths, assists). Within the project architecture, _combat_line acts as a standardized extraction layer for combat data. It is primarily invoked by parse_profile during the parsing of hero and role segments. By centralizing the retrieval, formatting, and fallback logic for these specific metrics, it prevents repetitive null-checking in the caller and guarantees that combat statistics are always presented as valid strings, even when underlying API responses are incomplete or malformed.
**Note**: The function strictly relies on the internal schema of the segment parameter, specifically expecting a "stats" key that maps to a dictionary containing "kills", "deaths", and "assists" entries. Callers must ensure that the segment data conforms to this structure before invocation. The fallback mechanism guarantees that the returned tuple never contains None or empty strings, which is critical for downstream UI components that expect string inputs. If the API response structure changes or omits these keys, the function will silently default to "0" rather than raising an exception, requiring upstream validation if strict data integrity is needed.
**Output Example**: ("15", "8", "23") (when segment contains valid kill/death/assist statistics), ("0", "0", "0") (when segment is None or lacks the required statistical keys).
## FunctionDef _hero_record(segment)
**_hero_record**: The function of _hero_record is extracting match win and loss statistics from a provided data segment and formatting them into a concise "XW / YL" string representation.
**parameters**: The parameters of this Function.
· segment: A dictionary or None representing a specific game data segment. It is expected to contain nested statistical data under a "stats" key, specifically tracking "matchesWon" and "matchesPlayed".
**Code Description**: This function processes raw match outcome statistics within a given segment to compute and format a hero's win-loss record. It first invokes the _stat utility to safely retrieve the raw dictionary objects for "matchesWon" and "matchesPlayed". If either statistic is unavailable or evaluates to None, the function immediately returns a placeholder dash ("—"). When both values are present, it extracts their numeric value fields, converting them to integers. The played count undergoes rounding via float() and round() before integer conversion to handle potential floating-point precision artifacts from the source API. Losses are calculated by subtracting wins from played matches, with a max(..., 0) safeguard ensuring non-negative results in edge cases where played counts might be lower than wins due to rounding or data inconsistencies. Finally, it returns a formatted string combining the win and loss counts. Within the project architecture, _hero_record serves as a specialized formatting helper called exclusively by parse_profile. During profile parsing, parse_profile iterates through hero-specific segments, invokes _hero_record(seg) to generate the record field for each HeroStats instance, and subsequently sorts these heroes by playtime. The function relies entirely on _stat for null-safe data extraction, ensuring that incomplete or malformed API responses do not trigger runtime exceptions during profile generation.
**Note**: Points to note about the use of the code
The function strictly expects the segment parameter to conform to the internal schema where statistical entries contain a value field. It does not validate whether matchesWon can logically exceed matchesPlayed; instead, it defensively clamps losses to zero. Callers must ensure that the segment data originates from a valid hero-type API response. The function returns a string and should be used directly in UI rendering or data serialization pipelines without further parsing.
**Output Example**: Mock up a possible appearance of the code's return value.
"12W / 8L"
## FunctionDef parse_profile(raw, username)
**parse_profile**: The function of parse_profile is to extract, process, and structure raw API response data into a comprehensive PlayerProfile object containing ranked statistics, combat metrics, role performance, and hero-specific gameplay data.

**parameters**: The parameters of this Function.
· raw: A dictionary representing the raw API response payload, expected to contain nested keys such as "data", "metadata", "segments", and "platformInfo".
· username: A string representing the player's account name, used as a fallback value for the platform handle if the API response lacks it.

**Code Description**: This function serves as the central data transformation layer within the tracker module, converting unstructured JSON-like API responses into a strongly typed PlayerProfile model. It begins by resolving the active season identifier and name from the metadata dictionary. Using the _segment utility, it isolates the "overview" segment for current-season statistics and the "ranked-peaks" segment for historical peak data. Platform information is extracted to determine the player's handle, defaulting to the provided username parameter if unavailable.

The function systematically processes competitive ranking data by invoking _stat to retrieve raw stat dictionaries, which are then passed to _rank_from_stat or _rank_from_peak_entry to construct RankInfo instances for current_rank, season_peak, lifetime_peak, and season_peaks. Combat and match statistics are aggregated using _display and _stat_value helpers, which safely extract formatted strings or StatValue objects containing optional percentile data.

Role-specific performance metrics are collected by iterating through segments filtered by type "hero-role" that match the current season and mode. For each valid segment, _combat_line extracts kills, deaths, and assists, while other stats populate a RoleStats instance. Similarly, hero-specific statistics are gathered from segments of type "hero". The parser filters out heroes with fewer than 0.5 matches played, calculates win-loss records via _hero_record, and sorts the remaining entries by matches_played in descending order to identify the top three most frequently played heroes.

Finally, the function derives an embed_color integer from the current rank's hexadecimal color code for UI styling consistency. All processed data is mapped to the corresponding attributes of a PlayerProfile instance, which is returned to the caller. Within the project architecture, this function is exclusively invoked by TrackerScraper.fetch_profile in src/tracker/client.py, acting as the bridge between network data retrieval and downstream embed generation or database storage pipelines.

**Note**: Points to note about the use of the code
- The raw parameter must conform to an internal API schema containing "data", "segments", and "platformInfo" keys; missing keys will result in None values or empty collections rather than exceptions due to extensive use of .get() and fallback logic.
- All statistical metrics stored as strings (e.g., kd_ratio, kills, win_pct) are pre-formatted for direct UI consumption and should not be used in arithmetic operations without explicit type conversion.
- Rank-related attributes (current_rank, season_peak, lifetime_peak) are optional and may evaluate to None if the player has no competitive history; downstream consumers must implement null checks before accessing nested fields like tier_name or rs.
- The roles and top_heroes lists are strictly filtered during parsing; heroes with matches_played below 0.5 are excluded, and only the top three by playtime are retained to optimize memory usage and UI rendering.
- The function relies on external helper utilities for data extraction and formatting; it contains no business logic or validation routines itself, adhering to a pure data mapping pattern.

**Output Example**: Mock up a possible appearance of the code's return value.
PlayerProfile(
    username="ShadowStrike",
    avatar_url="https://cdn.example.com/avatars/123.png",
    profile_url="https://tracker.gg/overwatch/profile/pc/shadowstrike?season=14",
    season_id=14,
    season_name="Season 14",
    matches_played="1,245",
    time_played="18d 4h 32m",
    current_rank=RankInfo(tier_name="Gold", tier_short="GOLD", rs="2,450", icon_url="https://cdn.example.com/ranks/gold.png", color="#FFA500", season_label="Season 14"),
    season_peak=RankInfo(tier_name="Platinum", tier_short="PLAT", rs="3,100", icon_url=None, color="#87CEEB", season_label="Season 12"),
    lifetime_peak=RankInfo(tier_name="Diamond", tier_short="DIAM", rs="4,200", icon_url=None, color="#9370DB", season_label="Season 8"),
    season_peaks=[RankInfo(...), RankInfo(...)],
    kda=StatValue(display="2.45", percentile=78.3),
    win_pct=StatValue(display="54.2%", percentile=65.1),
    wins=StatValue(display="675", percentile=None),
    mvp_pct=StatValue(display="12.4%", percentile=None),
    kd_ratio="1.89",
    kills="3,420",
    deaths="1,810",
    assists="4,150",
    last_kills="12",
    svp_pct="8.7%",
    damage="1,245,600",
    healing="890,300",
    damage_blocked="450,200",
    max_kill_streak="15",
    mvps="154",
    svps=StatValue(display="89", percentile=None),
    roles=[RoleStats(...)],
    top_heroes=[HeroStats(...), HeroStats(...), HeroStats(...)],
    embed_color=16753920,
    rating_chart=[],
    rating_chart_delta=None
)
