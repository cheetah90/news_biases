from lxml import html
import os
import re
import utils


def main():
    flag = 'foxnews'
    #flag = 'cnn'


    if flag == 'foxnews':
        all_files = os.listdir('foxnews/')
        for filename in all_files:
            path_to_file = 'foxnews/' + filename
            if filename.endswith("html") and os.path.isfile(path_to_file):
                with open(path_to_file) as file:
                    content = file.read()

                tree = html.fromstring(content)
                el = tree.xpath("//div[contains(@class, 'article-text')]")
                if len(el) > 1:
                    print("There are more than one article-content class in this html. Something is wrong!")
                    raise Exception("More than one article-content element in the ")

                context_text = ""
                for paragraph in tree.xpath('//p'):
                    if paragraph.text is not None:
                        # clean up the CR and convert utf-8 to ascii
                        paragraph_content = utils.unicodetoascii(paragraph.text.replace("\\n","").replace("\\t",""))

                        # clean up mysterious quadruple \\\\
                        paragraph_content = paragraph_content.replace("\\", "").strip().replace("  ", " ")

                        # get rid of the first couple of lines
                        if paragraph_content != 'b\'' and paragraph_content != 'By' and len(paragraph_content) != 0:
                            context_text = context_text + paragraph_content + " "


                # add an EOF sign at the end
                context_text = context_text.replace("©", "")
                context_text += "©"

                if not os.path.exists("foxnews/content/"):
                    os.makedirs("foxnews/content/")

                if os.path.exists("foxnews/content/" + filename):
                    print("Already parsed! Ignore!")
                else:
                    with open("foxnews/content/" + filename.replace('html', 'txt'), 'w+') as article_file:
                        article_file.write(context_text)






if __name__ == "__main__":
    main()