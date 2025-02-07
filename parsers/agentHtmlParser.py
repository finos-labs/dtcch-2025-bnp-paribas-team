from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
def parse_html(absolute_path):

    f = open(absolute_path, "r")

    soup = BeautifulSoup(f.read(), features="lxml")

    print(soup.getText())

    return soup.getText()