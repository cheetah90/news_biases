from lxml import html
import os


def main():
    all_files = os.listdir('foxnews/')
    for filename in all_files:
        if filename.endswith("html"):
            with open(filename) as file:
                content = file.read()

            tree = html.fromstring(content)
            el = tree.xpath("//div[contains(@class, 'article-text')]")
            if len(el) > 1:
                print("There are more than one article-content class in this html. Something is wrong!")
                raise Exception("More than one article-content element in the ")




if __name__ == "__main__":
    main()