import waybacktrack


def main():
    flinks, duds = waybacktrack.archive_domain(domain='www.foxnews.com',
                                               year=2017,
                                               dir_path='cnn/2017',
                                               percent=10,
                                               debug=True)

    with open("foxnews_links.txt", 'w') as file:
        for flink in flinks:
            if "htm" in flink:
                file.write(flink[flink.find('http'):])


if __name__ == "__main__":
    main()