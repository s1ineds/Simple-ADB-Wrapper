import sys, subprocess, re
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMessageBox,
    QStatusBar
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Android Debug Bridge Wrapper")
        self.setWindowIcon(QIcon("img\\app-icon-16px.png"))

        self.widget = QWidget()
        
        self.layout = QVBoxLayout()
        self.nestedLayout1 = QHBoxLayout()
        self.nestedLayout2 = QHBoxLayout()
        self.nestedLayout3 = QHBoxLayout()
        self.nestedLayout4 = QHBoxLayout()
        self.nestedLayout5 = QHBoxLayout()
        
        self.deviceLabel = QLabel()
        self.checkConnectionButton = QPushButton("Check connection")
        self.getAppListButton = QPushButton("Get apps")
        self.appList = QListWidget()
        self.uninstallButton = QPushButton("Uninstall")
        self.searchField = QLineEdit()
        self.searchField.setFixedSize(QSize(210, 25))
        self.searchButton = QPushButton()
        self.searchButton.setIcon(QIcon("img\\search-32px.png"))
        self.searchButton.setFixedSize(QSize(30, 30))
        self.searchButton.setEnabled(False)
        self.statusBar = QStatusBar()
        self.statusLabel = QLabel()
        self.statusBar.addWidget(self.statusLabel)

        self.appList.itemClicked.connect(self.selectItem)
        self.checkConnectionButton.clicked.connect(self.check_device_connection)
        self.getAppListButton.clicked.connect(self.getApps)
        self.uninstallButton.clicked.connect(self.uninstallApp)
        self.searchField.textChanged.connect(self.refreshList)
        self.searchButton.clicked.connect(self.filterList)
        
        self.nestedLayout1.addWidget(self.checkConnectionButton)
        self.nestedLayout1.addWidget(self.deviceLabel)
        self.nestedLayout2.addWidget(self.getAppListButton)
        self.nestedLayout2.addWidget(self.searchField)
        self.nestedLayout2.addWidget(self.searchButton)
        self.nestedLayout3.addWidget(self.appList)
        self.nestedLayout4.addWidget(self.uninstallButton)
        self.nestedLayout5.addWidget(self.statusBar)

        self.layout.addLayout(self.nestedLayout1)
        self.layout.addLayout(self.nestedLayout2)
        self.layout.addLayout(self.nestedLayout3)
        self.layout.addLayout(self.nestedLayout4)
        self.layout.addLayout(self.nestedLayout5)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
    
    # метод, который проверяет подключение устройства
    def check_device_connection(self):
        # выполняем команду и захватывает вывод
        self.output = subprocess.run(args="tools\\platform-tools-windows\\adb.exe devices", capture_output=True)
        # преобразуем вывод и сохраняем в переменной tmp
        self.tmp = str(self.output)
        # с помощью regex выделяем идентификатор подключенного устройства
        self.tmp = re.findall("[A-Z\d]{16}", self.tmp)
        # устанавиливаем индентификатор в label
        self.deviceLabel.setText(self.tmp[0])
    
    # метод, который получает и формирует список приложений
    def getApps(self):
        # если label, в который вывыводится идентификатор устройства - пустой,
        # (скорей всего устройство не подключено)
        # то создаем MessageBox с сообщением пользователю
        if self.deviceLabel.text() == "":
            self.emptyListWarning = QMessageBox()
            self.emptyListWarning.setText("The app list is empty. Check connection with device.")
            self.emptyListWarning.setIcon(QMessageBox.Icon.Warning)
            self.emptyListWarning.exec()
        else:
            # если label, в который вывыводится идентификатор устройства - не пустой,
            # (устройство скорей всего подключено)
            # то очищаем список приложений
            self.appList.clear()
            # делаем кнопку поиска активной
            self.searchButton.setEnabled(True)
            # выполняем команду получения списка приложений из подключенного устройства
            self.output = subprocess.run(args="tools\\platform-tools-windows\\adb.exe shell pm list packages", capture_output=True)
            # сохраняем результат выполнения команды в переменную tmp
            self.tmp = str(self.output.stdout)
            # результат выполнения команды типа str. Между названиями приложений
            # содержит символы \\r и \\n. Поэтому разбиваем строку по этим символам и
            # записываем результат в переменную tmp, которая уже является списком.
            # В результате, получится список приложений в виде ["package:com.android.chrome", "package:kz.onay"]
            self.tmp = self.tmp.split('\\r\\n')
            # создаем переменную, в которой храним индекс прилоежний для последующей вставки в виджет списка
            self.listIndex = 0
            # бежим по нашему списку tmp, при этом отсекаем последний символ при помощи среза
            for item in self.tmp[:-1]:
                # так как, название приложения содержит в себе слово package и символ : (package:com.android.chrome)
                # находим индекс двоеточия и сохраняем в переменной separatorIndex
                self.separatorIndex = item.index(":")
                # создаем элемент виджета списка
                self.list_item = QListWidgetItem()
                # устанавливаем текст для элемента списка при этом,
                # при помощи среза отсекаем все что находится слева от двоеточия, т.е. слово package
                # чтобы имя приложения не содержало самого двоеточия, указываем +1
                self.list_item.setText(item[self.separatorIndex+1:])
                # устанавливаем иконку для элемента списка
                self.list_item.setIcon(QIcon("img\\app-16px.png"))
                # добавляем элемент в виджет, передав в метод индекс элемента списка
                # и сам созданный элемент
                self.appList.insertItem(self.listIndex, self.list_item)
                # увеличиваем переменную индекса на 1
                # следующий элемент будет под индексом 2
                self.listIndex += 1
                # показываем в статус баре количество приложений
                self.statusLabel.setText(f"Number of apps: {str(self.appList.count())}")

    # метод-событие, которое получает выбранный на данный момент элемент списка
    def selectItem(self):
        # получаем выбранный на данный момент элемент списка и сохраняем в переменной current_item
        self.current_item = self.appList.currentItem()
        # выводим в консоль выбранный элемент
        print(self.current_item.text())

    # метод, который по нажатию кнопки удаляет приложение
    def uninstallApp(self):
        # если текущий выбранный элемент пусто (т.е. ничего не выбрано)
        if not self.current_item.text():
            # то создаем MessageBox
            self.emptySelectionWarning = QMessageBox()
            # устанавливаем текст, который покажем пользователю
            self.emptySelectionWarning.setText("No app is selected.")
            # устанавливаем иконку для сообщения
            self.emptySelectionWarning.SetIcon(QMessageBox.Icon.Warning)
            # выводим сообщение
            self.emptySelectionWarning.exec()
        # если текущий выбранный элемент не пустой (т.е. что-то выбрано)
        else:
            # то выполняем команду удаление и захватываем результат выполнения команды    
            self.output = subprocess.run(args=f"tools\\platform-tools-windows\\adb.exe shell pm uninstall -k --user 0 {self.current_item.text()}", 
                                         capture_output=True)
            # выводим на экран результат выполнения команды
            print(self.output)
            # удаляем текущий выбранный элемент из списка (takeItem)
            # передав в него номер текущего выбранного элемента
            self.appList.takeItem(self.appList.currentRow())
    
    # метод, который выполняет поиск по списку
    def filterList(self):
        # определяем переменную, в которой храним индекс элемента
        self.index = 0
        # если поле для поиска не пустое
        if len(self.searchField.text()) > 0:
            # то очищаем виджет списка
            self.appList.clear()
            # забираем из поля поиска введенный текст и сохраняем в переменной search_text
            self.search_text = self.searchField.text()
            # бежим по списку с приложениями, который сформировали в методе getApps
            for item in self.tmp[:-1]:
                # проверяем, если текст поиска содержится в текущем элементе списка
                if self.search_text in item:
                    # то находим индекс двоеточия
                    self.separatorIndex = item.index(":")
                    # создаем элемент списка
                    self.search_list_item = QListWidgetItem()
                    # устанавливаем текст для элемента списка при этом,
                    # при помощи среза отсекаем все что находится слева от двоеточия, т.е. слово package
                    # чтобы имя приложения не содержало самого двоеточия, указываем +1
                    self.search_list_item.setText(item[self.separatorIndex+1:])
                    # устанавливаем иконку для элемента списка
                    self.search_list_item.setIcon(QIcon("img\\app-16px.png"))
                    # увеличиваем переменную индекса на 1
                    # следующий элемент будет под индексом 2
                    self.index += 1
                    # вставляем элемент списка, передав в функцию insertItem индекс элемента
                    # и текст
                    self.appList.insertItem(self.index, self.search_list_item)
    
    # метод, который обновляет список
    def refreshList(self):
        # если поле поиска приложений пустое
        if len(self.searchField.text()) < 1:
            # то вызываем метод getApps чтобы заново сформировать список приложений
            self.getApps()
            
app = QApplication(sys.argv)

window = MainWindow()
window.setFixedSize(QSize(515, 400))
window.show()

app.exec()