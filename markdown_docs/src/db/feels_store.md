## ClassDef MatchFeelsRecord
**MatchFeelsRecord**: The function of MatchFeelsRecord is to serve as a structured data container that captures a user's subjective match rating alongside a complete snapshot of objective match statistics at the time of evaluation.
**attributes**: The attributes of this Class.
· discord_user_id: int - Unique identifier for the Discord user submitting the rating.
· tracker_username: str - Username associated with the Tracker.gg profile.
· match_id: str - Unique identifier for the specific game match.
· season_id: int - Identifier for the current game season.
· rating: int - Subjective score provided by the user.
· played_at: datetime | None - Timestamp indicating when the match was played.
· hero_name: str | None - Name of the character played in the match.
· map_name: str | None - Name of the game map.
· game_mode: str | None - Type of gameplay mode.
· outcome: str | None - Result of the match.
· score: str | None - Final match score.
· kills: str | None - Number of kills achieved.
· deaths: str | None - Number of times the player died.
· assists: str | None - Number of assists provided.
· kda_ratio: str | None - Kill/Death/Assist ratio.
· rs: str | None - Rating score at the time of the match.
· rs_delta: str | None - Change in rating score due to the match.
· raw_snapshot_json: str | None - JSON string containing the original raw match data snapshot.
· rated_at: datetime | None - Timestamp indicating when the rating was submitted.
**Code Description**: MatchFeelsRecord functions as an intermediate data transfer object within the application's database and feature layers. It is instantiated by `build_feels_record` in the view layer, which aggregates contextual match data from a `MatchBundle` and user input into this structure. Once populated, the record is passed to `FeelsStore.add_rating` and `_add_rating_sync`, where its attributes are directly mapped to columns in the SQLite `match_feels` table for persistent storage. During retrieval, `FeelsStore.list_for_season` queries the database and reconstructs instances of this class via `_row_to_record`. The deserialized records are subsequently consumed by downstream feature modules: `render_feels_chart` and `_bar_label` utilize fields such as `rating`, `outcome`, `hero_name`, and `played_at` to generate visual bar charts and axis labels, while `build_feels_overview_embed` and `build_feels_saved_embed` aggregate the records to compute seasonal averages and construct Discord embed messages for user feedback.
**Note**: All optional attributes default to `None` and require null-safe handling during serialization or UI rendering. The `rating` field is strictly typed as an integer, indicating it expects discrete numerical values rather than floats. When persisting the record, ensure that `rated_at` defaults to the current UTC time if not explicitly provided, as handled in `_add_rating_sync`. The `raw_snapshot_json` field preserves the original match data for potential future analysis or debugging, so its format must remain consistent with the source Tracker.gg API response. Ensure that all numeric statistics stored as strings are validated before database insertion to prevent type mismatch errors during SQLite operations.
## FunctionDef _parse_dt(value)
**_parse_dt**: The function of _parse_dt is to safely convert a string representation of a date and time into a datetime object, returning None if the input is invalid or missing.
**parameters**: The parameters of this Function.
· value: A string containing an ISO 8601 formatted date-time value, or None.
**Code Description**: This function serves as a defensive parser for timestamp strings extracted from database records. It begins by evaluating whether the input value is falsy (None or an empty string). If so, it immediately returns None to avoid unnecessary processing. When a non-empty string is provided, the function attempts to parse it using Python's datetime.fromisoformat() method, which strictly requires ISO 8601 compliance. If the string does not conform to this format, a ValueError is raised internally; the function catches this exception and returns None instead of propagating the error. In the context of the project, _parse_dt is exclusively invoked by the _row_to_record function in src/db/feels_store.py. During database record deserialization, _row_to_record passes the played_at and rated_at columns from a sqlite3.Row object to _parse_dt. This integration guarantees that any malformed, truncated, or absent timestamp data in the SQLite database is handled gracefully, preventing runtime crashes during object construction while preserving type safety for the MatchFeelsRecord attributes.
**Note**: Points to note about the use of the code
- The parser strictly enforces ISO 8601 formatting. Any deviation from this standard will silently return None rather than raising an exception.
- The leading underscore indicates that this is a private utility function intended for internal use within src/db/feels_store.py and should not be imported or called by external modules.
- Database columns feeding into this function should ideally contain either valid ISO 8601 strings or NULL values to align with the expected input contract.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: "2023-10-25T14:30:00" -> Output: datetime.datetime(2023, 10, 25, 14, 30)
- Input: None -> Output: None
- Input: "invalid-date-string" -> Output: None
## FunctionDef _row_to_record(row)
**_row_to_record**: The function of _row_to_record is to deserialize a single SQLite database row into a structured MatchFeelsRecord object for application use.
**parameters**: The parameters of this Function.
· row: A sqlite3.Row object containing the raw column data retrieved from the match_feels database table.
**Code Description**: This function acts as a dedicated deserialization utility that transforms raw database query results into strongly-typed domain objects. It extracts specific columns from the provided sqlite3.Row instance and assigns them to the corresponding attributes of a MatchFeelsRecord instance. For timestamp fields (played_at and rated_at), it delegates parsing to the _parse_dt helper function to ensure safe conversion from ISO 8601 strings to datetime objects, returning None for invalid or missing values. All other fields are directly mapped as-is, preserving their original types such as integers, strings, or JSON payloads. Within the project architecture, this function is exclusively invoked by FeelsStore._list_for_season_sync during the data retrieval phase. The caller executes a parameterized SQL query to fetch historical match ratings for a specific user and season, then applies _row_to_record to each resulting row via a list comprehension. This establishes a clear pipeline where raw relational data is systematically converted into domain models before being passed to higher-level feature modules for chart rendering or embed construction.
**Note**: Points to note about the use of the code
- The function assumes the input sqlite3.Row contains all expected columns; missing keys will raise a KeyError during execution.
- Timestamp parsing relies on _parse_dt, which silently returns None for malformed data, so downstream consumers must handle potential None values for played_at and rated_at.
- As a private utility (indicated by the leading underscore), this function is intended for internal use within the database layer and should not be imported or called directly by external modules.
- The mapping order does not affect functionality, but maintaining alignment with the MatchFeelsRecord attribute definition improves readability and maintainability.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: sqlite3.Row({'discord_user_id': 1234567890, 'tracker_username': 'PlayerOne', 'match_id': 'm_98765', 'season_id': 4, 'rating': 8, 'played_at': '2023-11-15T19:30:00', 'hero_name': 'Jett', 'map_name': 'Ascent', 'game_mode': 'Competitive', 'outcome': 'Win', 'score': '13-7', 'kills': '24', 'deaths': '18', 'assists': '5', 'kda_ratio': '1.61', 'rs': '1450', 'rs_delta': '+15', 'raw_snapshot_json': '{"kp": 0.85, "acs": 280}', 'rated_at': '2023-11-15T20:00:00'})
- Output: MatchFeelsRecord(discord_user_id=1234567890, tracker_username='PlayerOne', match_id='m_98765', season_id=4, rating=8, played_at=datetime.datetime(2023, 11, 15, 19, 30), hero_name='Jett', map_name='Ascent', game_mode='Competitive', outcome='Win', score='13-7', kills='24', deaths='18', assists='5', kda_ratio='1.61', rs='1450', rs_delta='+15', raw_snapshot_json='{"kp": 0.85, "acs": 280}', rated_at=datetime.datetime(2023, 11, 15, 20, 0))
## ClassDef FeelsStore
**FeelsStore**: The function of FeelsStore is to manage the persistent storage, retrieval, and deletion of match rating records using a SQLite database within the Discord bot application.

