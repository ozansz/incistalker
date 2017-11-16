import requests
from lxml import html
from collections import namedtuple
import sys

SVF_PAGE_HEADER = "\n" + "=" * 10 + "[{}]" + "=" * 10 + "\n"
SVF_ENT_HEADER = "\n" + "##> {}\n"

EntryData = namedtuple("Entry", ["entry_num", "entry_text", "entry_links"])

def showusage():
    raise NotImplementedError("Must write some shit here.")

def get_page_tree(url, use_session=False):
    if use_session:
        _getter = requests.Session()
    else:
        _getter = requests

    pg = _getter.get(url)
    if pg.status_code != 200:
        return pg.status_code

    return html.fromstring(pg.content.decode("utf-8"))

def get_whole_page(url, logger=None):
    tree = get_page_tree(url)
    if type(tree) == type(int()):
        if logger:
            logger.error("Status code {0} returned from page {1}.".format(
                tree, url))
        return None

    page_data = list()

    entries = tree.xpath("//ol[@class='entry-list']/li[@value]")
    for entry in entries:
        #print(entry.values())
        entry_num = int(entry.values()[1])

        try:
            entry_text_tree = entry.xpath(".//div[@class='entry-text-wrap ']")[0]
        except:
            try:
                entry_text_tree = entry.xpath(".//div[@class='entry-text-wrap uzunEntry']")[0]
            except Exception as e:
                raise RuntimeError("Unexpected error :" + e)

        entry_text = entry_text_tree.text_content()

        entry_links = [(a.text_content(), a.iterlinks().__next__()[2])
            for a in entry_text_tree.xpath(".//a")]

        page_data.append(EntryData(entry_num, entry_text, entry_links))

    return page_data

if __name__ == "__main__":
    if len(sys.argv) != 5:
        showusage()
        sys.exit(1)

    url = sys.argv[1]
    page_start = int(sys.argv[2])
    page_end = int(sys.argv[3])
    save_file_name = sys.argv[4]

    save_file = open(save_file_name, "w")

    print("[*] URL     :", url)
    print("[*] Pages   : {0}-{1}".format(page_start, page_end))
    print("[*] Save to :", save_file_name)

    for pgnum in range(page_start, page_end + 1):
        print("\n[i] Getting page", pgnum)

        if url.endswith("/"):
            _url = url + str(pgnum) + "/"
        else:
            _url = url + "/" + str(pgnum) + "/"
        print("[DEBUG] URL:", _url)

        page_data = get_whole_page(_url)
        if page_data == None:
            print("[!] An error has ocuured.")
            sys.exit(2)

        save_file.write(SVF_PAGE_HEADER.format(pgnum))

        for entry in page_data:
            print("  => Entry #" + str(entry.entry_num))

            save_file.write(SVF_ENT_HEADER.format(entry.entry_num))
            save_file.write("\n" + entry.entry_text + "\n\n")

            if len(entry.entry_links) != 0:
                for link in entry.entry_links:
                    save_file.write(link[0] + " => " + link[1] + "\n")
