## Changelog
### 0.0.2 Pre-Alpha - Issue Fixes
- **Fix**: Resolved the infinite softlock issue that occurred when none of the regex patterns matched the current line.
- **Update**: Changed the default regex pattern to accept logs that do not end with a period.

### 0.0.1 pre-alpha - Initial Commit
- **Feature**: Added logging with hierarchy.
- **Feature**: Introduced a singleton Config to manage global settings.
- **Feature**: Implemented log reading from **Project Zomboid**, allowing sequential processing of new entries.
- **Feature**: Added customizable regex filtering to capture specific log events, such as player interactions and state changes.
- **Feature**: Integrated SQLite database storage for filtered log data, facilitating easy querying and analysis.
- **Feature**: Implemented dynamic updating to track log reading position, ensuring only new entries are processed. 
- **Info**: The application is open source, promoting collaboration and community contributions.