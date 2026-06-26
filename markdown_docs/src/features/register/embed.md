## FunctionDef build_already_linked_embed(usernames)
**build_already_linked_embed**: The function of build_already_linked_embed is to construct a Discord embed message that informs a user that a specific Tracker.gg username is already associated with their Discord account, while displaying their current list of linked usernames and registration quota.

**parameters**: 
· usernames: A list of strings representing the Tracker.gg usernames currently linked to the user's Discord account.

**Code Description**: 
This function generates a formatted Discord Embed object specifically designed for the duplicate-link scenario within the registration workflow. It processes the input `usernames` list by formatting each entry as a bold bullet point (`• **name**`). If the provided list is empty, it defaults to a single em dash ("—") to preserve layout consistency. The formatted string is integrated into a Discord message with an orange color theme. The embed title is set to "Pseudo déjà lié", and the description provides contextual information in French, stating that the requested Tracker.gg username is already associated with the user's account. It dynamically calculates and displays the current number of linked usernames against the system limit (`MAX_REGISTRATIONS_PER_USER`), followed by the formatted list of existing links. Within the project architecture, this function is directly invoked by the `register_register_command/register` handler when the backend store confirms that a requested username already exists for the interacting user. It serves as a feedback mechanism to prevent duplicate registrations and clearly communicates the current state of the user's linked accounts before they proceed with further actions. The caller passes the pre-fetched list from `store.list_for_user(discord_user_id)` directly into this function, ensuring that presentation logic remains decoupled from data retrieval logic.

**Note**: 
- The function relies on an external constant `MAX_REGISTRATIONS_PER_USER` which must be defined in the module scope or imported appropriately for the quota calculation to execute correctly.
- The embed text is hardcoded in French; ensure this aligns with your bot's localization strategy or internationalization requirements before deployment.
- The function does not handle database queries, API calls, or validation itself; it strictly formats and returns a presentation object based on pre-fetched data.
- When `usernames` is an empty list, the description will still render correctly but will show "0/limit" followed by "—", which may appear slightly inconsistent if the quota logic expects at least one entry in this specific branch.

**Output Example**: 
Title: Pseudo déjà lié
Description: Ce pseudo Tracker.gg est déjà associé à votre compte Discord.

Vos pseudos (2/5)
• **ValorantPlayer1**
• **ApexHunter99**
Color: Orange
## FunctionDef build_quota_reached_embed(usernames)
**build_quota_reached_embed**: The function of build_quota_reached_embed is to construct and return a Discord embed message indicating that a user has reached the maximum allowed number of linked usernames.
**parameters**: The parameters of this Function.
· usernames: A list of strings representing the currently linked usernames for the user.
**Code Description**: This function generates a formatted Discord Embed object to notify users when they have met or exceeded the system-defined limit for linked usernames. It processes the `usernames` parameter by iterating through each string and formatting it as a bold, bulleted line using a generator expression joined by newline characters. The resulting embed is configured with the title "Limite atteinte", a description that dynamically inserts the value of `MAX_REGISTRATIONS_PER_USER`, displays the user's current linked usernames under the heading "**Vos pseudos**", and provides explicit instructions to remove an existing link before attempting to register a new one. The embed utilizes a red color scheme to visually communicate a warning or restriction state. Functionally, this object is tightly coupled with the registration workflow in `src/features/register/command.py`. It is invoked exclusively within the `register` command handler when the storage layer confirms that `await store.count_for_user(discord_user_id)` equals or exceeds `MAX_REGISTRATIONS_PER_USER`. The returned embed is immediately passed to `interaction.response.send_message()` with the ephemeral flag enabled, ensuring the quota limit notification is visible only to the requesting user and does not clutter public channels.
**Note**: Points to note about the use of the code
· The function depends on a module-level constant named `MAX_REGISTRATIONS_PER_USER` for dynamic text generation; this variable must be defined in the same scope or imported correctly before execution.
· All user-facing strings are hardcoded in French, indicating localized UI behavior. If multilingual support is required in the future, these strings should be externalized to a translation management system.
· The function strictly returns a `discord.Embed` object and does not handle message delivery, ephemeral flags, or error handling; those responsibilities remain entirely with the calling command handler.
**Output Example**: Mock up a possible appearance of the code's return value.
Embed(title='Limite atteinte', description='Vous avez déjà 5 pseudos liés (maximum autorisé).\n\n**Vos pseudos**\n• **PlayerOne**\n• **GamerTag2**\n\nRetirez un lien existant avant d\'en ajouter un nouveau.', color=Color.red())
## FunctionDef build_register_success_embed(added_profile, all_usernames)
**build_register_success_embed**: The function of build_register_success_embed is to generate and return a formatted Discord embed that confirms the successful linking of a game profile to a user's Discord account.
**parameters**: The parameters of this Function.
· added_profile: PlayerProfile - An instance containing the metadata of the newly registered player, specifically providing the display name (username) and the direct link to their external profile page (profile_url).
· all_usernames: list[str] - A list of strings representing all game usernames currently associated with the user's Discord account.
**Code Description**: This function constructs a Discord embed message to provide immediate feedback following a successful profile registration. It processes the all_usernames list by formatting each entry as a bulleted item and calculates the total count of linked profiles. The embed title is set to "Pseudo enregistré", while the description dynamically inserts the newly added username and displays the current quota usage against the system limit MAX_REGISTRATIONS_PER_USER. The embed utilizes a predefined color constant DEFAULT_EMBED_COLOR and links directly to the player's external Tracker.gg profile via the profile_url attribute from added_profile. A footer is appended to indicate the data source "Tracker.gg · Marvel Rivals". Functionally, this object serves as the final presentation layer in the registration workflow. It is invoked exclusively by the register command handler in src/features/register/command.py after database persistence and quota validation succeed. The function relies on the PlayerProfile model to extract display identifiers and external links, ensuring that downstream UI components receive structured, ready-to-render data without additional transformation.
**Note**: Points to note about the use of the code
- The function assumes all_usernames is non-empty; if an empty list is passed, the description will render with a blank line after the quota text.
- The embed title and footer text are hardcoded in French and English respectively; localization is not handled within this function.
- The MAX_REGISTRATIONS_PER_USER constant must be accessible in the module's scope for the quota display to function correctly.
- The returned discord.Embed object is designed for ephemeral delivery, meaning it will only be visible to the command invoker and should not be used for public channel broadcasting without modification.
**Output Example**: Mock up a possible appearance of the code's return value.
Title: Pseudo enregistré
Description: **ShadowHunter** est maintenant lié à votre compte Discord.

**Vos pseudos (1/5)**
• **ShadowHunter**
Color: #00FF00 (DEFAULT_EMBED_COLOR)
URL: https://tracker.gg/marvel-rivals/profile/battle.net/ShadowHunter#competitive
Footer: Tracker.gg · Marvel Rivals
