## FunctionDef _add_section_separator(embed)
**_add_section_separator**: The function of _add_section_separator is to insert a full-width visual divider into a Discord Embed object to separate distinct statistical sections.
**parameters**: The parameters of this Function.
· embed: A discord.Embed instance representing the message embed being constructed.
**Code Description**: The description of this Function.
This function appends a single field to the provided Discord Embed object using two module-level constants, `_BLANK` and `_SECTION_SEPARATOR`. By setting the `inline` parameter to `False`, the field is forced to occupy the entire horizontal width of the embed, effectively creating vertical whitespace that visually partitions the content. Within the project architecture, this function is exclusively invoked by `build_stats_embed`. It serves as a structural utility that is called conditionally before rendering major data categories such as Rank information, Combat and Impact metrics, Role statistics, Top Heroes podiums, and Rating Chart summaries. This ensures that the final player profile embed maintains a clean, organized layout without cluttering adjacent fields or exceeding Discord's inline field constraints.
**Note**: Points to note about the use of the code
The function relies on external constants `_BLANK` and `_SECTION_SEPARATOR` which must be defined in the same module for execution to succeed. It modifies the embed object in-place and does not return a value. Ensure that the separator constant renders appropriately within Discord's formatting rules, as excessive use may impact embed layout constraints or field limits. Always verify that the visual spacing aligns with the intended readability goals when integrating this utility into other embed-building workflows.
## FunctionDef _role_emoji(name)
**_role_emoji**: The function of _role_emoji is to map a given role name string to a corresponding Discord emoji, defaulting to a game controller icon if no specific mapping exists.
**parameters**: 
· name: A string representing the name of the game role. The function automatically trims leading and trailing whitespace and converts the string to lowercase before performing the lookup.
**Code Description**: This function operates as a deterministic lookup utility that translates textual role identifiers into visual emoji representations for UI display. It normalizes the input `name` by stripping whitespace and converting it to lowercase, then queries an internal dictionary named `_ROLE_EMOJIS`. If the normalized key exists within the dictionary, the associated emoji string is returned. If the key is absent, the function safely returns a fallback game controller emoji ("🎮"). Within the project architecture, this function is exclusively utilized by `build_stats_embed` to format the roles section of a player statistics Discord embed. Specifically, it is invoked inside a loop that iterates through up to three primary roles from a player profile. The returned emoji is concatenated with the role name to construct the field name for each inline embed field, ensuring consistent visual categorization across different player profiles and game updates.
**Note**: The function depends on the `_ROLE_EMOJIS` dictionary being properly initialized elsewhere in the module. Callers do not need to pre-process the input string, as case normalization and whitespace trimming are handled internally. The fallback mechanism guarantees that the Discord embed layout remains intact and visually consistent even when encountering unmapped, deprecated, or newly introduced role names.
**Output Example**: "🛡️" (for an input like "Tank"), "⚔️" (for an input like "DPS"), or "🎮" (for an unknown role name such as "NewRole").
## FunctionDef _percentile_badge(stat)
**_percentile_badge**: The function of _percentile_badge is to generate a formatted inline percentile badge string for Discord embeds based on the provided statistical value.
**parameters**: The parameters of this Function.
· stat: An optional StatValue object containing the display text and an optional percentile rank used to determine the badge content.
**Code Description**: This function processes a StatValue instance to produce a concise, visually contextualized string representing a player's performance percentile relative to a distribution. It first validates the input by checking if the stat parameter is None or if its percentile attribute lacks a value; in either case, it returns an empty string to prevent formatting errors downstream. When valid data is present, it extracts the numeric percentile and applies a threshold logic: values greater than 50 indicate top-tier performance, so it calculates the inverse percentage (100.0 - p) and prefixes the result with Top. Values less than or equal to 50 indicate lower-tier performance and are prefixed with Bottom. The output string begins with \n-#, which is Discord's markdown syntax for rendering small italicized text on a new line, ensuring the badge appears directly beneath the primary statistic without disrupting the embed layout. This function is exclusively called by build_stats_embed within the same module to dynamically append contextual rankings to key performance metrics such as KDA Ratio, Win Percentage, and total Wins. By relying on the StatValue.percentile field, it maintains a clear separation between data parsing (handled in the tracker module) and UI rendering logic, ensuring that statistical data remains decoupled from raw extraction while providing consistent embed generation.
**Note**: Developers should ensure that the percentile attribute within the StatValue object is properly populated before invoking this function, as missing or invalid percentile data will result in an empty string output. The function assumes a 0-100 scale for percentiles where higher values denote better performance relative to a distribution. The \n-# prefix is strictly tied to Discord embed formatting and should not be modified if the output is intended for Discord clients. When integrating this function into other components, verify that the calling object passes a valid StatValue instance to avoid silent failures in badge rendering.
**Output Example**: 
For a stat with percentile = 95.8, the function returns:
\n-# Top 4.2%
For a stat with percentile = 32.1, the function returns:
\n-# Bottom 32.1%
## FunctionDef _rank_line(rank)
**_rank_line**: The function of _rank_line is to format a RankInfo object into a concise, Discord-compatible string representation of a player's competitive rank, optionally including the rating score and seasonal context.

