from data_collection import waybacktrack


def main():
    open("foxnews_links.txt", 'w')
    waybacktrack.archive_domain(domain='rss.cnn.com/rss/cnn_allpolitics.rss',
                                               year=2017,
                                               dir_path='cnn/',
                                               percent=100,
                                               debug=True)
    # rss.cnn.com/rss/cnn_allpolitics.rss
    # www.foxnews.com/politics.html

if __name__ == "__main__":
    main()