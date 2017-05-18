"""waybacktrack.py
Use this to extract Way Back Machine's
url-archives of any given domain!
TODO: reiterate entire design!
"""
import time
import os
import urllib.request as request
from urllib.error import HTTPError
import random
import re


from lxml import html
from lxml.html import clean

ARCHIVE_DOMAIN = "http://web.archive.org"

CURR_DIR = os.path.dirname(__file__)

DATASET_DIR = os.path.join(CURR_DIR, '../../dataset/')


def does_url_match_yyyymmdd(url_string):
    date_reg_exp = re.compile('\d{4}[/]\d{2}[/]\d{2}')
    all_matches = date_reg_exp.findall(url_string)

    return True if len(all_matches) > 0 else False


def is_url_political_news(url_string):
    return True if "htm" in url_string and "politics" in url_string and does_url_match_yyyymmdd(url_string) else False


def write_to_file(current_snapshot_flinks):
    # TODO: remove the duplicates forward links
    with open("foxnews_links.txt", 'a') as file:
        for flink in current_snapshot_flinks:
            if is_url_political_news(flink):
                file.write(flink[flink.find('http'):])
                file.write('\n')


def parse_calendar_for_domain_snapshots(calendarurl, year, domain):
    try:
        content = request.urlopen(calendarurl).read().decode("utf-8")
        regex = re.escape(str(year)) + r"\d{10}"
        all_timestamps = re.findall(regex, content)
        all_snapshots = ['/web/' + ts + '/http://' + domain for ts in all_timestamps]

        return all_snapshots
    except HTTPError:
        print("Errors when trying to get a list of domain snapshots from {}".format(calendarurl))


def archive_domain(domain, year, dir_path=DATASET_DIR,
                   percent=0, debug=False, throttle=1):
    """
    domain
    @type domain: string
    @param domain: the domain of the website ie. www.nytimes.com
    @type year: int
    @param year: the year to extract archives from
    @type dir_path: string
    @param dir_path: the directory path to store archive, if
                     empty, directory will automatically be created
                     TODO: Think of better solution to storing
                     downloaded archives
    @type percent: int
    @param percent: the percentage of Way Back archives to crawl
    @rtype:
    @return: Returns a list of archived sites
    """
    # TODO: Improve this for module portability
    # WARNING: Module will likely break if used outside of
    # crawl-to-the-future project
    # automatically find or eventually create directory
    # based off domain name

    # Found way to check if file is being ran in crawl-to-the-future
    # super "hacky" though
    # TODO: Find better way to check if module is getting ran in
    # in crawl-to-the-future project
    # if os.path.split(
    #         os.path.abspath(os.path.join(__file__, os.pardir)))[1] != "Way-Back":
    #     raise Exception("Please manually specify 'dir_name' value")

    if dir_path is DATASET_DIR:
        dir_path = os.path.join(dir_path, domain + '/')

    if not os.path.exists(dir_path):
        # raise IOError("[Errno 2] No such file or directory: '" + dir_path + "'")
        # this part is shady
        os.makedirs(dir_path)

    if not isinstance(dir_path, str):
        raise Exception("Directory - third arg. - path must be a string.")

    calendarcaptures_url = ARCHIVE_DOMAIN + "/__wb/calendarcaptures?url=http://" + domain + "&selected_year=" + str(year)

    domain_snapshots = parse_calendar_for_domain_snapshots(calendarcaptures_url, year, domain)

    # Allen: this is the old method which parse the html page of the waybackmachine.
    # ia_year_url = ARCHIVE_DOMAIN + "/web/" + str(year) + \
    #               "*/http://" + domain + "/"
    #
    # ia_parsed = html.parse(ia_year_url)
    #
    # domain_snapshots = list(set(ia_parsed.xpath('//*[starts-with(@id,"' + str(year) + '-")]//a/@href')))

    # snapshot_age_span is a percentage of total snapshots to process from
    # the given year
    # ie. if percent is 100, and there are a total of 50 snapshots for
    # www.cnn.com, we will crawl (to a depth of 1 atm) all 50 snapshots
    snapshot_age_span = 1 if percent <= 0 \
        else len(domain_snapshots) - 1 \
        if percent >= 100 \
        else int(percent * len(domain_snapshots) / 100)

    if debug:
        print("Extracting links from: ", domain)

        # http://margerytech.blogspot.com/2011/06/python-get-last-directory-name-in-path.html
        print("Current directory: ", os.path.split(
            os.path.abspath(os.path.join(__file__, os.pardir)))[1])

        print("Storing files in: ", os.path.abspath(dir_path))

        print("Number of domain snapshots: ", len(domain_snapshots))

        print("Number of domain snapshots to process: ", snapshot_age_span + 1)

    random.shuffle(domain_snapshots)

    forward_links = []

    # for snapshot in domain_snapshots[:snapshot_age_span]:
    snapshots_pools = domain_snapshots[:3] if 'foxnews' in domain else domain_snapshots
    for snapshot in snapshots_pools:

        curr_snapshot_flinks = get_forwardlink_snapshots(snapshot)

        write_to_file(curr_snapshot_flinks)

        forward_links.extend(curr_snapshot_flinks)

        if debug:
            print("snapshot url: ", snapshot)

            print("forward link count: ", len(curr_snapshot_flinks))

        # archive forward links
        archived_links = []
        duds = []
        for forwardlink in forward_links:
            if is_url_political_news(forwardlink):
                if archive(forwardlink, year, dir_path, debug, throttle):
                    archived_links.append(forwardlink)
                else:
                    duds.append(forwardlink)

        if debug:
            print("Number of archived forward links: ", len(archived_links))
            print("Number of duds: ", len(duds))


