import waybacktrack


def main():
    open("foxnews_links.txt", 'w')
    flinks, duds = waybacktrack.archive_domain(domain='www.foxnews.com/politics.html',
                                               year=2017,
                                               dir_path='cnn/2017',
                                               percent=100,
                                               debug=True)
    # rss.cnn.com/rss/cnn_allpolitics.rss
    # www.foxnews.com/politics.html

if __name__ == "__main__":
    main()