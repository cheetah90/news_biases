from lxml import html
import os
import re
import utils


def main():
    # Change this corpus_flag according to corpus that you are parsing
    corpus_flag = 'foxnews'
    #corpus_flag = 'cnn'


    all_files = os.listdir(corpus_flag + '/')
    for filename in all_files:
        path_to_file = corpus_flag + '/' + filename
        if filename.endswith("html") and os.path.isfile(path_to_file):
            with open(path_to_file) as file:
                content = file.read()

            tree = html.fromstring(content)

            # start to parse
            el = tree.xpath("//div[contains(@class, 'article-text')]")
            if len(el) > 1:
                print("There are more than one article-content class in this html. Something is wrong!")
                raise Exception("More than one article-content element in the ")

            context_text = ""

            xpath_expre = '//p' if corpus_flag == 'foxnews' else "//*[contains(@class, 'zn-body__paragraph')]"

            for paragraph in tree.xpath(xpath_expre):
                if paragraph.tag == 'p' and corpus_flag == 'cnn':
                    if paragraph.getchildren():
                        paragraph_content = paragraph.getchildren()[0].tail
                else:
                    paragraph_content = paragraph.text

                if paragraph_content is not None:
                    # clean up the CR and convert utf-8 to ascii
                    paragraph_content = utils.unicodetoascii(paragraph_content.replace("\\n","").replace("\\t",""))

                    # clean up mysterious quadruple \\\\
                    paragraph_content = paragraph_content.replace("\\", "").strip().replace("  ", " ")

                    # get rid of the first couple of lines
                    if paragraph_content != 'b\'' and paragraph_content != 'By' and len(paragraph_content) != 0:
                        context_text = context_text + paragraph_content + " "


            # add an EOF sign at the end
            context_text = context_text.replace("©", "")
            context_text += "©"

            if not os.path.exists(corpus_flag + "/content/"):
                os.makedirs(corpus_flag + "/content/")

            if os.path.exists(corpus_flag + "/content/" + filename):
                print("Already parsed! Ignore!")
            else:
                with open(corpus_flag + "/content/" + filename.replace('html', 'txt'), 'w+') as article_file:
                    article_file.write(context_text)






if __name__ == "__main__":
    main()