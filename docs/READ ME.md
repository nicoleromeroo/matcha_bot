# READ ME

----
#### Author: Nicole M. Romero
----

## 1. Objective 
Goal of this project is to develop a Python-based bot that monitors the availability of selected matcha products on multiple online shop websites. 
The bot checks predefined URLs at regular time intervals and sends an automatic notification to a Discord channel via webhook when products are back in stock.

The system supports:
- Monitoring product availability on one or multiple websites
- Parsing website content (HTML or JavaScript-based)
- Sending stock notifications to a Discord channel using webhooks
- Automated scheduling of periodic checks


## 2. Intended Use
The application is intended for personal use by individuals who want to be automatically notified when certain matcha products are available for purchase again. 
This prevents the need to manually check online stores frequently.

## 3. Functional Requirements
#### 3.1 Product Monitoring
The system must monitor one or more product URLs.

Monitoring should occur every 5 minutes. (optional: 1min, 5min, 15min, 30min, 1hr)

The system should extract stock information from the product page.

#### 3.2 Notification Logic
If a product is back in stock, the bot must send a message to a Discord webhook.

The notification message should contain the product name and URL of the product.

#### 3.3 Website Management
The list of monitored URLs must be configurable (in code or via file).

The system must handle websites that dynamically load content (using JavaScript).

#### .4 Error Handling
The system must catch and log errors such as:

Failed HTTP requests

Parsing errors

Invalid webhook URLs

## 4. Non-Functional Requirements
The application must be written in Python.

Code must follow clean, modular practices with comments.

The bot must be executable on Windows.

The project should be version-controlled using Git (locally or GitHub).

Lightweight and low on dependencies.

The bot should be available as an extension on Google Chrome

## 5. Architecture
#### Current Setup
- Python script with logic

#### Target Architecture
Modular Python project with:
- Monitoring logic
- Parsing logic
- Notification logic
- Configurable website list
- Automation via Windows Task Scheduler (or schedule module)

Optional: Logging and error reporting

## 6. Technical Stack
Component - Technology
Programming	- Python 3.8+
Parsing	- BeautifulSoup / Playwright
HTTP Requests - requests
Notifications - Discord Webhook API
IDE	- PyCharm
Version Control	- Git / GitHub
Scheduler -	Windows Task Scheduler / schedule lib

## 7. Limitations
The following features are out of scope:

Real-time monitoring (more frequent than every 1 minute)

Web GUI or mobile notifications

Integration with Telegram, Email or other platforms (only Discord supported)

Internationalization (only English interface)

## 8. Glossary

Webhook: A URL endpoint that can receive POST requests to trigger actions
Product Parser: Logic that extracts stock info from product HTML or JS
BeautifulSoup: Python library for parsing HTML/XML
Playwright: Headless browser automation tool (for JavaScript-heavy websites)