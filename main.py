import math
import time
import os
import pyautogui
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
FILENAME_START = "Cisco Networking Academy_"
FULL_PATH = os.path.join(DOWNLOAD_DIR, FILENAME_START)
file_path = 0
def connect_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver

def save_page_macro(driver):
    global file_path
    print(f"\n>> [MACRO] Clicking screen center to FOCUS exam frame...")
    
    driver.switch_to.default_content()
    driver.maximize_window()
    
    size = driver.get_window_size()
    center_x = math.ceil(size['width'] * 0.9)
    center_y = math.ceil(size['height'] * 0.9)
    
    pyautogui.click(center_x, center_y)
    time.sleep(0.5)

    print(f"   [MACRO] Sending Ctrl+S...")
    pyautogui.hotkey('ctrl', 's')

    time.sleep(1)
    
    print("   [WAITING] Writing to disk...")
    time.sleep(8)
    
    download_dir = os.listdir(DOWNLOAD_DIR)
    for file in download_dir:
        if file.find(FILENAME_START) != -1:
            file_path = os.path.join(DOWNLOAD_DIR, file)
            return True
    return False

def parse_local_file_raw_regex_bottom_up():
    print(f"   [PARSER] Reverse Search (Bottom-Up) for 'component__body-inner'...")
    time.sleep(3)    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
            
        line_list = raw_content.splitlines()
        print("List length: ",len(line_list))

        start_index = raw_content.rfind("component__body-inner mcq__body-inner")
        end_index = raw_content.find("\n", start_index)

        line = raw_content[ start_index : end_index ]

        open_p_find = line.rfind("<p>")
        close_p_find = line.rfind("</p>")

        if close_p_find != -1:
            line = line[open_p_find + 3: close_p_find]

            print(line)
            print(f"indices = {open_p_find} : {close_p_find}")
        
        else:

            if "->" in line:
                line = line[line.rfind("->")+2:]

            if "</div>" in line:
                line = line.replace("/div", "")
            
        if "<b>" in line:
                line = line.replace("<b>", "")
                print(line)
                line = line.replace("</b>", "")
                print(line)


        if line[0] == '>':
            line = line[1:]

        print(line)

        return line

        
    except Exception as e:
        messagebox.showerror("RuntimeError", f"Failed to find matches. Exception: {e}")
        raise Exception("No matches")
    
def get_answer_fast(driver, question_text):
    original_window = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get("https://itexamanswers.net/")
    found = []
    try_count = 0
    while found == []:
        if try_count == 4:
            raise Exception("Cannot find the answers :C")
        try:
            try_count += 1
            wait = WebDriverWait(driver, 2)
            time.sleep(1)
            search = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='s'], .search-field")))
            search.clear()
            
            print(f"question_text = {question_text}")

            query = question_text[:60].replace("\n", " ")

            print(f"query = {query}")

            search.send_keys(query)
            
            search.send_keys(Keys.RETURN)
            
            time.sleep(2)

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "article h2 a, h3 a"))).click()
            
            time.sleep(2)

            reds = driver.find_elements(By.CSS_SELECTOR, ".correct_answer, [style*='color: red'], [style*='color: #ff0000']")
            
            time.sleep(2)

            print(f"reds = {reds}")

            found = list(set([el.text.strip() for el in reds if len(el.text.strip()) > 1 and "Correct Answer" not in el.text]))

            print(f"found = {found}")

        except: pass

        finally:
            driver.close()
            driver.switch_to.window(original_window)
    try_count = 0
    return found

def click_element_robust(driver, target_type, target_value):
    JS_SHADOW_CLICK = """
        let targetType = arguments[0];
        let targetValue = arguments[1] ? arguments[1].toLowerCase() : "";
        
        function deepClick(root) {
            if (!root) return false;
            
            // 1. DEFINE CANDIDATES
            let candidates = [];
            if (targetType === "next_btn") {
                // Look for Next Buttons
                candidates = root.querySelectorAll('button, div[role="button"], span[role="button"], .next-btn, .footer-navigation-next-btn');
            } else {
                // Look for Answer Choices (Labels, Inputs, Radio containers)
                candidates = root.querySelectorAll('label, input, .mat-radio-button, .mat-checkbox, .answer-option');
            }
            
            // 2. CHECK CANDIDATES
            for (let el of candidates) {
                // Ensure visible
                if (el.offsetParent === null) continue;
                
                if (targetType === "next_btn") {
                    let txt = (el.innerText || "").toLowerCase();
                    let aria = (el.getAttribute("aria-label") || "").toLowerCase();
                    if (txt.includes("next") || aria.includes("next")) {
                        el.click();
                        return true;
                    }
                } else {
                    // Answer Matching
                    let txt = (el.innerText || "").toLowerCase();
                    // We match if the element contains the answer snippet
                    if (txt.includes(targetValue)) {
                        el.click();
                        return true;
                    }
                }
            }
            
            // 3. RECURSE INTO SHADOW DOM
            // Standard querySelector cannot see inside #shadow-root, so we walk the tree
            let walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while(node = walker.nextNode()) {
                if (node.shadowRoot) {
                    if (deepClick(node.shadowRoot)) return true;
                }
            }
            return false;
        }
        
        return deepClick(document);
    """

    driver.switch_to.default_content()
    if driver.execute_script(JS_SHADOW_CLICK, target_type, target_value):
        return True

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    
    for i in range(len(frames)):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(i)
            
            if driver.execute_script(JS_SHADOW_CLICK, target_type, target_value):
                return True
        except:
            continue
            
    return False

