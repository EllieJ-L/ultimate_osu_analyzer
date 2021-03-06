from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from gui.objects.group import Group
from gui.objects.scene import Scene

from misc.callback import callback



class LayerManagerItem(QTreeWidgetItem):

    def __init__(self, parent, path, data):
        self.layer = data
        self.path  = path
        columns = (self.layer.name, )

        QTreeWidgetItem.__init__(self, parent, columns)
        
        self.setCheckState(0, Qt.Checked)  # Set checked on 0th column


    def layer_enable_event(self):
        # Set visibility to whatever the check state is
        self.layer.setVisible(self.checkState(0)) 
        self.layer.layer_changed()



class LayerManagerGroupItem(QTreeWidgetItem):

    def __init__(self, parent, path, name):
        QTreeWidgetItem.__init__(self, parent, [ name ])
        self.setCheckState(0, Qt.Checked)  # Set checked on 0th column
        self.path = path


    def layer_enable_event(self):
        # Set visibility to whatever the check state is
        for child_idx in range(self.childCount()):
            self.child(child_idx).setCheckState(0, self.checkState(0))
            self.child(child_idx).layer_enable_event()



class LayerManager(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.init_gui_elements()
        self.construct_gui()
        self.update_gui()


    def init_gui_elements(self):
        self.layout     = QVBoxLayout()
        self.layer_list = QTreeWidget()

        self.scene     = Scene()
        self.hierarchy = { '.' : [ self.layer_list, {} ] }
        '''
        { 
            '.' : [
                self.layer_list, 
                {
                    <subgroup> : [
                        LayerManagerGroupItem,
                        <subgroup> : [
                            ...
                        ]
                    ],
                    <subgroup> : [
                        LayerManagerGroupItem,
                        <subgroup> : [
                            ...
                        ]
                    ]
                }
            ]
        }
        '''


    def construct_gui(self):
        self.setLayout(self.layout)
        self.layout.addWidget(self.layer_list)


    def update_gui(self):
        self.layer_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.layer_list.customContextMenuRequested.connect(self.__right_click_menu)

        self.layer_list.header().setStretchLastSection(False)
        self.layer_list.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.layer_list.header().hide()

        self.layer_list.itemClicked.connect(self.__check_item_status)


    def add_layer(self, path, layer):
        group = self.__set_groups(path)
        group[1][layer.name] = [ LayerManagerItem(group[0], path, layer), {} ]

        self.scene.add_layer(layer)

        print(self.hierarchy)


    def get_scene(self):
        return self.scene


    def __set_groups(self, path):
        group_names = path.split('.')
        curr_group  = self.hierarchy['.']

        for group_name in group_names:
            if not group_name in curr_group[1]:
                self.__set_group(curr_group, path, group_name)
            curr_group = curr_group[1][group_name]

        return curr_group


    def __set_group(self, group, path, group_name):
        group[1][group_name] = [ LayerManagerGroupItem(group[0], path, group_name), {} ]


    def __get_group_parent(self, path):
        group_names = path.split('.')
        curr_group  = self.hierarchy['.']

        for group_name in group_names[:-1]:
            curr_group = curr_group[1][group_name]

        return curr_group


    def __check_item_status(self, item):
        item.layer_enable_event()


    def __remove(self, item):
        if type(item) == type(None): 
            return

        if type(item) == LayerManagerItem:
            self.scene.rmv_layer(item.layer)
            item.parent().removeChild(item)

        elif type(item) == LayerManagerGroupItem:
            for _ in range(item.childCount()):
                self.__remove(item.child(0))

            parent = self.__get_group_parent(item.path)[0]
            if type(parent) == QTreeWidget:
                parent.takeTopLevelItem(parent.indexOfTopLevelItem(item))
            elif type(parent) == LayerManagerGroupItem:
                parent.removeChild(item)
            else:
                print('[ ERROR ] Unexpected layer parent type', type(parent))

            self.__get_group_parent(item.path)[1] = {}

        else:
            print('[ ERROR ] item type', type(item))
            

    def __right_click_menu(self, pos):
        item = self.layer_list.itemAt(pos)
        if item == None: return

        remove_action = QAction('&Remove')
        remove_action.setStatusTip('Removes layer or group')
        remove_action.triggered.connect(lambda _, item=item: self.__remove(item))

        menu = QMenu(self)
        menu.addAction(remove_action)
        menu.exec(self.mapToGlobal(pos))