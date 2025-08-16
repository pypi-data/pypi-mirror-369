import signal
import sys
import json
import os
import feedparser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QSplitter, QToolButton, QSizePolicy, 
    QTreeView, QTableView, QTextEdit, QProgressBar, QStatusBar, QTextBrowser, 
    QVBoxLayout, QWidget, QMenu, QInputDialog, QLineEdit, QMessageBox, QHeaderView
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QDesktopServices, QIcon
from PyQt5.QtCore import Qt, QPoint, QUrl, pyqtSignal, QModelIndex, QTimer, QThread

from smart_news_organizer.modules.feed     import parse_url
from smart_news_organizer.modules.dates    import normalizar_data, get_datetime, is_less_than
from smart_news_organizer.modules.files    import detect_formats, open_with_graphical_editor
from smart_news_organizer.modules.data     import SYSTEM_DATA
from smart_news_organizer.modules.wabout   import show_about_window
from smart_news_organizer.modules.consult  import summarize_news, podcast_news
from smart_news_organizer.modules.wmessage import show_message
from smart_news_organizer.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
import smart_news_organizer.about as about

CONFIG_FILE = "~/.config/smart_news_organizer/config_data.json"

config_file_path = os.path.expanduser(CONFIG_FILE)

def load_config_data(config_file_path):
    config_data = SYSTEM_DATA.copy()
    try:
        if not os.path.exists(config_file_path):
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            
            with open(config_file_path, "w", encoding="utf-8") as arquivo:
                json.dump(config_data, arquivo, indent=4)
            print(f"File created in: {config_file_path}")
            
        with open(config_file_path, "r") as arquivo:
            config_data = json.load(arquivo)

        #print("config_file_path:",config_file_path)
        #print(json.dumps(config_data, indent=4, ensure_ascii=False))        
        return config_data
        
    except FileNotFoundError:
        print(f"Error: The file '{config_file_path}' was not found.")
        return config_data
        
    except json.JSONDecodeError:
        print(f"Error: The file '{config_file_path}' dont have a valid JSON.")
        return config_data


    return config_data

config_data = load_config_data(config_file_path)


TREE_FILE = "~/.config/smart_news_organizer/tree_data.json"
tree_file_path = os.path.expanduser(TREE_FILE)

LIST_DATA = []


# Thread que vai rodar a função lenta
class WorkerSummarizeThread(QThread):
    def __init__(self,config_data, list_data):
        super().__init__() 
        self.config_data = config_data 
        self.list_data = list_data
        self.output = ""
        
    def run(self):
        self.output = summarize_news(self.config_data, self.list_data)


# Thread que vai rodar a função lenta
class WorkerPodcastThread(QThread):
    def __init__(self,config_data, list_data):
        super().__init__() 
        self.config_data = config_data 
        self.list_data = list_data
        self.output = ""
        
    def run(self):
        self.output = podcast_news(self.config_data, self.list_data)

class MyTableView(QTableView):
    doubleLeftClicked = pyqtSignal(QModelIndex)
    doubleRightClicked = pyqtSignal(QModelIndex)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            if event.button() == Qt.LeftButton:
                self.doubleLeftClicked.emit(index)
            elif event.button() == Qt.RightButton:
                self.doubleRightClicked.emit(index)
        super().mouseDoubleClickEvent(event)