# I know I'm breaking so many rules by not seperating concerns
def archive(page, year, dir_path, debug=False, throttle=1):
    """
    Check to see if downloaded forward link
    satisfies the archival year specification
    ie. (2000, 2005, 2010)
    """
    # files = [f for f in os.listdir(dir_path) if os.path.isfile(f)]
    if debug:
        print("requesting ", page)

    #page_file = page.rsplit('/web/')[1].replace('http://', '').replace('-', '_')
    page_file = page[page.find('http'): ]
    page_file = page_file.replace('/', '_').replace(':', '_').replace('&', '_')
    page_file = page_file.replace('?', '_').replace('*', '_').replace('=', '_')

    file_path = dir_path + page_file
    if os.path.isfile(file_path):
        if debug:
            print ("Already saved: ", page_file)
            print()
        return False

    try:
        #current_download_url = ARCHIVE_DOMAIN + page
        current_download_url = page[page.find('http'):]
        #allen: not using the archive since it might not exist
        html_file = request.urlopen(current_download_url)
    except IOError:
        if debug:
            print ("Failed to open request for ", current_download_url)
            print()
        return False

    if html_file.getcode() == 302:
        if debug:
            print ("Got HTTP 302 response for ", current_download_url)
            print()
        return False

    html_string = str(html_file.read())

    if html_string.find("HTTP 302 response") != -1:
        if debug:
            print ("Got HTTP 302 response for ", current_download_url)
            print()
        return False

    archival_year_spec = ARCHIVE_DOMAIN + '/web/' + str(year)

    #page_url = html_file.geturl()
    #hack - since I directly donwload the current version. The next if statement does not hold


    if debug:
        print ("saving ", current_download_url)
        print()

    try:
        with open(file_path, 'w') as f:
            f.write(html_string)

        time.sleep(throttle)

    except IOError as e:
        if debug:
            print ("Got error: ", e)
        return False

    return True


def get_forwardlink_snapshots(parent_site):
    """
    @type index: string
    @param index: the index.html page from which to extract forward links
    @type year: int
    @param year: the year to extract archives from
    """
    try:
        parsed_parent_site = html.parse(ARCHIVE_DOMAIN + parent_site)
    except IOError:
        print ("Did not get extract links in ", ARCHIVE_DOMAIN + parent_site)
        return []

    if 'foxnews' in parent_site:


        cleaner = clean.Cleaner(scripts=True, javascript=True, comments=True,
                                style=True, meta=True, processing_instructions=True, embedded=True,
                                frames=True, forms=True, kill_tags=["noscript", "iframe", "img"])

        parsed_parent_site = cleaner.clean_html(parsed_parent_site)

        # spec archival year
        # check to see if the archival year of a forwark link
        # is that of the parent (ie. 2000|2005|2010)
        xpath_expre = '//a[starts-with(@href,"' + parent_site[:9] + '")]/@href'
        all_forwardlinks = parsed_parent_site.xpath(xpath_expre)

    elif 'cnn' in parent_site:
        all_forwardlinks = [element.text for element in parsed_parent_site.xpath('//guid')]


    return all_forwardlinks