**attributes**: 
· _path: str | None - The file path pointing to the SQLite database file. Defaults to DATABASE_PATH if no explicit path is provided during initialization.

**Code Description**: 
FeelsStore operates as the dedicated data access layer for handling user match feedback (ratings). It implements a deliberate asynchronous/synchronous separation pattern: all public methods are async and delegate blocking SQLite operations to a background thread via asyncio.to_thread, ensuring the Discord bot's event loop remains responsive. The class initializes the database schema on startup by creating necessary directories and executing a predefined `_SCHEMA` script. Core functionalities include inserting new rating records through add_rating, querying historical ratings for a specific season with list_for_season, identifying already-rated matches via rated_match_ids to prevent duplicate submissions, and purging all associated feedback data using delete_for_username during account dissociation. 

In the project architecture, FeelsStore is instantiated in main() and injected into MarvelLoggerBot during bot initialization. It is functionally integrated into two primary command flows: the /feels command handler utilizes rated_match_ids and list_for_season to fetch existing ratings, generate overview charts, and populate interactive views for unsubmitted matches. The /unregister command handler calls delete_for_username to perform cascading data cleanup when a user removes their tracker.gg account linkage. Additionally, the FeelsRatingView component receives an instance of this class to persist user selections after interaction completion. All database queries use parameterized statements to prevent injection, and tracker usernames are normalized to lowercase during insertion to guarantee case-insensitive lookups across operations.