class TreeModel(QStandardItemModel):
    def __init__(self, save_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_callback = save_callback

    def supportedDragActions(self):
        return Qt.MoveAction  # ou Qt.CopyAction | Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent_index):
        parent_item = self.itemFromIndex(parent_index)
        if parent_item and parent_item.data() is not None:
            return False
        return super().dropMimeData(data, action, row, column, parent_index)

    def setData(self, index, value, role):
        result = super().setData(index, value, role)
        if role == Qt.EditRole and self.save_callback:
            self.save_callback()
        return result


class TreeView(QTreeView):
    def __init__(self, parent=None, save_callback=None):
        super().__init__(parent)
        self.save_callback = save_callback

    def dropEvent(self, event):
        super().dropEvent(event)
        QTimer.singleShot(0, self.save_callback)

def getExpandedSeparator():
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return spacer

class MainWindow(QMainWindow):
    ############################################################################
    def __init__(self):
        super().__init__()

        self.setWindowTitle(about.__program_name__)
        self.setGeometry(50, 50, 1200, 800)
        
        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(icon_path)) 


        self._create_toolbar()
        self._create_central_widget()
        self._create_statusbar()

        self.load_tree_structure()
        
        # Timer para mostrar "atividade"
        self.contador = 0
        self.timer = self.startTimer(500)  # Atualiza a cada 500ms
        self.rodando = False


    ############################################################################
    def timerEvent(self, event):
        # Só mostra algo girando na barra de status
        if self.rodando:
            pontos = '.' * (self.contador % 32)
            self.status.showMessage(f"Working{pontos}")
            
            if self.contador % 2 == 0:
                self.progress.setValue(self.progress.maximum())
            else:
                self.progress.setValue(0)
            self.contador += 1
            

    ############################################################################
    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Coffee
        coffee_action = QAction(QIcon.fromTheme("emblem-favorite"),"Coffee", self)
        coffee_action.setToolTip("Buy me a coffee (TrucomanX)")
        coffee_action.triggered.connect(self.on_coffee_action_click)
        
        # About
        about_action = QAction(QIcon.fromTheme("help-about"),"About", self)
        about_action.setToolTip("About the program")
        about_action.triggered.connect(self.show_about)
        
        # Help
        help_action = QAction(QIcon.fromTheme("x-office-address-book"),"Help", self)
        help_action.setToolTip("Help information of the program")
        help_action.triggered.connect(self.show_help)
        
        # Config
        config_action = QAction(QIcon.fromTheme("document-properties"),"Configure AI", self)
        config_action.setToolTip("Configure variables of Artificial Inteligence.")
        config_action.triggered.connect(self.on_config_action_click)
        
        # Usage
        usage_action = QAction(QIcon.fromTheme("emblem-web"),"Usage", self)
        usage_action.setToolTip("Open url with AI usage information")
        usage_action.triggered.connect(self.on_usage_action_click)

        # Cria o botão com menu summarize-down
        self.summarize_button = QToolButton()
        self.summarize_button.setText("Summarize\ntitles")
        self.summarize_button.setToolTip("Summarize feed titles")
        self.summarize_button.setIcon(QIcon.fromTheme("format-text-strikethrough"))
        self.summarize_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        #self.summarize_button.setPopupMode(QToolButton.MenuButtonPopup)  
        self.summarize_button.setPopupMode(QToolButton.InstantPopup)
        # Cria o menu
        menu = QMenu()
        summarize_action1 = QAction("In last 24h", self)
        summarize_action1.triggered.connect(lambda: self.on_summarize_nh_action_click(24))
        menu.addAction(summarize_action1)
        summarize_action1 = QAction("In last week", self)
        summarize_action1.triggered.connect(lambda: self.on_summarize_nh_action_click(24*7))
        menu.addAction(summarize_action1)
        summarize_action3 = QAction("In all", self)
        summarize_action3.triggered.connect(lambda: self.on_summarize_nh_action_click(0))
        menu.addAction(summarize_action3)
        # Add menu
        self.summarize_button.setMenu(menu)


        # Cria o botão com menu find-down
        find_button = QToolButton()
        find_button.setText("Find")
        find_button.setToolTip("Find feeds with AI related to a topic")
        find_button.setIcon(QIcon.fromTheme("edit-find"))
        find_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        #find_button.setPopupMode(QToolButton.MenuButtonPopup)  
        find_button.setPopupMode(QToolButton.InstantPopup)
        # Cria o menu
        menu = QMenu()
        find_action1 = QAction("In last 24h", self)
        find_action2 = QAction("In last week", self)
        find_action3 = QAction("In all", self)
        menu.addAction(find_action1)
        menu.addAction(find_action2)
        menu.addAction(find_action3)
        # Add menu
        find_button.setMenu(menu)
        find_button.setEnabled(False)
        
        
        # Cria o botão com menu podcast-down
        self.podcast_button = QToolButton()
        self.podcast_button.setText("Podcast\nscript")
        self.podcast_button.setToolTip("Generate a podcast script from feed titles with AI")
        self.podcast_button.setIcon(QIcon.fromTheme("audio-volume-high"))
        self.podcast_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        #self.podcast_button.setPopupMode(QToolButton.MenuButtonPopup)  
        self.podcast_button.setPopupMode(QToolButton.InstantPopup)
        # Cria o menu
        menu = QMenu()
        podcast_action1 = QAction("In last 24h", self)
        podcast_action1.triggered.connect(lambda: self.on_podcast_nh_action_click(24))
        menu.addAction(podcast_action1)
        podcast_action2 = QAction("In last week", self)
        podcast_action2.triggered.connect(lambda: self.on_podcast_nh_action_click(24*7))
        menu.addAction(podcast_action2)
        podcast_action3 = QAction("In all", self)
        podcast_action3.triggered.connect(lambda: self.on_podcast_nh_action_click(0))
        menu.addAction(podcast_action3)
        # Add menu
        self.podcast_button.setMenu(menu)
        

        toolbar.addAction(coffee_action)
        toolbar.addAction(about_action)
        toolbar.addAction(help_action)
        toolbar.addAction(config_action)
        toolbar.addAction(usage_action)
        toolbar.addSeparator() # Separator
        toolbar.addWidget(getExpandedSeparator())
        toolbar.addWidget(self.summarize_button)
        toolbar.addWidget(find_button)
        toolbar.addWidget(self.podcast_button)

    ############################################################################
    def _create_central_widget(self):
        main_splitter = QSplitter(Qt.Horizontal)

        # Tree View (Left)
        self.tree_view = TreeView(save_callback=self.save_tree_structure)
        self.tree_model = TreeModel(save_callback=self.save_tree_structure)
        self.tree_model.setHorizontalHeaderLabels(["RSS tree"])

        
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_tree_context_menu)
        self.tree_view.doubleClicked.connect(self.handle_tree_double_click)
        
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setDefaultDropAction(Qt.MoveAction)  # ou Qt.CopyAction

        
        main_splitter.addWidget(self.tree_view)

        # Right splitter (TableView + TextEdit)
        right_splitter = QSplitter(Qt.Vertical)
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID","Title", "Data", "Author"])
        self.table_view = MyTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setColumnHidden(0, True)
        self.table_view.doubleLeftClicked.connect(self.on_table_left_double_click)
        self.table_view.doubleRightClicked.connect(self.on_table_right_double_click)
        self.table_view.clicked.connect(self.on_table_click)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        #header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.resizeSection(1, 500)
        header.resizeSection(2, 200)
        header.resizeSection(3, 200)
        
        self.markdown_widget = QTextBrowser()
        self.markdown_widget.setMarkdown("")
        self.markdown_widget.setMinimumHeight(50)
        fonte = QFont("Courier New")  # Ou "Monospace", "Courier", etc.
        fonte.setStyleHint(QFont.Monospace)
        self.markdown_widget.setFont(fonte)

        right_splitter.addWidget(self.table_view)
        right_splitter.addWidget(self.markdown_widget)
        right_splitter.setStretchFactor(0, 1)
 
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(1, 1)
        

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    ############################################################################
    def on_usage_action_click(self):
        QDesktopServices.openUrl(QUrl(config_data["usage"]))    

    ############################################################################
    def on_config_action_click(self):
        config_data = load_config_data(config_file_path)
        
        #QDesktopServices.openUrl(QUrl.fromLocalFile(config_file_path))
        open_with_graphical_editor(config_file_path)
        
    ############################################################################
    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    
    ############################################################################
    def on_table_right_double_click(self, index):
        pass

    ############################################################################
    def on_table_left_double_click(self, index):
        row = index.row()
        model = self.table_view.model()

        data_row = []
        for col in range(model.columnCount()):
            index_item = model.index(row, col)
            data_row.append(model.data(index_item))
        
        mydat = LIST_DATA[int(data_row[0])]
        QDesktopServices.openUrl(QUrl(mydat["link"]))
    
    ############################################################################
    def on_table_click(self, index):
        row = index.row()
        model = self.table_view.model()

        data_row = []
        for col in range(model.columnCount()):
            index_item = model.index(row, col)
            data_row.append(model.data(index_item))

        #print(f"Linha clicada: {row}")
        #print(f"Dados da linha: {data_row}")
        mydat = LIST_DATA[int(data_row[0])]
        
        D = detect_formats(mydat['summary'])
        
        maior_chave = max(D, key=D.get)
        
        if 'HTML'==maior_chave:
            description =   "<h1>"+ \
                            mydat['title']+ \
                            "</h1>\n"+ \
                            mydat['summary']
            self.markdown_widget.setHtml(description)
            
        elif 'Markdown'==maior_chave:
            description =   "# "+ \
                            mydat['title']+ \
                            "\n"+ \
                            mydat['summary']
            self.markdown_widget.setMarkdown(description)
            
        else:
            description =   mydat['title']+ \
                            "\n"+ \
                            "="*len(mydat['title'])+ \
                            "\n\n"+ \
                            mydat['summary']
            self.markdown_widget.setPlainText(description)
        
    ############################################################################
    def update_table_with_leaf_data(self, list_data):
        # 1. Limpar
        self.table_model.removeRows(0, self.table_model.rowCount())

        # Se o modelo ainda não foi definido, cria e aplica uma vez
        if not hasattr(self, 'table_model') or self.table_view.model() is None:
            self.table_model = QStandardItemModel()
            self.table_model.setHorizontalHeaderLabels(["ID","Title", "Data", "Author"])
            self.table_view.setModel(self.table_model)
            self.table_view.setSortingEnabled(True)
            self.table_view.setColumnHidden(0, True)
            self.table_view.doubleLeftClicked.connect(self.on_table_left_double_click)
            self.table_view.doubleRightClicked.connect(self.on_table_right_double_click)
            self.table_view.clicked.connect(self.on_table_click)
            self.table_view.setEditTriggers(QTableView.NoEditTriggers)
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Interactive)
            #header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.resizeSection(1, 500)
            header.resizeSection(2, 200)
            header.resizeSection(3, 200)

        # Adicionar os dados (esperando lista de dicionários com "title" e "url")
        L = len(list_data)
        self.progress.setRange(0,L)
        for i, data in enumerate(list_data):
            id_item = QStandardItem(str(i))
            title_item = QStandardItem(data.get("title","Unknown title"))
            if "published" in data:
                data_item = QStandardItem(normalizar_data(data.get("published","Unknown published"))) 
            else:
                data_item = QStandardItem(normalizar_data(data.get("updated","Unknown published"))) 
            author_item = QStandardItem(data.get("author", "Unknown author"))
            self.table_model.appendRow([id_item, title_item, data_item, author_item])
            self.progress.setValue(i+1)
        self.progress.setValue(0)
        
        #self.table_view.sortByColumn(2, Qt.DescendingOrder)

    ############################################################################
    def set_list_leaf_data_in_table_view(self,leaf_data_list):
        global LIST_DATA
        LIST_DATA=[]
        
        M = len(leaf_data_list)
        for i, item in enumerate(leaf_data_list):
            feed = feedparser.parse(item['url'])
            
            L = len(feed.entries)
            self.progress.setRange(0,L)
            for j, entry in enumerate(feed.entries):
                LIST_DATA.append(entry)
                self.progress.setValue(j+1)
            self.progress.setValue(0)
            self.status.showMessage(f"Collected feeds of leaf {i+1}/{M}",5000)
        
        
        LIST_DATA.sort(key=get_datetime, reverse=True)
        self.update_table_with_leaf_data(LIST_DATA)

    ############################################################################
    def handle_tree_double_click(self, index):
        self.status.showMessage("Searching for feeds",5000)
        self.table_view.setEnabled(False)
        item = self.tree_model.itemFromIndex(index)
        leaf_data_list = []

        def collect_leaf_data(node):
            if isinstance(node.data(), dict):
                leaf_data_list.append(node.data())
            L = node.rowCount()
            self.progress.setRange(0,L)
            for i in range(L):
                collect_leaf_data(node.child(i))
                self.progress.setValue(i+1)
            self.progress.setValue(0)
        
        collect_leaf_data(item)
        self.status.showMessage("Collected all leaf data",5000)
        
        self.set_list_leaf_data_in_table_view(leaf_data_list)
        
        self.table_view.setEnabled(True)
        self.status.showMessage("")

    ############################################################################
    def _create_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.addPermanentWidget(self.progress)

    ############################################################################
    def open_tree_context_menu(self, position: QPoint):
        index = self.tree_view.indexAt(position)
        selected_item = self.tree_model.itemFromIndex(index) if index.isValid() else None

        if selected_item is None: # nao selecionou nada
            return

        #print("")
        #print("rowCount:",selected_item.rowCount())

        menu = QMenu()
        
        add_node_action    = None
        add_leaf_action    = None
        rename_node_action = None
        rss_url_action     = None
        if selected_item.data() is None: # Es nodo
            add_node_action = menu.addAction(QIcon.fromTheme("folder-new"),"Add new node")
            add_leaf_action = menu.addAction(QIcon.fromTheme("document-new"),"Add new lead (with URL)")
            rename_node_action = menu.addAction(QIcon.fromTheme("document-edit"),"Rename")
        else: # is folha
            rss_url_action = menu.addAction(QIcon.fromTheme("insert-link"),"Copy RSS URL")
        
        menu.addSeparator()
        
        remove_action = menu.addAction(QIcon.fromTheme("edit-clear"),"Remove")  

        action = menu.exec_(self.tree_view.viewport().mapToGlobal(position))

        if action is None:# faço click fora
            return
        
        if action == add_node_action:
            name, ok = QInputDialog.getText(self, "New Node Name", "Enter the name:")
            if ok and name:
                new_item = QStandardItem(name)
                new_item.setIcon(QIcon.fromTheme("folder"))  # ícone de pasta
                if selected_item:
                    selected_item.appendRow(new_item)
                else:
                    self.tree_model.appendRow(new_item)
                self.save_tree_structure()

        elif action == rss_url_action: 
            #print("data:",selected_item.data())
            
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_item.data().get("url"))
            return
        
        elif action == add_leaf_action:
            url, ok2 = QInputDialog.getText(self, "URL", "Enter the URL:")
            url = parse_url(url)
            
            if url is None:
                QMessageBox.warning(self, "Feed error", "The URL is no valid feed.")
                return 


            if ok2 and url is not None:
                # Verifica se a URL já existe entre os filhos do nodo selecionado
                exists = False
                for row in range(selected_item.rowCount()):
                    child = selected_item.child(row)
                    data = child.data()
                    if isinstance(data, dict) and data.get("url") == url:
                        exists = True
                        break
                
                if exists:
                    QMessageBox.warning(self, "URL duplicada", "Esta URL já está presente neste nó.")
                    return

                # Criação do novo leaf
                feed = feedparser.parse(url)

                leaf_data = {
                    "title": feed.feed.get("title", "Title"),
                    "url": url,
                    "description": feed.feed.get("subtitle", "Description")
                }
                leaf_text = f"{leaf_data['title']} ({leaf_data['url']})"
                new_leaf = QStandardItem(leaf_text)
                new_leaf.setIcon(QIcon.fromTheme("application-rss+xml")) 
                new_leaf.setData(leaf_data)

                selected_item.appendRow(new_leaf)
                self.save_tree_structure()

        elif action == rename_node_action:
            if selected_item: 
                novo_nome, ok = QInputDialog.getText(self, 
                                                    "Rename Nodo", 
                                                    "New name:", 
                                                    QLineEdit.Normal, 
                                                    selected_item.text())
                if ok and novo_nome:
                    selected_item.setText(novo_nome)
                    self.save_tree_structure()

        elif action == remove_action:
            if selected_item:
                parent = selected_item.parent()
                if parent:
                    parent.removeRow(selected_item.row())
                else:
                    self.tree_model.removeRow(selected_item.row())
                self.save_tree_structure()

        
    ############################################################################
    def show_about(self):
        #QMessageBox.information(self, "Sobre", "Exemplo criado com PyQt5.\n(c) Fernando")
        
        data = {
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        
        show_about_window(data,logo_path)

    ############################################################################      
    def filter_list_data(self,complete_list_data,horas):
        list_data=[]
        for data in complete_list_data:
            if is_less_than(data,horas):
                list_data.append(data)
                #print(data.get('published_parsed'))
        return list_data
        
        
    ############################################################################      
    def on_summarize_nh_action_click(self, nh = 0):
        config_data = load_config_data(config_file_path)
        
        if config_data["api_key"] == "":
            self.on_config_action_click()
            return
    
        list_data = []
        if nh >0:
            list_data = self.filter_list_data(LIST_DATA,nh)
        else:
            list_data = LIST_DATA
        
        if len(list_data) == 0:
            QMessageBox.warning(self, 
                                "Void list", 
                                "The list is void please select a node in the left tree view.")
            return
            
        self.rodando = True       
        self.status.showMessage("Working")
        self.thread_summ = WorkerSummarizeThread(config_data, list_data)
        self.thread_summ.finished.connect(self.func_summarize_end)
        self.thread_summ.start()
        self.summarize_button.setEnabled(False)


    def func_summarize_end(self):
        self.rodando = False
        self.contador = 0
        self.status.showMessage("Ended!", 3000)  # Mostra por 3 segundos
        self.progress.setValue(0)
        show_message(self.thread_summ.output, width=800, height=600, parent = self)
        self.summarize_button.setEnabled(True)
          
          
    ############################################################################      
    def on_podcast_nh_action_click(self, nh = 0):
        config_data = load_config_data(config_file_path)
        
        if config_data["api_key"] == "":
            self.on_config_action_click()
            return
    
        list_data = []
        if nh >0:
            list_data = self.filter_list_data(LIST_DATA,nh)
        else:
            list_data = LIST_DATA
        
        if len(list_data) == 0:
            QMessageBox.warning(self, 
                                "Void list", 
                                "The list is void please select a node in the left tree view.")
            return
            
        self.rodando = True       
        self.status.showMessage("Working")
        self.thread_podcast = WorkerPodcastThread(config_data, list_data)
        self.thread_podcast.finished.connect(self.func_podcast_end)
        self.thread_podcast.start()
        self.podcast_button.setEnabled(False)


    def func_podcast_end(self):
        self.rodando = False
        self.contador = 0
        self.status.showMessage("Ended!", 3000)  # Mostra por 3 segundos
        self.progress.setValue(0)
        show_message(self.thread_podcast.output, width=800, height=600, parent = self)
        self.podcast_button.setEnabled(True)
          
    ############################################################################
    def show_help(self):
        QDesktopServices.openUrl(QUrl("https://github.com/trucomanx/SmartNewsOrganizer/tree/main/doc"))
     
    ############################################################################   
    def save_tree_structure(self):
        # SERIALIZAÇÃO DO TREEVIEW
        def serialize_item(item):
            data = {
                'text': item.text(),
                'user_data': item.data(),
                'children': [serialize_item(item.child(i)) for i in range(item.rowCount())]
            }
            return data

        root_items = [self.tree_model.item(i) for i in range(self.tree_model.rowCount())]
        data = [serialize_item(item) for item in root_items]

        with open(tree_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    ############################################################################
    def load_tree_structure(self):
        import os
        if not os.path.exists(tree_file_path):
            root_item = QStandardItem("Root")
            self.tree_model.appendRow(root_item)
            return

        def deserialize_item(data):
            item = QStandardItem(data['text'])
            item.setData(data.get('user_data'))
            if data.get('user_data',None) is None:
                item.setIcon(QIcon.fromTheme("folder"))
                item.setEditable(True)
            else:
                item.setIcon(QIcon.fromTheme("application-rss+xml"))
                item.setEditable(False)

            for child_data in data['children']:
                item.appendRow(deserialize_item(child_data))
            return item

        with open(tree_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item_data in data:
            self.tree_model.appendRow(deserialize_item(item_data))

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) # xprop WM_CLASS # *.desktop -> StartupWMClass
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()

