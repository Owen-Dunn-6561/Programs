import tkinter
from operator import indexOf
from random import random, randrange

from bs4 import BeautifulSoup
from tkinter import *
from tkinter.ttk import *
import requests

turn_count = 0

def main():


    def name_select(event):

        global turn_count

        curr_name = title_box.get()
        curr_index = indexOf(title, curr_name)

        # title_result = Label(m_window, text=curr_name)


        if curr_index + 1 == answer_rank :
            title_color = "green"
        else:
            title_color = "gray"
        title_result = tkinter.Label(m_window, text=curr_name, bg=title_color)
        title_result.grid(row=2 * turn_count + 1, column=0)
        # title_result.pack()

        quant_feedback(rank, curr_index, "Rank: ", 2 * turn_count + 1, 1)
        quant_feedback(volumes, curr_index, "Volumes: ", 2 * turn_count + 1, 2)
        quant_feedback(popularity, curr_index, "Popularity: ", 2 * turn_count + 2, 0)
        quant_feedback(timeline, curr_index, "Start Date: ", 2 * turn_count + 2, 1)

        demo_text = "Demographic: " + str(demographic[curr_index])[1:-1].replace("\'", "")
        if demographic[curr_index] == demographic[answer_rank - 1]:
            demo_color = "green"
        elif list(set(demographic[curr_index]) & set(demographic[answer_rank - 1])):
            demo_color = "yellow"
        else:
            demo_color = "gray"
        demo_label = tkinter.Label(m_window, text=demo_text, bg=demo_color)
        demo_label.grid(row=2 * turn_count + 2, column=2)
        # demo_label.pack()

        turn_count += 1


    def search_title(event):
        search_list = []
        if title_box.get() != "":
            for entry in title:
                if title_box.get().lower() in entry.lower():
                    search_list.append(entry)

        title_box.config(values=search_list)

    def quant_feedback(category, index, description, c_row, c_col):

        diff = int(category[index]) - int(category[answer_rank - 1])
        if (int(category[index]) == 0):
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
        # panel.pack()


    page_scope = 1
    manga_id = []
    title = []
    rank = list(range(1, page_scope * 50 + 1))
    volumes = []
    timeline = []
    popularity = []
    demographic = []

    answer_rank = randrange(1, (page_scope * 50 + 1), 1)

    get_data(page_scope, manga_id, title, rank, volumes, timeline, popularity, demographic)

    # print(title[answer_rank - 1] + ", rank: " + str(answer_rank) + ", volumes: " + volumes[answer_rank - 1] + ", start: " + timeline[answer_rank - 1] + ", pop: " + popularity[answer_rank - 1] + ", demo: " + str(demographic[answer_rank - 1]))



    m_window = tkinter.Tk(screenName="Guess the Manga", baseName=None, className='Guess the Manga', useTk=1)

    info_box = Label(m_window, text='Guess a Manga. The rules are like Wordle and stuff.')
    info_box.grid(row=0, column=0)
    #info_box.pack()

    title_box = Combobox(m_window, values=[])
    title_box.bind('<KeyRelease>', search_title)
    title_box.grid(row=0, column=1)
    # title_box.pack()

    submit_button = Button(m_window, text='submit')
    submit_button.bind('<Button>', name_select)
    submit_button.grid(row=0, column=2)
    # submit_button.pack()

    m_window.mainloop()




def get_data(page_scope, manga_id, title, rank, volumes, timeline, popularity, demographic):

    soup = []
    raw_text = []

    for n in range(page_scope):
        site_URL = requests.get("https://myanimelist.net/topmanga.php?limit=" + str(n * 50))
        site_URL.raise_for_status()
        soup = BeautifulSoup(site_URL.content, 'html.parser')
        for line in str(soup).splitlines():
            raw_text.append(line)

    page_scope *= 50

    get_name_and_id(raw_text, manga_id, title)
    get_timeline_and_volumes(soup, timeline, volumes)
    get_demo_and_pop(manga_id, title,page_scope, demographic, popularity)


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


def get_demo_and_pop(manga_id, title,page_scope, demographic, popularity):
    indiv_url: str

    for n in range(page_scope):
        # while
        indiv_url = requests.get(("https://myanimelist.net/manga/" + manga_id[n] + "/" + title[n]).replace(" ", "_"))
        indiv_url.raise_for_status()
        # raw_select = BeautifulSoup(indiv_url.content, 'html.parser')
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
        pop_select = str(soup.find_all('span', class_="numbers popularity"))
        popularity.append((pop_select.removeprefix("[<span class=\"numbers popularity\">Popularity <strong>#").removesuffix("</strong></span>]")))


main()