**Note**: 
- Public methods must be awaited; calling synchronous counterparts directly will block the event loop.
- Database initialization depends on an external `_SCHEMA` constant defined elsewhere in the module; missing or malformed schema definitions will cause init() to fail silently or raise SQLite errors.
- delete_for_username returns the exact number of affected rows, which should be used to verify successful data removal rather than relying solely on boolean success/failure.
- The rated_at field defaults to the current UTC time if record.rated_at is None during insertion.
- All string comparisons for tracker_username_normalized are case-insensitive due to normalization at write time.

**Output Example**: 
Mock return value for list_for_season:
[
  MatchFeelsRecord(
    discord_user_id=123456789,
    tracker_username="PlayerOne",
    tracker_username_normalized="playerone",
    match_id="abc123def456",
    season_id=42,
    rating=8,
    rated_at="2023-10-25T14:30:00+00:00",
    played_at="2023-10-24T20:15:00+00:00",
    hero_name="Ashe",
    map_name="Dorado",
    game_mode="5v5",
    outcome="win",
    score=35,
    kills=12,
    deaths=8,
    assists=15,
    kda_ratio=3.375,
    rs=1450,
    rs_delta=+25,
    raw_snapshot_json='{"key":"value"}'
  )
]
### FunctionDef __init__(self, path)
**__init__**: The function of __init__ is to initialize a new instance of the FeelsStore class by configuring its internal database path attribute.
**parameters**: The parameters of this Function.
· path: An optional string specifying the file or directory path for the database. Defaults to None if not provided.
**Code Description**: The description of this Function.
This method serves as the constructor for the FeelsStore class. Upon instantiation, it evaluates the `path` argument and assigns it to the private instance attribute `_path`. If the `path` argument is omitted or explicitly set to None, the assignment automatically defaults to a predefined module-level constant named `DATABASE_PATH`. This fallback mechanism ensures that every instance of the class is initialized with a valid database path without requiring mandatory input during object creation. The type hint `str | None` indicates that the parameter accepts either a string value or None, and the return type annotation `-> None` confirms that the method does not return any value.
**Note**: Points to note about the use of the code
The fallback behavior strictly depends on `DATABASE_PATH` being defined in the module scope prior to instantiation. Passing an empty string will still assign it to `_path`, so external validation should be implemented if strict path correctness is required. Additionally, since `_path` is a private attribute, direct modification outside the class is discouraged to maintain internal state consistency.
***
### FunctionDef init(self)
**init**: The function of init is to asynchronously trigger the synchronous initialization of the SQLite database backend by offloading the blocking setup task to a background thread pool.
**parameters**: 
· self: The instance of the FeelsStore class that manages the database path configuration and connection lifecycle.
**Code Description**: This async method serves as the designated entry point for database preparation within the FeelsStore component. It delegates the actual file system and database setup operations to the synchronous `_init_sync` method using `asyncio.to_thread`, which schedules the blocking I/O workload on a dedicated thread pool executor. This architectural pattern prevents the main asynchronous event loop from being blocked during critical SQLite connection establishment, directory creation, and schema application phases. The underlying `_init_sync` routine resolves the target database path via pathlib, creates any missing parent directories, establishes a new SQLite connection, applies the predefined schema structure through `executescript`, commits the transaction, and guarantees connection closure in a finally block. Within the project workflow, this method is invoked during the application startup sequence by the `setup_hook` method of the MarvelLoggerBot class, which coordinates subsystem initialization before the bot becomes operational. By integrating with the async event loop through controlled thread offloading, it ensures deterministic database readiness while preserving concurrent task execution capabilities.
**Note**: The method must be awaited to ensure completion before subsequent operations proceed. It depends on `self._path` being correctly configured and the external `_SCHEMA` constant containing valid table definitions prior to invocation. Because the actual setup runs synchronously in a background thread, developers must verify that the target directory path has appropriate write permissions for the executing process. The use of `asyncio.to_thread` requires Python 3.9 or later, and any exceptions raised during database initialization will propagate through the await point, requiring explicit error handling in the caller (`setup_hook`) to maintain application stability.
***
### FunctionDef _init_sync(self)
**_init_sync**: The function of _init_sync is to synchronously initialize the SQLite database file and apply the initial schema structure.
**parameters**: 
· self: The instance of the FeelsStore class containing the database path configuration.
**Code Description**: This method performs the core synchronous setup for the SQLite database. It first resolves the database file path using `pathlib.Path` and ensures that all necessary parent directories exist by calling `mkdir` with `parents=True` and `exist_ok=True`. A new SQLite connection is then established to the resolved path. Within a try block, it executes a predefined schema script (`_SCHEMA`) via `executescript` to create the required tables and structure, followed by a commit to finalize the changes. The connection is guaranteed to be closed in the finally block, regardless of whether an exception occurs during execution. Functionally, this synchronous routine is invoked by the async `init` method using `asyncio.to_thread`, which offloads the blocking database initialization work to a background thread pool. This design maintains non-blocking behavior in the main asynchronous event loop while ensuring reliable and deterministic database setup without interrupting other concurrent tasks.
**Note**: The method relies on an external constant `_SCHEMA` for table definitions and assumes `self._path` is a valid string or path-like object representing the desired database file location. Developers should ensure that the target directory permissions allow for file creation, and be aware that this operation performs blocking I/O. It must always be executed within a thread pool (as demonstrated by its caller) when used in asynchronous contexts to prevent event loop starvation.
***
### FunctionDef add_rating(self, record)
**add_rating**: The function of add_rating is to asynchronously persist a user's match rating and associated statistical data into the database by offloading the synchronous insertion task to a background thread.
**parameters**: The parameters of this Function.
· record: MatchFeelsRecord - A structured data container holding the Discord user ID, tracker username, match details, subjective rating, timestamps, hero/map/mode information, outcome, score, combat statistics, rating metrics, and a raw JSON snapshot of the match data.
**Code Description**: This method serves as an asynchronous bridge between the application's event loop and blocking database operations. It accepts a `MatchFeelsRecord` instance containing all necessary fields for storage. Instead of executing the SQLite insertion directly on the main thread, it delegates the work to `_add_rating_sync` via `asyncio.to_thread`. This design ensures that the I/O-bound database write does not block the asynchronous event loop, maintaining application responsiveness. The method is functionally invoked by `FeelsRatingView._on_rating_select`, which constructs the `record` from user interaction data and passes it here for persistence. Upon completion of the background thread execution, control returns to the caller, allowing the view layer to proceed with post-save operations such as fetching updated seasonal records, rendering a chart, and updating the Discord interface. The synchronous counterpart `_add_rating_sync` handles the actual parameterized SQL insertion, timestamp normalization, and connection management.
**Note**: Ensure that the `record` object is fully populated before invocation, particularly verifying that all required fields like `discord_user_id`, `tracker_username`, `match_id`, `season_id`, and `rating` contain valid data. Since this method delegates to a synchronous function, it must always be awaited using `await`. The underlying `_add_rating_sync` method relies on the parent class's internal database path configuration; an invalid path will propagate connection errors up through this async wrapper. Error handling for constraint violations (such as duplicate ratings) should be managed at the caller level, as demonstrated in `_on_rating_select`, rather than within this method itself.
***
### FunctionDef _add_rating_sync(self, record)
**_add_rating_sync**: The function of _add_rating_sync is to synchronously persist a match rating and its associated statistical snapshot into a SQLite database using parameterized SQL insertion.

