import wx
import wx.lib.scrolledpanel
from webScraper import WebScraper
import logging

class UIManager:
    def __init__(self) -> None:
        # Initialize the UI

        logging.debug('UIManager started')
        app = wx.App()
        
        self.createMainFrame()
        self.webScraper = WebScraper()

        app.MainLoop()
    
    def createMainFrame(self) -> None:
        # Create the main frame
        logging.debug('createMainFrame started')

        frame = wx.Frame(None, title="DarthScraper", size=(800, 600))

        # Create the main panel
        main_panel = wx.Panel(frame)
        main_panel.SetBackgroundColour("white")

        # Split main panel in two halves with a sizer
        sizer = wx.GridSizer(1, 2, (2,0))

        # Create each half separately
        sizer.Add(self.createLeftPanel(main_panel), 1, wx.EXPAND)
        sizer.Add(self.createRightPanel(main_panel), 1, wx.EXPAND)

        main_panel.SetSizer(sizer)   

        # Show the frame
        frame.Layout()
        frame.Show()

    def createLeftPanel(self, main_panel: wx.Panel) -> wx.Panel:
        # Create the left side of the main panel
        logging.debug('createLeftPanel started')

        # Create a border panel to add padding
        border_panel = wx.Panel(main_panel)
        border_sizer = wx.BoxSizer(wx.VERTICAL)
        border_panel.SetBackgroundColour("white")

        # Create the actual panel
        panel = wx.Panel(border_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add url label and text box
        urlLabel = wx.StaticText(panel, label="URL")
        sizer.Add(urlLabel, 0, wx.BOTTOM, 10)
        self.urlBox = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, name="url")
        sizer.Add(self.urlBox, 0, wx.EXPAND | wx.BOTTOM, 30)

        # Add filter radio buttons
        self.filter_radio = wx.RadioBox(panel, choices=["All", "Text", "Links", "Images"], name="filter", label="Filter")
        sizer.Add(self.filter_radio, 0, wx.EXPAND | wx.BOTTOM, 30)

        # Add filename label and text box
        fileLabel = wx.StaticText(panel, label="Filename")
        sizer.Add(fileLabel, 0, wx.BOTTOM, 10)
        self.fileBox = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, name="file")
        sizer.Add(self.fileBox, 0, wx.EXPAND | wx.BOTTOM, 30)

        # Add confirm and preview buttons
        buttonPanel = wx.Panel(panel)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        confirmButton = wx.Button(buttonPanel, label="Confirm")
        confirmButton.Bind(wx.EVT_BUTTON, self.onConfirm)
        previewButton = wx.Button(buttonPanel, label="Preview")
        previewButton.Bind(wx.EVT_BUTTON, self.onPreview)
        buttonSizer.Add(previewButton, 0, wx.RIGHT, 10)
        buttonSizer.Add(confirmButton, 0, wx.RIGHT, 10)
        buttonPanel.SetSizer(buttonSizer)

        sizer.Add(buttonPanel, 0, wx.ALIGN_RIGHT, 0)

        panel.SetSizer(sizer)

        border_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 50)
        border_panel.SetSizer(border_sizer)
        return border_panel
    
    def createRightPanel(self, main_panel: wx.Panel) -> wx.Panel:
        # Create the right side of the main panel
        logging.debug('createRightPanel started')

        # Create a border panel to add padding
        border_panel = wx.Panel(main_panel)
        border_sizer = wx.BoxSizer(wx.VERTICAL)
        border_panel.SetBackgroundColour("white")

        # Create preview label
        self.preview_label = wx.StaticText(border_panel, label="Preview")

        # Create preview panel with scrolling function
        self.preview_panel = wx.lib.scrolledpanel.ScrolledPanel(border_panel, style=wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL, name="result")
        self.preview_panel.SetupScrolling()
        self.preview_panel.SetBackgroundColour("white")

        # Create sizer for preview panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create preview text
        self.preview_text = wx.StaticText(self.preview_panel, label="", style=wx.ST_ELLIPSIZE_END)
        sizer.Add(self.preview_text, 0, wx.EXPAND, 0)

        self.preview_panel.SetSizer(sizer)

        # Add preview label and panel to border panel
        border_sizer.Add(self.preview_label, 0, wx.TOP | wx.LEFT, 50)
        border_sizer.Add(self.preview_panel, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 50)
        border_panel.SetSizer(border_sizer)
        return border_panel

    def onPreview(self, event):
        # Preview the result
        logging.debug('onPreview started')

        # Check if URL is empty
        if (self.urlBox.GetValue() == ""):
            self.setPreview("Enter a URL!")
            return

        # Try to get HTML from URL
        try:
            html = self.webScraper.getHTML(self.urlBox.GetValue())
        except:
            logging.error(f"Error getting HTML: {e}")
            self.setPreview("Invalid URL")
            return
        
        # Check which filter is selected and preview the result
        if (self.filter_radio.GetStringSelection() == "All"):

            # Set preview to full HTML
            self.setPreview(html)
        elif (self.filter_radio.GetStringSelection() == "Text"):

            # Set preview to text
            self.setPreview(self.webScraper.getHTMLText(html))
        elif (self.filter_radio.GetStringSelection() == "Links"):

            # Set preview to id, class and href of all links
            linkTags = self.webScraper.getElementsWithTag(html, "a")
            self.setPreview("\n".join(self.webScraper.extractAttributes(linkTags, ["id", "class", "href"])))
        elif (self.filter_radio.GetStringSelection() == "Images"):

            # Set preview to id, class, src and alt of all images
            images = self.webScraper.getElementsWithTag(html, "img")
            self.setPreview("\n".join(self.webScraper.extractAttributes(images, ["id", "class", "src", "alt"])))
    
    def setPreview(self, text: str):
        # Set the preview text
        logging.debug('setPreview started')

        # Check if text is too long and cut it off if necessary
        if (len(text) > 10000):
            logging.debug('setPreview: text too long')
            text = text[:10000]
        
        # Set the preview text and wrap it
        self.preview_text.SetLabel(text)
        self.preview_text.Wrap(self.preview_panel.GetSize()[0] - 100)
        self.preview_panel.SetupScrolling(scrollToTop=False)

    def onConfirm(self, event):
        # Extract info and create the .csv file
        logging.debug('onConfirm started')

        # Check if URL is empty
        if (self.urlBox.GetValue() == ""):
            self.setPreview("Enter a URL!")
            return
        
        # Check if filename is empty
        if (self.fileBox.GetValue() == ""):
            self.setPreview("Enter a filename!")
            return
        
        # Try to get HTML from URL
        try:
            html = self.webScraper.getHTML(self.urlBox.GetValue())
        except Exception as e:
            logging.error(f"Error getting HTML: {e}")
            self.setPreview("Invalid URL")
            return
        
        # Check which filter is selected and create the file
        if (self.filter_radio.GetStringSelection() == "All"):

            # Create file with full HTML
            self.createFile(self.fileBox.GetValue(), html)
        elif (self.filter_radio.GetStringSelection() == "Text"):

            # Create file with text
            self.createFile(self.fileBox.GetValue(), self.webScraper.getHTMLText(html))
        elif (self.filter_radio.GetStringSelection() == "Links"):

            # Create file with id, class and href of all links
            linkTags = self.webScraper.getElementsWithTag(html, "a")
            self.createFile(self.fileBox.GetValue(), "\n".join(self.webScraper.extractAttributes(linkTags, ["id", "class", "href"])))
        elif (self.filter_radio.GetStringSelection() == "Images"):

            # Create file with id, class, src and alt of all images
            images = self.webScraper.getElementsWithTag(html, "img")
            self.createFile(self.fileBox.GetValue(), "\n".join(self.webScraper.extractAttributes(images, ["id", "class", "src", "alt"])))

    def createFile(self, filename, text):
        # Create the file
        logging.debug('createFile started')
        # Create the file and write the text to it
        try:
            with open("files/" + filename + ".csv", "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logging.error(f"Error writing to file: {e}")
            self.setPreview("Error writing to file")
