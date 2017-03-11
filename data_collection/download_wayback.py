import waybacktrack


def main():
    open("foxnews_links.txt", 'w')
    flinks, duds = waybacktrack.archive_domain(domain='www.foxnews.com/politics.html',
                                               year=2017,
                                               dir_path='foxnews',
                                               percent=100,
                                               debug=True)

if __name__ == "__main__":
    main()