**parameters**: The parameters of this Function.
· record: MatchFeelsRecord - A structured data container holding the Discord user ID, tracker username, match details, subjective rating, timestamps, hero/map/mode information, outcome, score, combat statistics (kills, deaths, assists, KDA), rating metrics (rs, rs_delta), and a raw JSON snapshot of the match data.

**Code Description**: This method handles the direct database insertion logic for the `match_feels` table. It first processes timestamp fields by converting them to ISO 8601 formatted strings, defaulting `rated_at` to the current UTC time if it is not provided, and setting `played_at` to SQL NULL when absent. A new SQLite connection is established using the instance's internal `_path` attribute. The method then executes an INSERT statement with twenty parameter placeholders, mapping each attribute from the `record` object to its corresponding database column. Notably, the `tracker_username` is explicitly lowercased during insertion to ensure case-insensitive consistency in the storage layer. After execution, the transaction is committed, and the connection is guaranteed to be closed via a finally block, preventing resource leaks. Functionally, this synchronous routine is designed to be executed off the main thread; it is invoked by the asynchronous `add_rating` method through asyncio.to_thread, which bridges the blocking I/O operation with the application's event loop without causing performance degradation. The data flow originates from view-layer builders that instantiate MatchFeelsRecord, passes through this persistence layer, and becomes available for downstream retrieval methods like list_for_season.

