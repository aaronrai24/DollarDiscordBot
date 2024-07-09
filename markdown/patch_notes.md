Dollar 1.1.9 updates Lavalink to 4.0.7 and Youtube-Source to 1.4.0 to keep up with the latest changes and bug fixes for both dependencies. Updating our dependencies ensures Dollar runs smoothly and efficiently, and we can take advantage of the latest features and improvements. Expect minor updates similar to this one as we continue to maintain and improve Dollar.

## Fixes and Enhancements
- Updated Lavalink to 4.0.7 which provides the following dependency updates:
  - Updated Lavaplayer to 2.2.1
  - Updated spring-boot to 3.3.0 & spring-websocket to 6.1.9
  - Updated kotlin to 2.0.0 & kotlinx-serialization-json to 1.7.0
  - Updated logback to 1.5.6 & sentry-logback to 7.10.0
- Updated Youtube-Source plugin to 1.4.0 which fixes an issue with the n cipher regex that meant some new patterns weren't being detected. In addition, switched to a cookie-less HTTP interface manager to avoid storing cookies between requests.
