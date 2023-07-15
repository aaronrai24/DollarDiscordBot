Dollar 1.1.3 introduces significant improvements to Dollar's codebase, aimed at enhancing readability and overall performance. However, as with any major update, there is a possibility of new bugs being introduced. To address this, we have implemented comprehensive logging to better track and address any issues that may arise. If you encounter any bugs, we encourage you to utilize the `/reportbug` command and provide us with details.

**New Features:**
- Reworked codebase for improved readability and performance.

**Fixes:**
- Restructured the main file into multiple files, organizing them based on command types. These files are then loaded as cogs into the main program.
- Removed the /ping command as it is no longer necessary. Dollar now incorporates enhanced measures to ensure its availability.
- Implemented standardized loggers for each command category, facilitating better error tracking and troubleshooting.