**Note**: Ensure that the record object contains valid data types compatible with SQLite before invocation, particularly verifying that numeric statistics stored as strings are properly handled or converted if strict typing is enforced at the database level. The method relies on the parent class's `_path` attribute to locate the database file; an invalid or inaccessible path will raise a connection error. Since this function performs blocking I/O, it must always be wrapped in an asynchronous thread executor (as done by add_rating) to maintain application responsiveness. Timestamp normalization is critical: missing rated_at values are automatically backfilled with UTC time, while missing played_at values are explicitly stored as SQL NULL. The parameterized query structure inherently prevents SQL injection, but data validation should still be enforced at the application layer to avoid constraint violations or type mismatch errors during commit.
***
### FunctionDef list_for_season(self, discord_user_id, tracker_username_normalized, season_id)
**list_for_season**: The function of list_for_season is to asynchronously retrieve a chronological list of match rating records for a specific user and season by offloading a synchronous database query to a background thread pool.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class that manages the SQLite database file path.
· discord_user_id: int - Unique identifier for the Discord user whose match ratings are being requested.
· tracker_username_normalized: str - Lowercase, normalized Tracker.gg username used to filter records in the database.
· season_id: int - Identifier for the specific game season to filter the results.
**Code Description**: This async method serves as the public data access interface within the FeelsStore module for fetching historical match rating data. Rather than executing I/O operations directly on the main event loop, it utilizes asyncio.to_thread to delegate the actual retrieval work to self._list_for_season_sync. This architectural choice prevents blocking the asynchronous runtime during SQLite queries, ensuring the Discord bot remains responsive under concurrent requests. The method forwards all three filter parameters directly to the synchronous helper, which constructs a parameterized SQL query against the match_feels table, orders results chronologically using COALESCE(played_at, rated_at), and deserializes each row into a MatchFeelsRecord instance via _row_to_record. Upon completion, the coroutine resolves to a list of these structured records. Functionally, this method bridges the asynchronous feature layer with the synchronous data access layer. It is invoked by the /feels slash command to populate seasonal overview charts and by the FeelsRatingView._on_rating_select callback to refresh the rating visualization after a new submission. The returned list is subsequently consumed by downstream rendering functions such as render_feels_chart and embed builders like build_feels_overview_embed to generate visual feedback and compute seasonal statistics for Discord users.
**Note**: Points to note about the use of the code
- The method must be awaited in an asynchronous context; invoking it without await will return a coroutine object instead of the resolved list.
- It relies entirely on _list_for_season_sync for database connectivity and query execution, meaning any sqlite3.OperationalError or connection issues will propagate up to this async wrapper.
- The use of asyncio.to_thread ensures that the synchronous SQL query does not block the Discord bot's main event loop, maintaining responsiveness during high-concurrency scenarios.
- All parameters are passed by value; no validation is performed at this layer, so callers must ensure type correctness and data normalization (e.g., lowercase username) before invocation.
- The returned list may be empty if no matching records exist for the provided filters, which downstream modules must handle gracefully to avoid rendering errors.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: discord_user_id=1234567890, tracker_username_normalized='player_one', season_id=4
- Output: [MatchFeelsRecord(discord_user_id=1234567890, tracker_username='PlayerOne', match_id='m_98765', season_id=4, rating=8, played_at=datetime.datetime(2023, 11, 15, 19, 30), hero_name='Jett', map_name='Ascent', game_mode='Competitive', outcome='Win', score='13-7', kills='24', deaths='18', assists='5', kda_ratio='1.61', rs='1450', rs_delta='+15', raw_snapshot_json='{"kp": 0.85, "acs": 280}', rated_at=datetime.datetime(2023, 11, 15, 20, 0)), MatchFeelsRecord(discord_user_id=1234567890, tracker_username='PlayerOne', match_id='m_98766', season_id=4, rating=9, played_at=datetime.datetime(2023, 11, 16, 20, 15), hero_name='Sage', map_name='Bind', game_mode='Competitive', outcome='Loss', score='11-13', kills='18', deaths='20', assists='7', kda_ratio='1.25', rs='1465', rs_delta='+15', raw_snapshot_json='{"kp": 0.90, "acs": 310}', rated_at=datetime.datetime(2023, 11, 16, 21, 0)]]
***
### FunctionDef _list_for_season_sync(self, discord_user_id, tracker_username_normalized, season_id)
**_list_for_season_sync**: The function of _list_for_season_sync is to synchronously query an SQLite database for match rating records associated with a specific user and season, returning them as a list of structured MatchFeelsRecord objects sorted chronologically.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class that holds the database file path.
· discord_user_id: int - Unique identifier for the Discord user whose match ratings are being retrieved.
· tracker_username_normalized: str - Normalized Tracker.gg username used to filter records.
· season_id: int - Identifier for the specific game season to filter the results.
**Code Description**: This method performs a synchronous database retrieval operation within the FeelsStore class. It establishes a connection to the SQLite database located at self._path and configures the row factory to return sqlite3.Row objects, enabling column access by name. The function executes a parameterized SQL query against the match_feels table, filtering rows by discord_user_id, tracker_username_normalized, and season_id. Results are ordered chronologically using COALESCE(played_at, rated_at) ASC to handle cases where one timestamp might be null, ensuring consistent chronological sorting. After fetching all matching rows, it iterates through them and converts each raw database row into a MatchFeelsRecord instance via the _row_to_record helper function. The connection is guaranteed to close in the finally block regardless of execution success or failure. Functionally, this method serves as the synchronous core for data retrieval, explicitly designed to be offloaded from the main event loop by its caller, list_for_season, which wraps it using asyncio.to_thread to prevent blocking the asynchronous runtime during database I/O operations. The _row_to_record callee handles the deserialization of raw SQLite rows into domain objects, establishing a clear pipeline where relational data is systematically converted before being passed to higher-level feature modules.
**Note**: Points to note about the use of the code
- The method relies on self._path being correctly initialized before invocation; an invalid or missing path will raise a sqlite3.OperationalError.
- Parameterized queries are used exclusively to prevent SQL injection attacks and ensure type-safe binding for all three filter conditions.
- The COALESCE function ensures chronological ordering even when played_at is null, falling back to rated_at without raising errors.
- As a private method (indicated by the leading underscore), it is intended for internal use within the database layer and should not be called directly by external modules.
- The synchronous nature of this function requires careful handling in asynchronous contexts; direct invocation on the main thread will block event loop execution, which is why list_for_season delegates it to a background thread pool via asyncio.to_thread.
**Output Example**: Mock up a possible appearance of the code's return value.
- Input: discord_user_id=1234567890, tracker_username_normalized='player_one', season_id=4
- Output: [MatchFeelsRecord(discord_user_id=1234567890, tracker_username='PlayerOne', match_id='m_98765', season_id=4, rating=8, played_at=datetime.datetime(2023, 11, 15, 19, 30), hero_name='Jett', map_name='Ascent', game_mode='Competitive', outcome='Win', score='13-7', kills='24', deaths='18', assists='5', kda_ratio='1.61', rs='1450', rs_delta='+15', raw_snapshot_json='{"kp": 0.85, "acs": 280}', rated_at=datetime.datetime(2023, 11, 15, 20, 0)), MatchFeelsRecord(discord_user_id=1234567890, tracker_username='PlayerOne', match_id='m_98766', season_id=4, rating=9, played_at=datetime.datetime(2023, 11, 16, 20, 15), hero_name='Sage', map_name='Bind', game_mode='Competitive', outcome='Loss', score='11-13', kills='18', deaths='20', assists='7', kda_ratio='1.25', rs='1465', rs_delta='+15', raw_snapshot_json='{"kp": 0.90, "acs": 310}', rated_at=datetime.datetime(2023, 11, 16, 21, 0))]
***
### FunctionDef delete_for_username(self, discord_user_id, tracker_username_normalized)
**delete_for_username**: The function of delete_for_username is an asynchronous method that removes all database entries associated with a specific Discord user ID and normalized tracker username, returning the count of deleted records.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class that manages the SQLite database connection path.
· discord_user_id: An integer representing the unique identifier of the Discord user whose records are to be deleted.
· tracker_username_normalized: A string containing the normalized tracker username used as a secondary filter for the deletion query.
**Code Description**: This method functions as an asynchronous interface that offloads synchronous database operations to a background thread pool, preventing blocking of the main event loop. It delegates execution to the `_delete_for_username_sync` method via `asyncio.to_thread`, passing both `discord_user_id` and `tracker_username_normalized` as arguments. The underlying synchronous function establishes a direct connection to the SQLite database, executes a parameterized DELETE statement on the `match_feels` table filtered by the provided identifiers, commits the transaction, and returns the number of affected rows. Within the project architecture, this method is invoked by the `unregister` command handler located in `src/features/unregister/command.py`. The caller uses it to purge all associated tracking records before proceeding with the final removal of the user entry from the store. The returned integer is captured as `feels_deleted` and utilized to construct success embeds and generate execution logs, ensuring accurate feedback regarding how many related entries were purged during the unregistration process.
**Note**: Points to note about the use of the code
· This method must be awaited in an asynchronous context; it does not perform database operations directly but schedules them on a thread pool.
· The parameterized query syntax used by the underlying synchronous function ensures protection against SQL injection attacks.
· The returned integer will be 0 if no matching records exist, or a positive integer representing the exact number of deleted rows.
· Database connections are managed manually within the synchronous backend, so concurrent access to the same database file from multiple threads may require external synchronization mechanisms depending on the application's concurrency model.
**Output Example**: Mock up a possible appearance of the code's return value.
2
***
### FunctionDef _delete_for_username_sync(self, discord_user_id, tracker_username_normalized)
**_delete_for_username_sync**: The function of _delete_for_username_sync is to synchronously remove all database entries matching a specific Discord user ID and normalized tracker username, returning the count of deleted records.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class that manages the SQLite database connection path.
· discord_user_id: An integer representing the unique identifier of the Discord user whose records are to be deleted.
· tracker_username_normalized: A string containing the normalized tracker username used as a secondary filter for the deletion query.
**Code Description**: This method performs a synchronous database operation using the built-in sqlite3 module. It establishes a direct connection to the SQLite database file located at self._path, executes a parameterized DELETE statement on the match_feels table, and commits the transaction. The WHERE clause filters records by both discord_user_id and tracker_username_normalized to ensure precise targeting. After execution, it returns cursor.rowcount, which indicates how many rows were successfully removed. The connection is guaranteed to be closed in the finally block, preventing resource leaks even if an exception occurs. Functionally, this method serves as the synchronous backend for the async delete_for_username method. The caller wraps this function using asyncio.to_thread to execute it in a separate thread pool, thereby avoiding blocking the main event loop while preserving the exact same input parameters and return type. This design pattern separates synchronous I/O operations from asynchronous control flow, ensuring efficient database handling within an async-driven application architecture.
**Note**: Points to note about the use of the code
· This method is strictly synchronous and must not be awaited directly; it should only be invoked through its async wrapper or in a non-async context.
· The parameterized query syntax (?, ?) ensures protection against SQL injection attacks.
· The returned integer will be 0 if no matching records exist, or a positive integer representing the exact number of deleted rows.
· Database connections are managed manually within the method scope, so concurrent access to the same database file from multiple threads may require external synchronization mechanisms depending on the application's concurrency model.
**Output Example**: Mock up a possible appearance of the code's return value.
2
***
### FunctionDef rated_match_ids(self, discord_user_id, tracker_username_normalized, season_id)
**rated_match_ids**: The function of rated_match_ids is to asynchronously retrieve a collection of match identifiers that have already been rated by a specific Discord user for a given tracker username and season.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class providing access to internal database configuration and file paths.
· discord_user_id: An integer representing the unique identifier of the Discord user requesting the data.
· tracker_username_normalized: A string containing the lowercased and normalized version of the game tracker username.
· season_id: An integer representing the specific game season identifier used for filtering records.
**Code Description**: This async method functions as a non-blocking wrapper that delegates synchronous database operations to a background thread pool using `asyncio.to_thread`. It forwards the provided `discord_user_id`, `tracker_username_normalized`, and `season_id` to the internal `_rated_match_ids_sync` method, which establishes a direct SQLite connection, executes a parameterized SELECT query against the `match_feels` table, and returns the extracted match IDs as a set of strings. The threading delegation ensures that the blocking file I/O does not halt the main asynchronous event loop. Within the project architecture, this method is invoked by the `/feels` Discord slash command handler to fetch pre-existing rating data. The returned set is subsequently utilized to calculate rating statistics, filter out already-rated entries from the current match bundle, and determine whether a `FeelsRatingView` component should be rendered for user interaction.
**Note**: Because the underlying implementation performs synchronous SQLite queries, direct invocation within an async context without threading support would block the event loop. The internal delegation via `asyncio.to_thread` correctly mitigates this constraint. Ensure that the database file referenced by `self._path` exists and contains a properly structured `match_feels` table before calling this method. The caller must provide a valid, normalized tracker username and an active season ID to guarantee accurate query results and prevent empty or erroneous returns.
**Output Example**: {'match_12345', 'match_67890', 'match_11223'}
***
### FunctionDef _rated_match_ids_sync(self, discord_user_id, tracker_username_normalized, season_id)
**_rated_match_ids_sync**: The function of _rated_match_ids_sync is to synchronously query a SQLite database and retrieve a collection of match identifiers associated with a specific user and season.
**parameters**: The parameters of this Function.
· self: The instance of the FeelsStore class that provides the internal database file path via `self._path`.
· discord_user_id: An integer representing the unique identifier of the Discord user.
· tracker_username_normalized: A string containing the normalized version of the game tracker username.
· season_id: An integer representing the specific game season to filter by.
**Code Description**: This function establishes a direct connection to a SQLite database file located at `self._path`. It executes a parameterized SQL SELECT statement against the `match_feels` table, filtering records based on the provided `discord_user_id`, `tracker_username_normalized`, and `season_id`. The query retrieves all matching rows, and the function extracts the first column (match_id) from each row, returning them as a set of strings. A try-finally block ensures that the database connection is properly closed regardless of whether the query succeeds or raises an exception. Functionally, this synchronous method handles the low-level database retrieval logic. It is invoked by the async wrapper `rated_match_ids`, which utilizes `asyncio.to_thread` to execute this blocking I/O operation in a separate thread pool, thereby preventing the main asynchronous event loop from being blocked during database access.
**Note**: Because this function performs synchronous file I/O and database operations, it must not be called directly within an async context without threading support, as it will block the event loop. The caller `rated_match_ids` already handles this by delegating execution to a thread pool. Ensure that `self._path` points to a valid SQLite database file before invocation, and verify that the `match_feels` table schema contains the expected columns for accurate query results.
**Output Example**: {'match_12345', 'match_67890', 'match_11223'}
***
