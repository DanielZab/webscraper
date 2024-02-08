from ui import UIManager
import logging

def main():

    logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)

    logging.info('Started')
    
    ui = UIManager()

if __name__ == "__main__":
    main()