import sys
import time
import threading
import requests
from datetime import datetime
from tkinter import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

timeout = 5


# Class that handling the upfile site .
class Upfile(object):
    # create list of links and password
    def __init__(self):
        self.urls = []

    # Add links and passwords to 3 lists
    def add_list(self, url_given, pass_key=None):
        if pass_key is not None:
            self.urls.append((url_given, pass_key))
            send_log("{0} Added.".format(get_song_name(url_given)))
        else:
            self.urls.append((url_given, "None"))
            send_log("{0} Added.".format(get_song_name(url_given)))

    # Keeps error away by downloading link by link and not all together
    def start_threading(self):
        lock = threading.Lock()
        threads = []
        if self.urls is not None:
            for li in self.urls:
                if li[1] == "None":
                    t = threading.Thread(target=download_page, args=(lock, li[0], "None"))
                else:
                    t = threading.Thread(target=download_page, args=(lock, li[0], li[1]))
                threads.append(t)
                t.start()


# Give the song name from the link
def get_song_name(url_given):
    ans = ""
    r2 = requests.get(url_given)
    with open("site.txt", "w") as fd:
        fd.write(r2.text)
    with open("site.txt", "r") as fd:
        for line in fd.readlines():
            if "</title>" in line:
                ans = line[line.find(">") + 1:line.rfind("UpFile") - 10]
    open("site.txt", "w").close()
    return ans


#  Send messages to txt_box in UI
def send_msg_to_tk(string):
    txt.insert(END, str("\n" + string))


# Checking site and give the user info about it (password or not, deleted and others) .
def url_check():
    url2 = ent1.get().strip()
    r3 = requests.get(url2)
    if "הקובץ מוגן בסיסמא" in r3.text:
        send_log("Song name - {0} with password.".format(get_song_name(url2)))
    elif "סוג הקובץ" in r3.text:
        send_log("Song name - {0} without pass.".format(get_song_name(url2)))
    elif "קובץ הורדה לא נמצא" in r3.text:
        send_log("Error: {0} - file deleted.".format(url2))
    else:
        send_log("Error while trying to get - {0} UNKNOWN error.".format(url2))


# send errors and status to log and to GUI
def send_log(text):
    with open("log.txt", "a") as fd:
        fd.write(text + '\n')
        send_msg_to_tk(text)


# ADD links to the lists from Upfile Class
def add_link():
    global r
    url = ent1.get().strip()
    pass_url = ent2.get().strip()
    r = requests.get(url)
    if "הקובץ מוגן בסיסמא" in r.text:
        a.add_list(url, pass_url)
    else:
        a.add_list(url_given=url)
    ent1.delete(0, END)
    ent2.delete(0, END)


# RESTARTING THE PROGRAM
def start():
    btn1.configure(state='normal')
    btn2.configure(state='normal')
    btn3.configure(state='normal')
    txt.delete(1.0, END)
    ent1.delete(0, END)
    ent2.delete(0, END)
    send_log("NEW SESSION STARTED AT {0}\nAdd links"
             .format(datetime.now().strftime("%d/%m/%Y %H:%M:")))


# close last tab
def close_last_tab(driver1):
    if len(driver1.window_handles) == 2:
        driver1.switch_to.window(window_name=driver1.window_handles[-1])
        driver1.close()
        driver1.switch_to.window(window_name=driver1.window_handles[0])


# Click all the necessary buttons for downloading
def download_page(lock, url_given, pass_word):
    # check if download is over
    def every_downloads_chrome(driver):
        if not driver.current_url.startswith("chrome://downloads"):
            driver.get("chrome://downloads/")
        return driver.execute_script("""
            var items = document.querySelector('downloads-manager')
                .shadowRoot.getElementById('downloadsList').items;
            if (items.every(e => e.state === "COMPLETE"))
                return items.map(e => e.fileUrl || e.file_url);
            """)

    try:
        with lock:
            chromeOptions = Options()
            chromeOptions.add_extension(sys.path[0] + '/AdBlockerExt/extension_4_42_0_0.crx')
            driver = webdriver.Chrome(executable_path=sys.path[0] + '/chromedriver/chromedriver',
                                      options=chromeOptions)
            driver.maximize_window()
            time.sleep(1)
            close_last_tab(driver)
            driver.get(url_given)
            time.sleep(2)
            if pass_word == "None":
                pass
            else:
                psd_textbox = driver.find_element(By.CSS_SELECTOR, '#downloadContent > form > input.input_text')
                psd_textbox.send_keys(str(pass_word))
                submit_btn = driver.find_element(By.CSS_SELECTOR, '#downloadContent > form > input.simple_submit')
                submit_btn.click()
                send_log("password sent")
            send_log("Trying to Download:{0}".format(get_song_name(url_given)))
            time.sleep(5)
            # הכן קובץ להורדה
            driver.find_element(By.CSS_SELECTOR, '#abc').click()
            time.sleep(12)
            # לחץ להורדה
            driver.find_element(By.CSS_SELECTOR, '#dl > input[type=submit]').click()
            time.sleep(2)
            # waits for all the files to be completed and returns the paths
            WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
            driver.close()
            send_log("Successfully Downloaded: {0}".format(get_song_name(url_given)))
    except Exception as e:
        driver.close()
        send_log("Error while trying to download> {0}.\nError:{1}".format(url_given, e))


#  Create the design of the program
def design():
    global ent1, btn1, lbl1, lbl2, txt, ent2, btn3, btn4, btn5, txt, btn2, a
    a = Upfile()
    window = Tk()
    window.title('Bar Maizel - Upfile downloader Project ITsafe')
    window.title('Bar Maizel - Upfile downloader Project ITsafe')
    window.geometry("600x700")
    window.resizable(False, False)
    window.attributes('-topmost', True)
    btn2 = Button(window, text="Add link", command=add_link, state='disabled', width=10, height=2,
                  font=('david', 20, 'bold'))
    btn2.place(x=450, y=30)
    lbl1 = Label(window, text="link:", font=('david', 20, 'bold'))
    lbl1.place(x=15, y=50)
    ent1 = Entry(window, width=37)
    ent1.place(x=70, y=50)
    btn1 = Button(window, text="Check link", fg='orange', command=url_check,
                  state='disabled', width=10, height=2, font=('david', 20, 'bold'))
    btn1.place(x=450, y=100)

    btn3 = Button(window, text="Start Downloads", command=a.start_threading, state='disabled',
                  width=12, height=2, fg='green', font=('david', 20, 'bold'))
    btn3.place(x=225, y=170)

    btn4 = Button(window, text="Start", command=start, state='normal',
                  width=10, height=2, fg='green', font=('david', 20, 'bold'))
    btn4.place(x=20, y=170)

    btn5 = Button(window, text="Exit", command=quit, state='normal', width=10, height=2,
                  fg='red', font=('david', 20, 'bold'))
    btn5.place(x=450, y=170)

    lbl2 = Label(window, text="Password: ", font=('david', 20, 'bold'))
    lbl2.place(x=15, y=130)
    ent2 = Entry(window, width=20)
    ent2.place(x=130, y=130)

    txt = Text(window, font=('david', 15, 'bold'), width=52)
    txt.place(x=15, y=230)
    start()
    window.mainloop()


design()  # Starting the program
