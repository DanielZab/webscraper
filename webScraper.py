from bs4 import BeautifulSoup
import requests
import logging

class WebScraper:
    def getHTML(self, url: str) -> str:
        # Gets the HTML from a URL
        logging.debug('getHTML started')

        # Perfrom GET request
        response = requests.get(url)

        # Check if response is OK
        if (response.ok):
            return response.text
        else:
            return None
        
    def extractAttributes(self, elements: list, attrList: list) -> list:
        # Extracts the attributes of a tag from a list of elements and filters out None values
        logging.debug('extractAttributes started')

        # Get the attributes of the elements
        attributes = []
        for e in elements:
            l = []
            for f in attrList:
                attr = e.attrs.get(f, "")

                # Convert lists to string
                if type(attr) == list:
                    attr = " ".join(attr)

                l.append(attr)
            attributes.append(l)

        # Filter out None-only values
        attributes = list(filter(lambda x: not all(not y for y in x), attributes))

        # Join the attributes to a comma separated string
        res = []
        for a in attributes:
           
            addition = ",".join(a)
            res.append(addition)

        return res
    
    def getElementsWithTag(self, html: str, tag: str) -> list:
        # Gets all elements with a certain tag from HTML
        logging.debug('getElementsWithTag started')
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all(tag)
    
    def getHTMLText(self, html: str) -> str:
        # Gets the text  of a HTML string
        logging.debug('getHTMLText started')
        
        # Get the text from the HTML
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

        # Remove double newlines
        for i in range(0, 100):
            text = text.replace("\n\n", "\n")
        return text