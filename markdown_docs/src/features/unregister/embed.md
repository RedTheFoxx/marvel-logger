## FunctionDef build_not_registered_embed(username)
**build_not_registered_embed**: The function of build_not_registered_embed is to construct and return a Discord embed object that informs the user that the specified username is not linked to their Discord account.
**parameters**: 
· username: A string representing the username or pseudo provided by the user during the unregister command execution.
**Code Description**: This function initializes and returns a `discord.Embed` instance designed for user feedback within a Discord bot interface. It configures the embed with a fixed French title "Pseudo introuvable", dynamically injects the provided username into the description, and appends instructions to verify spelling or use the `/register` command. The visual styling applies an orange color (`discord.Color.orange()`) to indicate a warning or informational state. Within the project architecture, this function is directly invoked by the `unregister` slash command handler in `src/features/unregister/command.py`. It executes exclusively when the persistence layer confirms that the requested username does not exist under the user's Discord ID. The returned embed is immediately passed to `interaction.response.send_message` with `ephemeral=True`, ensuring the feedback is visible only to the requesting user and does not pollute public chat channels.
**Note**: The textual content within the embed is hardcoded in French and will not adapt to different locales automatically. The function expects a standard string input; excessively long usernames may trigger Discord's embed character limits or formatting constraints. It strictly depends on the `discord.py` library for the `Embed` and `Color` classes. Ensure the caller passes a sanitized string to prevent unexpected formatting issues.
**Output Example**: 
```python
Embed(
    title="Pseudo introuvable",
    description="**example_user** n'est pas lié à votre compte Discord.\nVérifiez l'orthographe ou utilisez `/register` pour l'ajouter.",
    color=16753920,
    type="rich"
)
```
## FunctionDef build_unregister_success_embed(removed_username, remaining_usernames, feels_deleted)
**build_unregister_success_embed**: The function of build_unregister_success_embed is to construct and return a formatted Discord embed message that confirms the successful removal of a username from a user's account while displaying remaining associated usernames and deleted feels count.
**parameters**: The parameters of this Function.
· removed_username: A string representing the exact username that was just unregistered and dissociated from the Discord account.
· remaining_usernames: A list of strings containing the usernames that are still currently linked to the user's account after the removal operation.
· feels_deleted: An integer indicating the number of associated feels records that were deleted alongside the unregistered username.
**Code Description**: This function generates a structured Discord embed to provide user feedback following a successful unregistration process. It first evaluates the remaining_usernames list. If the list contains entries, it formats them into a bulleted string with bolded names and appends a counter indicating how many pseudonyms remain out of the maximum allowed per user (MAX_REGISTRATIONS_PER_USER). If the list is empty, it generates a fallback message instructing the user to use the /register command to add new pseudonyms. Next, it conditionally constructs a suffix string detailing the number of deleted feels if feels_deleted is greater than zero; otherwise, it remains an empty string. Finally, it assembles these components into a Discord Embed object with the title "Pseudo retiré", a description combining the dissociation confirmation, optional feels deletion notice, and remaining pseudonyms status, and applies a predefined default embed color (DEFAULT_EMBED_COLOR). Within the project architecture, this function is exclusively invoked by the unregister command handler in src/features/unregister/command.py. The caller executes database operations to remove the username and associated feels, retrieves the updated list of remaining usernames, and passes these results directly into this function. This separation of concerns ensures that business logic remains isolated from presentation logic, allowing the embed builder to focus solely on formatting and displaying the outcome of the unregistration operation.
**Note**: Points to note about the use of the code
- The function relies on external constants MAX_REGISTRATIONS_PER_USER and DEFAULT_EMBED_COLOR, which must be defined in the module scope or imported appropriately before execution.
- The embed title and descriptive text are hardcoded in French; ensure this aligns with the bot's configured language settings or internationalization strategy.
- The function does not perform any validation or database queries; it strictly formats data provided by the caller. Passing incorrect types (e.g., non-string usernames or negative integers for feels) may result in unexpected formatting or runtime errors.
**Output Example**: Mock up a possible appearance of the code's return value.
Embed(title="Pseudo retiré", color=0x00A86B, description="**example_user** a été dissocié de votre compte Discord.\n\n• **user_one**\n• **user_two**\n\n**Vos pseudos restants (2/5)**")
## FunctionDef build_unregister_error_embed(message)
**build_unregister_error_embed**: The function of build_unregister_error_embed is to construct and return a formatted Discord embed object specifically designed to display error messages during the user unregister process.
**parameters**: 
· message: A string containing the specific error description or notification text to be displayed within the embed's body.
**Code Description**: This function initializes a discord.Embed instance with predefined styling attributes tailored for error reporting. It sets the title to "Erreur", assigns the provided message parameter as the embed's description, and applies a red color scheme using discord.Color.red() to visually indicate a failure state. Within the project architecture, this function is exclusively invoked by the /unregister command handler located in src/features/unregister/command.py. It is utilized when internal database operations fail unexpectedly or when an exception is caught during the unregistration workflow. By centralizing the error embed construction, it ensures consistent visual feedback and message formatting across all failure scenarios in the unregister feature.
**Note**: The returned embed is typically sent as an ephemeral response, meaning only the command requester will see it. The title remains hardcoded in French ("Erreur"), which should be considered if internationalization is required. The function does not handle logging or state management; it strictly formats and returns the visual component for Discord API consumption.
**Output Example**: 
{
  "title": "Erreur",
  "description": "Une erreur inattendue s'est produite lors de la suppression. Réessayez plus tard.",
  "color": 16711680,
  "type": "rich"
}
