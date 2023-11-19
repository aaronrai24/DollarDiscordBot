Dollar 1.1.4 represents a significant cleanup effort, addressing lingering issues from its earlier, smaller-scale iterations. We are thrilled to announce that a major update is in the works, bringing with it exciting new features.

## Roadmap Highlights

Our future plans include a deeper integration with the Spotipy API, opening up new possibilities for Dollar's functionality. In the upcoming update, our goal is to elevate Dollar beyond being just Cash's personal assistant to a tool that caters to everyone's needs. Imagine automating daily tasks such as checking scores, monitoring the weather, and estimating commute times for work. Checkout the [issues](https://github.com/aaronrai24/DollarDiscordBot/issues) board for a sneak peek on new features projected for Dollar 2.0!

## Fixes and Enhancements

### Consistent Coding and Improved Contribution Process

- Pylinted the entire Dollar code base to ensure consistent coding practices and a cleaner programming environment. This makes contributing to Dollar significantly more accessible and streamlined.

### Improved User Experience

- Incorporated shutdown warnings for when the Dollar system becomes inactive. Additionally, this feature will now ping `@Cash` to promptly notify of an unplanned shutdown.
- Added inactivity message for Dollar after 10 minutes has been reached. Dollar will clear the `commands` chat and then log a message about inactivity.
- Enhanced consistency in embed usage across general messages and error notifications to deliver clear and user-friendly messages, ensuring a more intuitive and streamlined experience for users.
- Added more error handling for internal debugging, along with visible messages to users for all errors.
- Resolved an issue where Dollar would persistently remain active, even after 10 minutes of inactivity.
- Resolved an issue where patch notes would not display on startup.
- Resolved an issue where DEBUG logging would not display in `discord.log`