def click_submit_robust(driver):
    JS_SUBMIT_HUNT = """
        function deepClick(root) {
            if (!root) return false;
            
            // 1. Candidate Selectors including specific ion-button and material variants
            let candidates = root.querySelectorAll('button, input[type="submit"], div[role="button"], span[role="button"], .ion-button, .mat-button, .mat-raised-button');
            
            for (let el of candidates) {
                // Must be visible
                if (el.offsetParent === null) continue;
                
                let txt = (el.innerText || "").toLowerCase().trim();
                let aria = (el.getAttribute("aria-label") || "").toLowerCase();
                let val = (el.value || "").toLowerCase(); 
                let id = (el.id || "").toLowerCase();
                
                // 2. Keyword Matching for various final-state buttons
                if (txt.includes("submit") || txt.includes("finish") || txt.includes("complete") ||
                    aria.includes("submit") || aria.includes("finish") || 
                    val.includes("submit") || id.includes("submit")) {
                    
                    el.scrollIntoView();
                    el.click();
                    return true;
                }
            }
            
            // 3. Shadow DOM Recursion (Crucial for NetAcad components)
            let walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while(node = walker.nextNode()) {
                if (node.shadowRoot) {
                    if (deepClick(node.shadowRoot)) return true;
                }
            }
            return false;
        }
        return deepClick(document);
    """

    driver.switch_to.default_content()
    try:
        if driver.execute_script(JS_SUBMIT_HUNT):
            return True
    except:
        pass

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for i in range(len(frames)):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(i)
            if driver.execute_script(JS_SUBMIT_HUNT):
                return True
        except:
            continue
            
    return False

def delete_file():
    for file in os.listdir(DOWNLOAD_DIR):
        if FILENAME_START in file:
            file_name = os.path.join(DOWNLOAD_DIR, file)
            os.remove(file_name)
            print(f"Deleted {file_name}")

def main():
    delete_file()
    driver = connect_driver()
    
    start_num = 11
    current_num = start_num
    
    print(f"\nRaw 'Ctrl+S' & Regex Search. Starting at Q{current_num}...\n")
    
    while True:
        try:
            if not save_page_macro(driver):
                print("Save failed.")
                print(FULL_PATH)
                raise RuntimeError("Cannot find saved file or save failed.")
            
            print(file_path)
            q_text = parse_local_file_raw_regex_bottom_up()
            
            if not q_text:
                print(f"Could not find Question {current_num} in the saved file.")
                print(f"             Please ensure the exam frame is visible/active.")
                time.sleep(3)
                continue

            print(f"\n------------------------------------------------")
            print(f">> [FOUND LOCALLY] {q_text[:80]}...")
            
            answers = get_answer_fast(driver, q_text)
            
            print(f"answers = {answers}")

            if answers:
                print(f"{answers}")
                
                driver.switch_to.default_content()
                for ans in answers:
                    snippet = ans[:40].strip()
                    
                    if click_element_robust(driver, "text", snippet):
                        print(f"Clicked answer starting with: '{snippet[:15]}...'")
                    else:
                        print(f"Could not click answer: '{snippet[:15]}...'")
            else:
                print("No online match found.")
                raise RuntimeError(f"No matches. q_text = {q_text}")

            time.sleep(2)
            
            size = driver.get_window_size()
            pyautogui.click(math.ceil(size['width'] * 0.9), math.ceil(size['height'] * 0.95))
            time.sleep(3) 
            delete_file()

        except KeyboardInterrupt: break
        except Exception as e:
            print(f"   [ERROR] {e}")
            delete_file()
            raise Exception("Error occurred.")
            

if __name__ == "__main__":
    main()