import tkinter
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
import os
from operator import indexOf
from random import random, randrange
from bs4 import BeautifulSoup
import requests
import time

turn_count = 0

def main():

# Handle empty box error?
# Work on importing images to use for game.
# Clean up GUI.

    def start_game(page_scope):

        def name_select(event):

            global turn_count

            curr_name = title_box.get()
            curr_index = indexOf(title, curr_name)

            if curr_index + 1 == answer_pop:
                title_color = "green"
                '''img = ImageTk.PhotoImage(Image.open("https://cdn.myanimelist.net/images/manga/2/255379.jpg"))
                win_panel = tkinter.label(m_window, image=img)
                win_panel.pack()'''
                # ^Work on this


            else:
                title_color = "gray"
            title_result = tkinter.Label(m_window, text=curr_name, bg=title_color)
            title_result.grid(row=2 * turn_count + 1, column=0)

            quant_feedback(popularity, curr_index, "Popularity: ", 2 * turn_count + 1, 1)
            quant_feedback(volumes, curr_index, "Volumes: ", 2 * turn_count + 1, 2)
            quant_feedback(rank, curr_index, "Rank: ", 2 * turn_count + 2, 0)
            quant_feedback(timeline, curr_index, "Start Date: ", 2 * turn_count + 2, 1)

            demo_text = "Demographic: " + str(demographic[curr_index])[1:-1].replace("\'", "")
            if demographic[curr_index] == demographic[answer_pop - 1]:
                demo_color = "green"
            elif list(set(demographic[curr_index]) & set(demographic[answer_pop - 1])):
                demo_color = "yellow"
            else:
                demo_color = "gray"
            demo_label = tkinter.Label(m_window, text=demo_text, bg=demo_color)
            demo_label.grid(row=2 * turn_count + 2, column=2)

            turn_count += 1

        def search_title(event):
            search_list = []
            if title_box.get() != "":
                for entry in title:
                    if title_box.get().lower() in entry.lower():
                        search_list.append(entry)

            title_box.config(values=search_list)

        def quant_feedback(category, index, description, c_row, c_col):

            global turn_count

            diff = int(category[index]) - int(category[answer_pop - 1])
            if int(category[index]) == 0:
                panel_text = description + "?"
            else:
                panel_text = description + str(category[index])

            panel_color = 'gray'
            if diff == 0:
                panel_color = 'green'
            elif abs(diff) <= 10:
                panel_color = 'yellow'
            if diff > 0:
                panel_text += " v"
            elif diff < 0:
                panel_text += " ^"

            panel = tkinter.Label(m_window, text=panel_text, bg=panel_color)
            panel.grid(row=c_row, column=c_col)

        turn_count = 0

        m_window = tkinter.Tk(screenName="Guess the Manga", baseName=None, className='Guess the Manga', useTk=1)


        answer_pop = randrange(1, (page_scope * 50 + 1), 1)

        info_box = Label(m_window, text='Guess a Manga. The rules are like Wordle and stuff.')
        info_box.grid(row=0, column=0)

        title_box = Combobox(m_window, values=[])
        title_box.bind('<KeyRelease>', search_title)
        title_box.grid(row=0, column=1)

        submit_button = Button(m_window, text='submit')
        submit_button.bind('<Button>', name_select)
        submit_button.grid(row=0, column=2)

        retry_button = Button(m_window, text='retry', command=lambda: [m_window.destroy(), start_game(page_scope)])
        retry_button.grid(row=0, column=3)

        m_window.mainloop()



    page_scope = 1
    manga_id = []
    title = []
    rank = []
    volumes = []
    timeline = []
    popularity = list(range(1, page_scope * 50 + 1))
    demographic = []

    get_data(page_scope, manga_id, title, rank, volumes, timeline, popularity, demographic)
    start_game(page_scope)


# START DATA COLLECTION
# _____________________
def get_data(page_scope, manga_id, title, rank, volumes, timeline, popularity, demographic):

    print("Gathering Data. This may take a minute...")

    soup = []
    raw_text = []


    for n in range(page_scope):
        if n > 0:
            site_URL = requests.get("https://myanimelist.net/topmanga.php?type=bypopularity&limit=" + str(n * 50))
        else:
            site_URL = requests.get("https://myanimelist.net/topmanga.php?type=bypopularity")
        site_URL.raise_for_status()
        soup = BeautifulSoup(site_URL.content, 'html.parser')
        for line in str(soup).splitlines():
            raw_text.append(line)

    page_scope *= 50

    get_name_and_id(raw_text, manga_id, title)
    get_timeline_and_volumes(soup, timeline, volumes)
    get_demo_and_rank(manga_id, title,page_scope, demographic, rank)


def get_name_and_id(full_HTML: [], manga_id: [], title: []):

    pre_string = "<h3 class=\"manga_h3\"><a class=\"hoverinfo_trigger fs14 fw-b\" href=\"https://myanimelist.net/manga/"
    index = 0

    for line in full_HTML:
        if pre_string in line:
            manga_id.append(line.removeprefix(pre_string).split("/")[0])
            title.append(line.removeprefix(pre_string + manga_id[index] +  "/").split("\"")[0].replace("_", " "))

            index += 1


def get_timeline_and_volumes(soup, timeline, volumes):

    counter = 0
    for line in str(soup.find_all('div', class_="information di-ib mt4")).splitlines():
        if (counter + 2) % 4 == 0:
            timeline.append(line.split(" ")[9])
        elif "vols" in line:
            volumes.append(line.removesuffix(" vols)<br/>")[-2:].replace("(", "").replace("?", "0"))
        counter += 1


def get_demo_and_rank(manga_id, title,page_scope, demographic, rank):
    indiv_url: str

    for n in range(page_scope):

        time.sleep(2)
        indiv_url = requests.get(("https://myanimelist.net/manga/" + manga_id[n] + "/" + title[n]).replace(" ", "_"))
        indiv_url.raise_for_status()
        soup = BeautifulSoup(indiv_url.content, 'html.parser')
        raw_select = str(soup.find_all('div', class_="leftside")).splitlines()

        demo_string = []
        if "<span class=\"dark_text\">Demographic" not in str(raw_select):
            demo_string.append("None")
        else:
            if "/manga/genre/41/Seinen" in str(raw_select):
                demo_string.append("Seinen")
            if "/manga/genre/25/Shoujo" in str(raw_select):
                demo_string.append("Shoujo")
            if "/manga/genre/27/Shounen" in str(raw_select):
                demo_string.append("Shounen")
            if "/manga/genre/42/Josei" in str(raw_select):
                demo_string.append("Josei")
            if "/manga/genre/15/Kids" in str(raw_select):
                demo_string.append("Kids")
        demographic.append(demo_string)
        rank_select = str(soup.find_all('span', class_="numbers ranked"))
        rank.append((rank_select.removeprefix("[<span class=\"numbers ranked\" title=\"based on the top anime page. Please note that \'Not yet aired\' and \'R18+\' titles are excluded.\">Ranked <strong>#").removesuffix("</strong></span>]")))

# END DATA COLLECTION
# ___________________

main()
