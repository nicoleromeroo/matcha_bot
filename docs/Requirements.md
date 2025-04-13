# Requirement List – Matcha Stock Notification Bot


## 1. Functional Requirements

F1	The system shall regularly (every 5 minutes or optional time) check one or more websites.
F2	The system shall detect whether the product is "in stock" or "out of stock".
F3	If the product is available, the system shall send a notification to a Discord channel.
F4	The notification shall be sent via a preconfigured Discord Webhook.
F5	The system shall support checking multiple websites either sequentially or in parallel.
F6	The URLs of the websites to monitor shall be configurable.
F7	The bot shall be executable and stoppable from the terminal/command line.
F8	Errors (e.g., connection failures) shall be printed to the terminal.

## 2. Non-Functional Requirements

N1	The bot shall be developed using Python.
N2	The bot shall be developed and tested in PyCharm.
N3	The system shall reliably run in the background on Windows.
N4	The project shall be well documented (README, code comments).
N5	The solution shall minimize external dependencies.
N6	The codebase shall be maintainable and extendable (e.g., for adding new websites).

## 3. Technical Requirements

T1	The project shall use the Python libraries requests, beautifulsoup4 (and optionally playwright).
T2	The system shall use Discord Webhooks to send notifications.
T3	Python version 3.8 or higher shall be installed.
T4	The script shall be executable on a schedule using Windows Task Scheduler.