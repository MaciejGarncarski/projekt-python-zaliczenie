from ftplib import error_perm
from math import floor, log, pow

from PyQt5.QtCore import QTimer


def delete_items_of_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                delete_items_of_layout(item.layout())


def is_directory(ftp, name):
    try:
        ftp.cwd(name)
        ftp.cwd('..')

        return True
    except:
        return False

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB")
   unit_index = int(floor(log(size_bytes, 1024)))
   power = pow(1024, unit_index)
   size = round(size_bytes / power, 2)

   return f"{size} {size_name[unit_index]}"


def clear_tree_widget(tree_widget):
        while tree_widget.topLevelItemCount() > 0:
            tree_widget.takeTopLevelItem(0)

def defer_ui_change(callback):
    QTimer.singleShot(0, callback)