**parameters**: The parameters of this Function.
· rank: RankInfo - A structured data model containing rank metadata such as tier_name, rs (rating score), and season_label.
· with_season: bool - A keyword-only boolean flag that determines whether the seasonal label should be appended to the output string. Defaults to False.

**Code Description**: The _rank_line function constructs a formatted text string designed for direct insertion into Discord embed fields. It initializes a list containing the player's tier name wrapped in bold Markdown syntax. If the rank object contains a truthy rs attribute, it appends the rating score followed by " RS" to the list. These components are joined using a middle dot separator ( · ) to form the primary rank line. When the with_season parameter is explicitly True and the rank object provides a valid season_label, the function appends a Discord caption-style line break and italicized text containing the seasonal identifier. This function operates as a dedicated presentation utility within src/features/stats/embed.py, directly consuming RankInfo instances that have been populated by the tracker parser layer. It is invoked by build_stats_embed to render rank data across multiple embed fields: current rank, season peak, and lifetime peak. The with_season flag is conditionally passed based on the specific rank context, ensuring that seasonal metadata is only displayed where relevant (e.g., lifetime peak). The function relies entirely on the RankInfo model for data access and does not implement validation or fallback logic, assuming downstream parsers have already guaranteed valid tier_name values.

**Note**: Points to note about the use of the code
- The function expects rank.tier_name to always be a non-empty string, as parser guarantees ensure this field is never null.
- The rs attribute is treated as an optional string; if it evaluates to False (e.g., empty string or None), it will be omitted from the output.
- The season_label is only appended when with_season is explicitly True and the attribute exists on the RankInfo instance.
- The output uses Discord Markdown formatting (** for bold, -# for caption/italicized text), making it directly compatible with discord.py Embed field values.
- As a private utility function (indicated by the leading underscore), it is not intended for direct external import and should only be used within the stats embed generation module.

**Output Example**: Mock up a possible appearance of the code's return value.
**Grandmaster** · 5200 RS
-# Season 3
## FunctionDef _rating_chart_summary(profile)
**_rating_chart_summary**: The function of _rating_chart_summary is to generate a concise, formatted text summary of a player's rating progression and current competitive standing based on their profile data.
**parameters**: The parameters of this Function.
· profile: PlayerProfile - The comprehensive data model containing the player's match history, rating chart points, rating delta, and current rank information.
**Code Description**: This function constructs a single-line string that aggregates key rating metrics from the provided PlayerProfile instance. It begins by calculating the total number of rated matches tracked in the profile.rating_chart list. It then evaluates the profile.rating_chart_delta attribute to determine the net change in rating score, appending an appropriate directional emoji and formatted value for positive, negative, or zero changes. Finally, it checks for the presence of a current rank and its associated RS (Rating Score) value, appending it if available. All collected metrics are concatenated using a bullet separator and returned as a plain string. Within the project architecture, this function is exclusively invoked by build_stats_embed when rendering the rating progression section of a Discord embed. It acts as a presentation-layer utility that transforms raw numerical data from the PlayerProfile model into a visually structured summary compatible with Discord's formatting rules, directly preceding the attachment of a visual chart image. The function relies on the rating_chart list for match count, rating_chart_delta for trend direction, and current_rank.rs for the active competitive score.
**Note**: Points to note about the use of the code
- The function assumes profile.rating_chart supports len(); it does not validate whether the list is empty before calculating its length.
- The rating_chart_delta attribute may be None; the function safely handles this by skipping delta formatting if the value is absent.
- The current_rank.rs field access requires explicit null checks on both profile.current_rank and profile.current_rank.rs to prevent AttributeError or TypeError during runtime.
- The output string uses Discord-compatible markdown (bold syntax) and emoji characters, making it suitable for direct embedding in chat applications but not intended for programmatic parsing.
- The function is a private utility (indicated by the leading underscore) and should not be called directly by external modules; it is strictly bound to the embed generation pipeline.
**Output Example**: Mock up a possible appearance of the code's return value.
📈 **42** parties classées · 🔺 **+150 RS** · 🎯 **3850 RS** actuels
## FunctionDef _role_field_value(role)
**_role_field_value**: The function of _role_field_value is to format a RoleStats data object into a structured, multi-line string optimized for display within a Discord embed field.
**parameters**: The parameters of this Function.
· role: RoleStats - An instance containing aggregated performance metrics for a specific player role, including win percentage, total wins, KDA ratio, and kill/death/assist counts.
**Code Description**: This function accepts a single `RoleStats` object and returns a formatted string that organizes the role's key statistics into three distinct lines. The first line displays the win rate (WR) prefixed with a trophy emoji and total wins. The second line shows the Kill/Death/Assist ratio (KDA) with a balance scale emoji. The third line presents the raw combat breakdown (kills / deaths / assists) using Discord's inline text styling prefix `-#`. The function does not perform any data validation, type conversion, or mathematical computation; it strictly maps existing string attributes from the `RoleStats` model to a predefined visual template. It is invoked by the `build_stats_embed` function during the construction of player profile embeds, specifically when iterating through the top three roles in the `profile.roles` collection. The returned string is directly assigned as the `value` parameter for an inline Discord embed field, ensuring consistent styling and layout across all role statistics displayed to the user.
**Note**: Points to note about the use of the code
- All statistical values are passed through as pre-formatted strings from the `RoleStats` model; direct arithmetic operations on these attributes should be avoided without explicit parsing.
- The function assumes the `role` parameter is never `None`; callers must ensure valid `RoleStats` instances are passed to prevent `AttributeError`.
- The `-#` prefix in the final line is a Discord Markdown directive for italicized/gray text, which will render accordingly in the client interface.
- Since this function is tightly coupled with the embed generation pipeline, any changes to its output format must be coordinated with `build_stats_embed` and the `RoleStats` data model to maintain UI consistency across the application.
**Output Example**: Mock up a possible appearance of the code's return value.
🏆 WR **54.2%** · 128 wins
⚖️ KDA **3.45**
-# 412 / 119 / 506
## FunctionDef _hero_field_value(hero)
**_hero_field_value**: The function of _hero_field_value is to format a HeroStats data object into a concise, emoji-prefixed string representation optimized for display within a Discord embed field.

**parameters**: The parameters of this Function.
· hero: HeroStats - An instance containing aggregated performance statistics for a specific game hero, including win rate, match record, KDA ratio, and absolute kill/death/assist counts.

**Code Description**: This function accepts a single HeroStats object and returns a formatted string designed specifically for Discord embed field values. It constructs the output using three distinct lines separated by newline characters. The first line displays the hero's win rate percentage prefixed with a trophy emoji and labeled as WR, followed by the match record (wins-losses-ties). The second line presents the Kill/Death/Assist ratio using a balance scale emoji. The third line provides the absolute kill, death, and assist counts separated by slashes, prefixed with Discord's italic text syntax (-#). All statistical values are directly accessed from the HeroStats attributes, which are pre-formatted as strings during the parsing phase. The function is invoked within the build_stats_embed function when iterating over the top three heroes of a player profile. For each hero, its formatted string is passed as the value argument to embed.add_field(), alongside a field name containing a medal emoji and the hero's display name. This ensures consistent visual presentation across the embed without duplicating formatting logic in the caller.

**Note**: Points to note about the use of the code
- The function relies entirely on string-typed attributes from HeroStats. If any attribute contains placeholder characters like "—" due to missing API data, these will render directly in the output without modification.
- Discord markdown formatting is hardcoded: ** for bold and -# for italic attribution. Ensure downstream consumers do not strip or alter these syntax markers before rendering.
- The function does not perform validation, type conversion, or fallback handling. It assumes the HeroStats instance is fully populated according to the parser's filtering rules (e.g., heroes with fewer than 0.5 matches played are excluded upstream).
- When extending this formatter, maintain compatibility with the existing string-based statistical fields to prevent runtime errors during embed generation.

**Output Example**: Mock up a possible appearance of the code's return value.
🏆 WR **62.5%** · 145-87-3
⚖️ KDA **3.42**
-# 1,204 / 352 / 987
## FunctionDef _pad_inline_row(embed, used)
**_pad_inline_row**: The function of _pad_inline_row is to fill incomplete inline field rows in a Discord embed with blank placeholders to maintain a strict three-column grid layout.
**parameters**: The parameters of this Function.
· embed: A discord.Embed object representing the target embed where fields will be added.
· used: An integer indicating the number of inline fields already present in the current row or group.
**Code Description**: This function calculates the exact number of missing inline fields required to complete a set of three by evaluating the expression `(3 - used % 3) % 3`, which reliably yields 0, 1, or 2 depending on the input. It then iterates that many times, appending invisible placeholder fields (using a predefined `_BLANK` constant for both name and value arguments) to the provided embed object. In the context of `build_stats_embed`, this utility is invoked immediately after populating logical data sections such as key performance metrics, rank information, combat statistics, role data, and top hero achievements. By ensuring each section occupies exactly three columns or fewer without leaving trailing gaps, it prevents Discord's automatic field wrapping from misaligning subsequent content blocks. This guarantees that the next section always begins on a fresh row, preserving a clean, structured visual presentation across varying player data configurations where some fields may be conditionally omitted.
**Note**: Points to note about the use of the code
· The function relies on an external constant `_BLANK` for placeholder text; ensure this is defined in the module scope before calling.
· It modifies the embed object in-place and returns `None`, so it should be called as a standalone statement rather than assigned to a variable.
· The padding logic strictly enforces a modulo-3 alignment, making it unsuitable for layouts requiring different column counts without modification.
· When using this function, always pass the exact count of inline fields added in the preceding block to guarantee accurate spacing and prevent visual misalignment.
## FunctionDef build_stats_embed(profile)
**build_stats_embed**: The function of build_stats_embed is to construct a structured Discord Embed object containing a comprehensive statistical overview and competitive ranking data for a given player profile.

**parameters**: The parameters of this Function.
· profile: PlayerProfile - A data model instance containing aggregated player statistics, rank information, role/hero performance metrics, rating chart progression data, and UI styling attributes.

**Code Description**: This function orchestrates the assembly of a multi-section Discord Embed by iterating through the attributes of the provided PlayerProfile instance. It initializes the embed with dynamic coloring derived from the current rank, author metadata using either a rank icon or avatar URL, and a summary description detailing total matches played and cumulative playtime. The function then conditionally appends inline fields organized into logical sections: Key Performance metrics (KDA Ratio, Win Percentage, Wins), Competitive Rank details (current rank, season peak, lifetime peak, and historical peaks), Combat/Impact/Honors statistics, Top Roles, and Top Heroes. Each section utilizes private utility functions to maintain modular formatting logic. The _percentile_badge function appends contextual ranking indicators to key metrics, while _rank_line formats tier names and rating scores with optional seasonal labels. The _pad_inline_row function enforces a strict three-column grid layout by calculating the modulo-3 remainder of added fields and inserting invisible placeholder fields where data is sparse, preventing Discord's automatic field wrapping from misaligning subsequent sections. Section dividers are inserted using _add_section_separator to create full-width visual breaks between major data categories. Role and hero statistics are formatted using _role_field_value and _hero_field_value, with role names mapped to corresponding emojis via _role_emoji. When rating progression data exists, the function appends a textual summary generated by _rating_chart_summary and attaches a reference to an external image file using attachment://rating_chart.png. Finally, it sets a dynamic footer incorporating the season name and tracker attribution, applies a UTC timestamp, and returns the fully constructed discord.Embed instance. Within the project architecture, this function serves as the primary presentation-layer bridge between the raw PlayerProfile data model and the Discord UI. It is invoked by the stats command handler in src/features/stats/command.py, which passes the fetched profile to this function before attaching a dynamically rendered rating chart image file via discord.File and delivering the response via Discord's interaction followup mechanism. The function relies on several private utility functions (_add_section_separator, _pad_inline_row, _rank_line, _rating_chart_summary, _role_field_value, _hero_field_value) to maintain consistent visual alignment across varying player data configurations without duplicating formatting logic in the caller.

**Note**: Points to note about the use of the code
- The function assumes all PlayerProfile attributes are pre-populated by the tracker parser; it performs no data validation or fallback handling for missing fields beyond standard truthiness checks.
- Inline field padding relies on the modulo-3 logic in _pad_inline_row; passing an incorrect count will cause visual misalignment in subsequent sections.
- The rating chart image is referenced via attachment://rating_chart.png but is not generated within this function; it must be provided by the caller as a discord.File object to avoid broken image links.
- Discord markdown syntax (e.g., -# for caption text, ** for bold) is hardcoded in helper outputs and will render natively in Discord clients without additional processing.
- The function modifies no external state and returns a new discord.Embed instance, making it safe for concurrent command execution within the stats handler.
- Conditional field addition means embeds may vary significantly in height depending on player activity; callers should not assume a fixed embed dimension.

**Output Example**: 
Title: PlayerName — Marvel Rivals Overview
Description: 🎮 **1,240** matchs · ⏱️ **342h** de jeu
-# Season 5
Fields (Inline):
⚖️ KDA Ratio | **3.45** \n-# Top 8.2%
🏆 Win % | **58.1%** \n-# Top 12.5%
✅ Wins | **720** \n-# Top 15.0%
(Section Separator)
🏅 Rang actuel | **Grandmaster** · 4850 RS
📈 Peak saison | **Master** · 4200 RS
👑 All-time best | **Diamond I** · 3900 RS \n-# Season 1
(Section Separator)
⚔️ Combat | K/D **2.8** \n Kills **8,420** \n Deaths **3,007**
💥 Impact | Damage **1.2M** \n Healing **450K**
🌟 Distinctions | MVPs **142** \n MVP % **11.4%**
(Section Separator)
🛡️ Tank | 🏆 WR **61.2%** · 310 wins \n ⚖️ KDA **4.10** \n -# 980 / 239 / 995
⚔️ DPS | 🏆 WR **54.8%** · 450 wins \n ⚖️ KDA **2.95** \n -# 1,102 / 373 / 996
🎮 Support | 🏆 WR **48.5%** · 120 wins \n ⚖️ KDA **1.80** \n -# 210 / 116 / 400
(Section Separator)
🥇 Widowmaker | 🏆 WR **65.3%** · 145-87-3 \n ⚖️ KDA **3.42** \n -# 1,204 / 352 / 987
🥈 Genji | 🏆 WR **59.1%** · 98-65-2 \n ⚖️ KDA **2.88** \n -# 890 / 309 / 994
🥉 D.Va | 🏆 WR **52.4%** · 76-68-1 \n ⚖️ KDA **2.50** \n -# 650 / 260 / 998
(Section Separator)
📊 Évolution du rating | 📈 **42** parties classées · 🔺 **+150 RS** · 🎯 **4850 RS** actuels
Footer: Season 5 · Tracker.gg · Marvel Rivals
Timestamp: [Current UTC Time]
## FunctionDef build_error_embed(message)
**build_error_embed**: The function of build_error_embed is to construct and return a standardized Discord Embed object formatted specifically for displaying error messages to users.
**parameters**: The parameters of this Function.
· message: A string containing the specific error details or exception text that will be displayed as the description of the embed.
**Code Description**: The description of this Function.
This function initializes a discord.Embed instance with a fixed title "Erreur", assigns the provided message parameter to the embed's description field, and applies a red color scheme using discord.Color.red() to visually indicate an error state. It serves as a centralized utility for error reporting across the bot's command handlers. In the project architecture, this function is invoked within try...except blocks in multiple slash commands (/feels, /match, /register, and /stats). When exceptions such as ProfileNotFoundError, TrackerRateLimitError, TrackerScraperError, or generic runtime errors occur during API calls or data processing, the caught exception's string representation is passed to this function. The resulting embed is then sent to the user via interaction.followup.send() or interaction.response.send_message(), ensuring consistent error presentation and immediate feedback regardless of the underlying failure type.
**Note**: Points to note about the use of the code
The title is hardcoded in French ("Erreur"), which may require localization adjustments if the bot supports multiple languages. The function does not handle logging or exception suppression; it strictly formats the message for UI display. Callers are responsible for converting exceptions to strings before passing them as arguments. The embed is typically sent with ephemeral=True in command handlers, meaning only the requesting user can see it.
**Output Example**: Mock up a possible appearance of the code's return value.
A Discord embed with a red border, title "Erreur", and description containing the provided error string (e.g., "Profile not found on Tracker.gg").
