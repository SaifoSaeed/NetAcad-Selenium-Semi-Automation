_Note: take the computer networks course (takes 4 months), which is the first section of the CCNA (takes 2 months), and take the NetAcad course, as a 6% weighing assignment part of the course, and you will know all the basics!_
_I can't handle not learning during the learning process anymore, so let's learn selenium!_
# NetAcad Selenium Semi-Automation

This project is a Python-based utility designed to assist in navigating Cisco Networking Academy (Netacad) assessments. It uses a "Semi-Automation" approach, combining Selenium with PyAutoGUI macros to bypass advanced security restrictions like Cross-Origin Iframes and Shadow DOMs that standard automation tools often fail to penetrate.

## Core Functionality

* **Macro-Based Capture**: Uses `Ctrl+S` macros to save the current exam page locally, ensuring all content within nested iframes is captured for parsing.
* **Shadow DOM Piercing**: Implements deep-recursion JavaScript to locate and click radio buttons and navigation links hidden inside encapsulated Shadow Roots.
* **Bottom-Up Parsing**: Employs a "Bottom-Up" regex search strategy to isolate the most recent question content and ignore navigation sidebars or UI noise.
* **Automated Research**: Automatically queries `itexamanswers.net` for the identified question and retrieves correct answers based on the `.correct_answer` CSS class.
* **Robust Navigation**: Specialized "Next" and "Submit" handlers that iterate through all available frames to ensure the exam progresses smoothly.

## Setup & Requirements

### 1. Install Dependencies

Ensure you have Python installed, then run the following to install the necessary libraries:

```bash
pip install selenium pyautogui beautifulsoup4

```

### 2. Custom Chrome Shortcut (CRITICAL)

Because this script attaches to an existing browser session to avoid detection and maintain your login state, you **must** launch Chrome in remote debugging mode.

1. Right-click on your desktop and select **New > Shortcut**.
2. In the location field, paste the following (adjusting for your specific Chrome installation path):
`"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\sel_temp"`
3. Name the shortcut (e.g., `Chrome-Selenium`).
4. **Important**: Close all existing Chrome windows before launching this shortcut.
5. Navigate to your Netacad exam and log in manually before starting the script.

## Usage

1. Launch Chrome using the **Custom Shortcut** created above.
2. Navigate to the assessment start page.
3. Run the script:
```bash
python main.py

```

4. Enter the starting question number when prompted.
5. **Important**: Keep the Chrome window visible and avoid touching the mouse or keyboard while the `[MACRO]` is running, as it uses physical key injection to save the page.

## Technical Implementation Details

* **Interaction Logic**: The script uses a `click_element_robust` function that switches the driver context through every available iframe and shadow root until a target is resolved.
* **Parser**: Specifically targets the `.component__body-inner.mcq__body-inner` class to extract clean question text while ignoring base64 images and metadata.
* **Submission**: The `click_submit_robust` function uses an aggressive attribute scanner to find the final "Submit" button by checking `aria-labels`, `ids`, and inner text.
