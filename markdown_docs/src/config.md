## FunctionDef _env_bool(key, default)
**_env_bool**: The function of _env_bool is to safely retrieve and interpret an environment variable as a boolean value, supporting multiple string representations for true states while providing a fallback default when the variable is unset or empty.
**parameters**: The parameters of this Function.
· key: A string representing the name of the environment variable to be retrieved from the system.
· default: A boolean value returned when the environment variable is unset, empty, or contains only whitespace.
**Code Description**: The function begins by accessing the operating system's environment variables via os.getenv using the provided key. If the variable does not exist, it defaults to an empty string. The retrieved value is then stripped of leading and trailing whitespace and converted to lowercase to ensure case-insensitive matching. If the processed string evaluates to a falsy state (i.e., it is empty), the function immediately returns the default parameter. Otherwise, it checks whether the cleaned string exactly matches any of the predefined truthy tokens: "1", "true", "yes", or "on". If a match is found, the function returns True; if the value does not match any truthy token, the expression evaluates to False and is returned.
**Note**: Points to note about the use of the code
- The function strictly requires the environment variable to be set to one of the specified truthy strings to return True. Any other non-empty string (including "0", "false", "no", "off", or arbitrary text) will result in False.
- Whitespace handling is automatic, so values with surrounding spaces are correctly normalized before evaluation.
- The function relies on the os module; ensure it is imported in the parent scope before calling this function.
- Case sensitivity is normalized internally, but exact string matching is enforced after normalization.
**Output Example**: Mock up a possible appearance of the code's return value.
- When key is "DEBUG" and the environment variable DEBUG=true, the function returns True.
- When key is "VERBOSE" and the environment variable is unset, the function returns False (assuming default=False).
- When key is "ENABLE_CACHE" and the environment variable is "  YES  ", the function returns True.
