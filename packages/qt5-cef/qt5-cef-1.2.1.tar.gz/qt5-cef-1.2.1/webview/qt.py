import sys
import os
import base64
import time
import subprocess
import platform
import signal
import logging
from PyQt5 import QtCore
from threading import Event, Thread
import webview.constant as constant
from cefpython3 import cefpython as cef
from uuid import uuid4
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import hashlib
import webbrowser

is_ip_set_domain = True

splash = None  # 闪屏界面
third_party_client_pid_lists = []  # 记录应用生命周期中所启动的第三方应用程序的PID
third_party_client_launch_status = {}  # 记录每个第三方应用当前启动状态{ -1: 未启动,  0: 启动中,  1: 已启动 }
pixel_ratio = 1
screen_width = 0
screen_height = 0
qt_class_name = constant.qt_class_name
default_window_width = constant.default_window_width
default_window_height = constant.default_window_height
default_window_title = constant.default_window_title
default_nest_window_margin = constant.default_nest_window_margin
min_window_width = constant.min_window_width
min_window_height = constant.min_window_height
cef_sdk = constant.burgeon_cef_sdk_js
language_locale = constant.language_locale

global_icon_path = ''
app_cef_cache_path = ''
app_version_info = 'No Version Info Specified'
app_inject_obj = {}

debug_mode = False

# dpi 所对应的缩放比
dpi_dict = {
    '96': 1,
    '120': 1.25,
    '144': 1.5,
    '168': 1.75,
    '192': 2
}


# 打点记录每个页面加载情况
def record_page_monitor(browser, data):
    global app_inject_obj
    global app_cef_cache_path
    if 'BuriedPoint' in app_inject_obj.keys():
        app_inject_obj['BuriedPoint'].add_embed_page_operate(data[0])
    if app_cef_cache_path != '':
        browser.ExecuteFunction('window.python_cef.increaseMonitor', data)


class Dialog(QDialog):
    def __init__(self, params={}, view=None):
        super(Dialog, self).__init__()
        default_params = {
            'topBgColor': '#2a5596',
            'topFontSize': 24,
            'buttonBgColor': '#2a5596',
            'buttonHoverBgColor': '#153D7A',
            'middleFontColor': '#2a5596',
            'middleFontSize': 16,
            'title': 'Dialog Title',
            'description': 'Description Info',
            'dialogWidth': 360,
            'dialogHeight': 201,
            'leftButtonText': 'Left Button',
            'rightButtonText': 'Right Button',
            'leftButtonAction': 'emit',
            'rightButtonAction': 'cancel',
            'buttonWidth': 110,
            'buttonHeight': 34,
            'buttonFontSize': 16,
            'borderRadius': 0,
            'blurRadius': 20,
            'customizedData': {}
        }
        default_params.update(params)
        global pixel_ratio
        if platform.system() == 'Windows':
            pixel_ratio = dpi_dict[str(self.logicalDpiX())]
            default_params['borderRadius'] = 6
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.view = view
        self.pixel_ratio = pixel_ratio
        self.m_drag = False
        self.m_DragPosition = 0
        self.params = default_params
        self.init()
        self.init_style()
        # self.show()
        # q = QEventLoop()
        # q.exec_()
        self.exec_()

    def init(self):
        action = {
            'close': self.quit_app,
            'cancel': self.close,
            'emit': self.emit_event_to_browser
        }
        width = self.params['dialogWidth'] * self.pixel_ratio + self.params['blurRadius'] * 2 * self.pixel_ratio
        height = self.params['dialogHeight'] * self.pixel_ratio + self.params['blurRadius'] * 2 * self.pixel_ratio
        self.resize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(' ')
        self.setWindowIcon(QIcon(global_icon_path))
        if platform.system() == 'Windows':
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setColor(Qt.gray)
            shadow_effect.setBlurRadius(self.params['blurRadius'])
            shadow_effect.setOffset(0, 0)
            self.setGraphicsEffect(shadow_effect)
            self.setContentsMargins(self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio)

        v_layout = QVBoxLayout()

        h_layout_top = QHBoxLayout()
        h_layout_top.setContentsMargins(0, 0, 0, 0)
        h_layout_top.setSpacing(0)

        h_layout_middle = QHBoxLayout()
        h_layout_middle.setContentsMargins(0, 0, 0, 0)
        h_layout_middle.setSpacing(0)

        h_layout_bottom = QHBoxLayout()

        dialog_title = QLabel()
        dialog_title.setText(self.params['title'])
        dialog_title.setAlignment(Qt.AlignCenter)
        dialog_title.setObjectName('dialog_title')
        h_layout_top.addWidget(dialog_title)

        dialog_description = QLabel()
        dialog_description.setText(self.params['description'])
        dialog_description.setAlignment(Qt.AlignCenter)
        dialog_description.setObjectName('dialog_description')
        h_layout_middle.addWidget(dialog_description)

        left_button = QPushButton(self.params['leftButtonText'])
        left_button.clicked.connect(action[self.params['leftButtonAction']])
        right_button = QPushButton(self.params['rightButtonText'])
        right_button.clicked.connect(action[self.params['rightButtonAction']])

        h_layout_bottom.addStretch(1)
        h_layout_bottom.addWidget(left_button)
        h_layout_bottom.addStretch(1)
        h_layout_bottom.addWidget(right_button)
        h_layout_bottom.addStretch(1)

        top_widget = QWidget()
        top_widget.setProperty('name', 'top_widget')

        middle_widget = QWidget()
        middle_widget.setProperty('name', 'middle_widget')

        bottom_widget = QWidget()
        bottom_widget.setProperty('name', 'bottom_widget')

        top_widget.setLayout(h_layout_top)
        middle_widget.setLayout(h_layout_middle)
        bottom_widget.setLayout(h_layout_bottom)

        v_layout.addWidget(top_widget, 50)
        v_layout.addWidget(middle_widget, 101)
        v_layout.addWidget(bottom_widget, 50)
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(v_layout)
        if 'parentWindow' in self.params.keys():
            parent = self.params['parentWindow']
            self.move(parent.geometry().center() - self.rect().center())

    def init_style(self):
        style = """
          QWidget [name="top_widget"] {
            background-color: [topBgColor];
            border-top-left-radius: [borderRadius];
            border-top-right-radius:[borderRadius];
          }
          QWidget [name="middle_widget"] {
            background-color: [middleBgColor];
          }
          QWidget [name="bottom_widget"] {
            border-top: 1px solid #dcdcdc;
            background-color: [bottomBgColor];
            border-bottom-left-radius:[borderRadius];
            border-bottom-right-radius:[borderRadius];
          }
          QPushButton {
            background-color: [buttonBgColor];
            color: #fff;
            font-family: Microsoft YaHei;
            text-align: center;
            border-radius: 5px;
            width: [buttonWidth];
            height: [buttonHeight];
            font-size: [buttonFontSize];
          }
          QPushButton:hover {
            background-color: [buttonHoverBgColor];
          }
          QLabel {
            font-family: Microsoft YaHei;
            text-align: center;
          }
          #dialog_title {
            color: #fff;
            font-size: [topFontSize];
          }
          #dialog_description{
            color: [middleFontColor];
            font-size: [middleFontSize];
          }
        """
        style = style.replace('[borderRadius]', str(self.params['borderRadius'] * self.pixel_ratio) + 'px')
        style = style.replace('[topBgColor]', self.params['topBgColor'])
        style = style.replace('[middleBgColor]', '#fff')
        style = style.replace('[bottomBgColor]', '#fff')
        style = style.replace('[buttonWidth]', str(self.params['buttonWidth'] * self.pixel_ratio) + 'px')
        style = style.replace('[buttonHeight]', str(self.params['buttonHeight'] * self.pixel_ratio) + 'px')
        style = style.replace('[buttonBgColor]', self.params['buttonBgColor'])
        style = style.replace('[middleFontColor]', self.params['middleFontColor'])
        style = style.replace('[middleFontSize]', str(int(self.params['middleFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[topFontSize]', str(int(self.params['topFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[buttonFontSize]', str(int(self.params['buttonFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[buttonHoverBgColor]', self.params['buttonHoverBgColor'])
        self.setStyleSheet(style)

    def emit_event_to_browser(self):
        if self.view:
            self.view.dispatch_customize_event(event_name='cefDialogConfirmEvent',
                                               event_data=self.params['customizedData'])
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.m_drag and event.buttons() and Qt.LeftButton:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False

    def quit_app(self):
        BrowserView.instances['master'].hide()
        if platform.system() == 'Windows':
            for pid in BrowserView.hwnd_subprocess_map.values():
                os.popen('taskkill /pid {pid} -f'.format(pid=pid))
        quit_application()


class CefApplication(QApplication):
    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.timer = self.create_timer()

    def create_timer(self):
        timer = QTimer()
        timer.timeout.connect(self.on_timer)
        timer.start(10)
        return timer

    @staticmethod
    def on_timer():
        cef.MessageLoopWork()

    def stop_timer(self):
        # Stop the timer after Qt's message loop has ended
        self.timer.stop()


class PopUp(object):
    def __init__(self, browser):
        self.browser = browser

    def closePopUp(self):
        self.browser.CloseBrowser()


class LoadHandler(object):
    def __init__(self, uid, payload, cid, browser):
        self.payload = payload
        self.uid = uid
        self.cid = cid
        self.browser = browser
        self.handlerId = generate_guid()

    def OnLoadStart(self, browser, frame):
        logging.debug(
            'OnLoadStart: url = {url}'.format(url=browser.GetUrl()))
        if browser.IsPopup():
            bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
            bindings.SetProperty('qt5CefVersion', constant.qt5_cef_version)
            bindings.SetObject('cef', PopUp(browser))
            browser.SetJavascriptBindings(bindings)

        if frame.IsMain():
            if debug_mode:
                with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                    browser.ExecuteJavascript(js.read())
            else:
                logging.debug('Inject cef sdk to cid={cid}, uid={uid}'.format(cid=self.cid, uid=self.uid))
                browser.ExecuteJavascript(cef_sdk)
                append_payload(self.uid, self.payload, self.cid)
                self.browser.update_browser_info_one_by_one()

        record_page_monitor(browser, [{
            'ID': hashlib.md5(
                '{handlerId}{globalId}{Id}'.format(handlerId=self.handlerId, globalId=frame.GetBrowserIdentifier(),
                                                   Id=frame.GetIdentifier()).encode(encoding='UTF-8')).hexdigest(),
            'uid': self.uid,
            'cid': self.cid,
            'time': time.time() * 1000,
            'url': frame.GetUrl(),
            'loadStart': True,
            'loadEnd': False
        }])

    def OnLoadEnd(self, browser, frame, http_code):
        record_page_monitor(browser, [{
            'ID': hashlib.md5(
                '{handlerId}{globalId}{Id}'.format(handlerId=self.handlerId, globalId=frame.GetBrowserIdentifier(),
                                                   Id=frame.GetIdentifier()).encode(encoding='UTF-8')).hexdigest(),
            'uid': self.uid,
            'cid': self.cid,
            'time': time.time() * 1000,
            'url': frame.GetUrl(),
            'loadStart': False,
            'loadEnd': True
        }])

    def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url):
        if frame.IsMain():
            if debug_mode:
                with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                    browser.ExecuteJavascript(js.read())
            else:
                browser.ExecuteJavascript(cef_sdk)
                append_payload(self.uid, self.payload, self.cid)
                self.browser.update_browser_info_one_by_one()


class LifeSpanHandler(object):
    def __init__(self, validate_function=lambda *args: False):
        self.validate_function = validate_function

    def OnBeforePopup(self, browser, frame, target_url, target_frame_name, target_disposition, user_gesture,
                      popup_features, window_info_out, client, browser_settings_out, no_javascript_access_out):
        try:
            if hasattr(self.validate_function, '__call__') and self.validate_function(target_url):
                webbrowser.open(target_url)
                return True
            pass
        except Exception as e:
            logging.debug(e)


class KeyboardHandler(object):
    def __init__(self, browser):
        self.browser = browser

    def OnKeyEvent(self, browser, event, event_handle):
        # MacOS系统，57.0以下版本，复制内容后，粘贴会产生两次内容。以下内容摘自66.0版本的源代码。
        """Default implementation for keyboard shortcuts on Mac (Issue #161)."""
        if platform.system() == "Darwin":
            if event["modifiers"] == 128 \
                    and event["type"] != cef.KEYEVENT_RAWKEYDOWN:
                # Copy and paste was handled in RAWKEYDOWN, return True
                if event["native_key_code"] in [8, 9]:
                    return True
            if event["modifiers"] == 128 \
                    and event["type"] == cef.KEYEVENT_RAWKEYDOWN:
                # Select all: command + a
                if event["native_key_code"] == 0:
                    browser.GetMainFrame().SelectAll()
                    return True
                # Copy: command + c
                elif event["native_key_code"] == 8:
                    browser.GetMainFrame().Copy()
                    return True
                # Paste: command + v
                elif event["native_key_code"] == 9:
                    browser.GetMainFrame().Paste()
                    return True
                # Cut: command + x
                elif event["native_key_code"] == 7:
                    browser.GetMainFrame().Cut()
                    return True
                # Undo: command + z
                elif event["native_key_code"] == 6:
                    browser.GetMainFrame().Undo()
                    return True
            elif event["modifiers"] == 130 \
                    and event["type"] == cef.KEYEVENT_RAWKEYDOWN:
                # Redo: command + shift + z
                if event["native_key_code"] == 6:
                    browser.GetMainFrame().Redo()
                    return True
        return False


class BrowserView(QMainWindow):
    instances = {}
    menu_map = {}
    cid_map = {}
    cid_hwnd_map = {}
    cid_3rd_client_process_map = {}  # 当需要启动某个第三方应用到某个独立的窗口时，存放启动某个第三方应用所对应的子进程ID的映射关系
    hwnd_subprocess_map = {}  # 存放每个第三方应用主窗口句柄所对应的子线程ID

    full_screen_trigger = QtCore.pyqtSignal()
    resize_trigger = QtCore.pyqtSignal(int, int)
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    def __init__(self, uid, title="", url="", width=default_window_width,
                 height=default_window_height,
                 resizable=True, full_screen=False, min_size=(min_window_width, min_window_height),
                 background_color="#ffffff", web_view_ready=None, cid='', enable_max=True, window_type='cef',
                 quit_app_when_main_window_close=True, popup_validate=None, extendScreen="false"):
        super(BrowserView, self).__init__()
        BrowserView.instances[uid] = self
        screen = QDesktopWidget().screenGeometry()
        global screen_width, screen_height
        screen_width = screen.width()
        screen_height = screen.height()
        self.popup_validate = popup_validate
        self.quit_app_when_main_window_close = quit_app_when_main_window_close
        self.key_board_layout = 0  # 用于记录当前窗口在禁用输入法之前的状态
        self.attached_child_list = []  # 存储该窗口的跟随子窗口列表
        self.third_party_pid_list = []  # 存储当前窗口所内嵌第三方应用的子进程Id
        self.responsive_params = {
            'top': 0,
            'right': 0,
            'bottom': 0,
            'left': 0
        }  # 当作为某个窗口的跟随子窗口时，如果需要响应式的随着父窗口缩放而改变自身大小，则使用这些参数，表示在窗口自适应过程中，始终距离父窗口四边的距离
        self.uid = uid
        if cid == '':
            self.cid = uid
        else:
            self.cid = cid

        BrowserView.cid_map[uid] = self.cid
        self.is_full_screen = False
        self.load_event = Event()

        # 处理默认窗口大小
        if width != -1 and height != -1:
            if extendScreen == "true":
                if QDesktopWidget().screenCount() > 1:
                    screen1 = QDesktopWidget().screenGeometry(1)
                    self.resize(screen1.width(), screen1.height())
                else:
                    self.resize(screen_width, screen_height)
            else:
                self.resize(width, height)
        else:
            self.resize(screen_width * 0.85, screen_height * 0.8)

        self.title = title
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(global_icon_path))

        # Set window background color
        self.background_color = QColor()
        self.background_color.setNamedColor(background_color)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.background_color)
        self.setPalette(palette)

        if not resizable:
            self.setFixedSize(width, height)

        self.setMinimumSize(min_size[0], min_size[1])
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        # 禁用窗口最大化
        if not enable_max and extendScreen == "false":
            self.setFixedSize(self.width(), self.height())
            self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        if window_type == 'cef':
            window_info = cef.WindowInfo()
            rect = [0, 0, self.width(), self.height()]
            window_info.SetAsChild(int(self.winId()), rect)

            setting = {
                "standard_font_family": "Microsoft YaHei",
                "default_encoding": "utf-8",
                "plugins_disabled": True,
                "tab_to_links_disabled": True,
                "web_security_disabled": True,
                "accept_language_list": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            }

            if url is not None:
                pass
                self.view = cef.CreateBrowserSync(window_info, url=url, settings=setting)
            else:
                self.view = cef.CreateBrowserSync(window_info, url="about:blank", settings=setting)

        # self.view.ShowDevTools()
        self.full_screen_trigger.connect(self.toggle_full_screen)
        self.resize_trigger.connect(self.trigger_window_resize)
        self.load_event.set()

        if full_screen:
            self.emit_full_screen_signal()

        if extendScreen == "true":
            self.move(screen_width, 0)
        else:
            self.move(QApplication.desktop().availableGeometry().center() - self.rect().center())
        self.activateWindow()
        self.raise_()
        if web_view_ready is not None:
            web_view_ready.set()

    def exit_application(self):
        quit_application()

    def close_attached_window(self):
        for child_window in self.attached_child_list:
            child_window.close()

    def showEvent(self, event):
        if self.cid in BrowserView.cid_hwnd_map:
            parent = self.parent()
            global pixel_ratio
            if platform.system() == 'Windows':
                pixel_ratio = dpi_dict[str(parent.logicalDpiX())]
            geometry = parent.third_party_window_geometry
            offset_top = pixel_ratio * geometry['top']
            offset_right = pixel_ratio * geometry['right']
            offset_bottom = pixel_ratio * geometry['bottom']
            offset_left = pixel_ratio * geometry['left']
            self.resize(parent.width() - offset_left - offset_right,
                        parent.height() - offset_top - offset_bottom)

    def changeEvent(self, event):
        if self.isActiveWindow() and hasattr(self, 'view'):
            self.view.SetFocus(True)

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            if hasattr(self, 'view'):
                self.view.ExecuteFunction('window.python_cef.dispatchCustomEvent', 'windowCloseEvent')
            else:
                self.kill_subprocess()
                self.close_attached_window()
                event.accept()
        else:
            if self.uid == 'master':
                if self.quit_app_when_main_window_close:
                    self.kill_subprocess()
                    quit_application()
                else:
                    self.kill_subprocess()
                    self.close_attached_window()
                    self.update_browser_info_one_by_one(increase=False)
                    event.accept()

            else:
                self.kill_subprocess()
                self.close_attached_window()
                self.update_browser_info_one_by_one(increase=False)
                event.accept()

    def resizeEvent(self, event):
        cef.WindowUtils.OnSize(self.winId(), 0, 0, 0)
        size = event.size()
        self.resize_trigger.emit(size.width(), size.height())

    def kill_subprocess(self):
        if platform.system() == 'Windows':
            for sub_pid in self.third_party_pid_list:
                os.popen('taskkill /pid {pid} -f'.format(pid=sub_pid))

    def close_nest_client(self, cid):
        if cid in BrowserView.cid_hwnd_map.keys():
            self.close_window([cid])
            hwnd = BrowserView.cid_hwnd_map[cid]
            subprocess = BrowserView.hwnd_subprocess_map[hwnd]
            os.popen('taskkill /pid {pid} -f'.format(pid=subprocess))

    def show_window(self, cid=''):
        uid = self.get_uid_by_cid(cid)
        if cid == '' or cid is None:
            self.show()
        elif uid is not None:
            BrowserView.instances[uid].show()

    def hide_window(self, cid=''):
        uid = self.get_uid_by_cid(cid)
        try:
            if cid == '' or cid is None:
                self.hide()
            elif uid is not None:
                BrowserView.instances[uid].hide()
        except Exception as e:
            logging.error(e)

    def close_window(self, cid_lists=[]):
        """
        This method can be invoked by Javascript.
        :return:
        """
        if len(cid_lists) == 0:
            self.view.CloseDevTools()  # 关闭cef的devTools
            self.close()  # 关闭qt的窗口
        else:
            for cid in cid_lists:
                uid = self.get_uid_by_cid(cid)
                if uid in BrowserView.instances.keys():
                    BrowserView.instances[uid].close()
                else:
                    self.view.ExecuteFunction('window.python_cef.console', '不存在 cid = {cid} 的窗口'.format(cid=cid),
                                              'warn')

    def close_all_window(self):
        """
        This method can be invoked by Javascript.
        :return:
        """
        # for qt_main_window in BrowserView.instances.values():
        #     qt_main_window.close()
        self.kill_subprocess()
        quit_application()

    def open(self, param=None):
        """
        This method can be invoked by Javascript.
        :return:
        """
        if param is None:
            param = {}
        if isinstance(param, dict):
            param.setdefault('url', 'about:blank')
            param.setdefault('title', default_window_title)
            param.setdefault('payload', {})
            param.setdefault('cid', '')
            param.setdefault('maximized', False)
            param.setdefault('minimized', False)
            param.setdefault('width', default_window_width)
            param.setdefault('height', default_window_height)
            param.setdefault('enableMax', True)
            param.setdefault('extendScreen', 'false')
            open_new_window(url=param["url"], title=param["title"], payload=param["payload"],
                            maximized=param["maximized"], minimized=param["minimized"], cid=param["cid"],
                            width=param["width"], height=param["height"], enable_max=param["enableMax"], extendScreen=param["extendScreen"])
        elif isinstance(param, str):
            open_new_window(url=param)

    def toggle_full_screen(self):
        if self.is_full_screen:
            self.showNormal()
        else:
            self.showFullScreen()

        self.is_full_screen = not self.is_full_screen

    def trigger_window_resize(self, width, height):
        global pixel_ratio
        if hasattr(self, 'third_party_wrapper_window'):
            try:
                if platform.system() == 'Windows':
                    pixel_ratio = dpi_dict[str(self.logicalDpiX())]
                param = self.third_party_window_geometry
                width = width - param['left'] * pixel_ratio - param['right'] * pixel_ratio
                height = height - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
                self.third_party_wrapper_window.resize(width, height)
            except RuntimeError:
                del self.third_party_wrapper_window

        # 处理该窗口的所有跟随子窗口的resize行为
        if len(self.attached_child_list) > 0:
            for child_window in self.attached_child_list:
                try:
                    if platform.system() == 'Windows':
                        pixel_ratio = dpi_dict[str(child_window.logicalDpiX())]
                    param = child_window.responsive_params
                    width = self.width() - param['left'] * pixel_ratio - param['right'] * pixel_ratio
                    height = self.height() - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
                    child_window.resize(width, height)
                except RuntimeError:
                    self.attached_child_list.remove(child_window)

    def emit_full_screen_signal(self):
        self.full_screen_trigger.emit()

    def create_cef_pure_window(self, url):
        """
        This method can be invoked by Javascript.
        :return:
        """
        cef.CreateBrowserSync(url=url)

    def maximize_current_window(self):
        self.showMaximized()

    def minimize_current_window(self):
        self.showMinimized()

    def maximize_window(self, uid):
        BrowserView.instances[uid].showMaximized()

    def minimize_window(self, uid):
        BrowserView.instances[uid].showMinimized()

    def update_browser_info_one_by_one(self, increase=True):
        # 移除窗口实例
        if not increase:
            if self.uid in BrowserView.instances.keys():
                del BrowserView.instances[self.uid]
            if self.uid in BrowserView.cid_map.keys():
                del BrowserView.cid_map[self.uid]

        for browser in BrowserView.instances.values():
            if hasattr(browser, 'view'):
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'cidLists',
                                             list(BrowserView.cid_map.values()))
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'widLists',
                                             list(BrowserView.cid_map.keys()))

    def focus_browser(self, cid=None):
        if cid is not None and isinstance(cid, str):
            for (uid, _cid_) in BrowserView.cid_map.items():
                if _cid_ == cid:
                    BrowserView.instances[uid].activateWindow()
                    BrowserView.instances[uid].view.SetFocus(True)
                    BrowserView.instances[uid].view.SetFocus(True)
                    break
        else:
            self.activateWindow()
            self.setFocus(True)
            self.view.SetFocus(True)

    def arouse_window(self, cid=None):
        if cid is not None and isinstance(cid, str):
            for (uid, _cid_) in BrowserView.cid_map.items():
                if _cid_ == cid:
                    BrowserView.instances[uid].activateWindow()
                    BrowserView.instances[uid].showNormal()
                    break
        else:
            self.showNormal()
            self.activateWindow()

    def set_browser_payload(self, cid, payload):
        for (uid, value) in BrowserView.cid_map.items():
            if value == cid:
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
                break

    def set_cookie(self, cookieObj={}):
        if not isinstance(cookieObj, dict):
            return
        else:
            cookieObj.setdefault('name', 'default_cookie_name')
            cookieObj.setdefault('value', 'default_cookie_value')
            cookieObj.setdefault('domain', '127.0.0.1')
            cookieObj.setdefault('path', '/')
            cookie_manager = cef.CookieManager().GetGlobalManager()
            cookie = cef.Cookie()
            cookie.SetName(cookieObj['name'])
            cookie.SetValue(cookieObj['value'])
            cookie.SetDomain(cookieObj['domain'])
            cookie.SetPath(cookieObj['path'])
            cookie_manager.SetCookie(self.view.GetUrl(), cookie)

    def get_room_level(self):
        self.view.ExecuteFunction('window.python_cef.console', self.view.GetZoomLevel())

    def set_roo_level(self, level):
        self.view.SetZoomLevel(level)

    def get_uid_by_cid(self, cid):
        for (uid, value) in BrowserView.cid_map.items():
            if value == cid:
                return uid

    def dispatch_customize_event(self, event_name='', event_data={}):
        for uid in BrowserView.instances.keys():
            if hasattr(BrowserView.instances[uid], 'view'):
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.dispatchCustomEvent', event_name,
                                                                event_data)

    def nest_third_party_application(self, param={}):
        if param is None:
            param = {}
        param.setdefault('newCid', '')  # 本窗口的cid
        param.setdefault('targetCid', 'master')  # 内嵌应用目标窗口的cid
        param.setdefault('top', 0)  # 内嵌窗口距离目标窗口顶部的自适应距离
        param.setdefault('right', 0)  # 内嵌窗口距离目标窗口右侧的自适应距离
        param.setdefault('bottom', 0)  # 内嵌窗口距离目标窗口底部的自适应距离
        param.setdefault('left', 0)  # 内嵌窗口距离目标窗口左侧的自适应距离
        param.setdefault('applicationPath', '')
        param.setdefault('launchParams', {})
        launch_third_party_application(param)

    def nest_frame_window(self, param={}):
        logging.debug('[Nest Frame Window] : param = {param}'.format(param=param))
        if param is None:
            param = {}

        try:
            # 外置浏览器打开时，要拼接参数
            if param.get("open_default_browser", "false") == "true" and param.get('url') and param.get(
                    "sip_appkey") and param.get("sip_sign"):
                param["url"] = str(param["url"]) + "&sip_appkey=" + str(param.get("sip_appkey")) + "&sip_sign=" + str(
                    param.get("sip_sign"))
        except Exception as e:
            logging.error("外置浏览器打开链接，拼接参数错误：" + str(e))

        if isinstance(param, dict):
            param.setdefault('newCid', '')  # 新窗口的cid
            param.setdefault('targetCid', 'master')  # 目标窗口cid
            param.setdefault('url', '')  # 新窗口将要加载的url
            param.setdefault('payload', {})  # 需要传递给新窗口的挂载数据
            param.setdefault('top', default_nest_window_margin)  # 内嵌窗口距离target窗口的顶部距离
            param.setdefault('right', default_nest_window_margin)  # 内嵌窗口距离target窗口的右侧距离
            param.setdefault('bottom', default_nest_window_margin)  # 内嵌窗口距离target窗口的底部距离
            param.setdefault('left', default_nest_window_margin)  # 内嵌窗口距离target窗口的左侧距离
            param.setdefault('windowType', 'cef')
            param.setdefault('open_default_browser', 'false')        #是否使用外置默认浏览器打开界面 true 使用，false 不使用


            if param.get("open_default_browser") == "true":
                try:
                    webbrowser.open(param.get("url"))
                except Exception as e:
                    logging.error("外置浏览器打开异常，检查是否存在默认浏览器；异常原因："+e.__str__())
            else:
                frame_window = create_qt_view(url=param['url'], cid=param['newCid'], default_show=False,
                                              payload=param['payload'], window_type=param['windowType'],
                                              popup_validate=self.popup_validate)
                frame_window.responsive_params['top'] = param['top']
                frame_window.responsive_params['right'] = param['right']
                frame_window.responsive_params['bottom'] = param['bottom']
                frame_window.responsive_params['left'] = param['left']
                target_uid = self.get_uid_by_cid(param['targetCid'])
                if target_uid is not None:
                    global pixel_ratio
                    if platform.system() == 'Windows':
                        pixel_ratio = dpi_dict[str(frame_window.logicalDpiX())]
                    target_window = BrowserView.instances[target_uid]
                    target_window.attached_child_list.append(frame_window)
                    frame_window.setParent(target_window)
                    frame_window.show()
                    frame_window.move(param['left'] * pixel_ratio, param['top'] * pixel_ratio)
                    width = target_window.width() - param['left'] * pixel_ratio - param['right'] * pixel_ratio
                    height = target_window.height() - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
                    frame_window.resize(width, height)
                    frame_window.setWindowFlags(Qt.FramelessWindowHint)

    def update_window_geometry(self, cid=None):
        if cid is None:
            uid = self.uid
        else:
            uid = self.get_uid_by_cid(cid)
        BrowserView.instances[uid].view.ExecuteJavascript(
            'window.__cef__.CEF_INFO.windowLogicalWidth = {windowLogicalWidth}'.format(
                windowLogicalWidth=self.width()))
        BrowserView.instances[uid].view.ExecuteJavascript(
            'window.__cef__.CEF_INFO.windowLogicalHeight = {windowLogicalHeight}'.format(
                windowLogicalHeight=self.height()))

    def show_cef_dialog(self, params={}):
        if params is None:
            params = {}
        params['parentWindow'] = self
        Dialog(params, self)

    def send_key_event_to_client(self, params={}):
        if params is None:
            params = {}
        params.setdefault('hwnd', int(self.winId()))
        params.setdefault('keys', [])
        if platform.system() == 'Windows':
            import win32api
            import win32con
            import win32gui
            win32gui.SetFocus(params['hwnd'])
            # 模拟键盘按下操作
            for keyCode in params['keys']:
                win32api.keybd_event(keyCode, 0, 0, 0)
            # 模拟键盘弹出操作
            for keyCode in params['keys']:
                win32api.keybd_event(keyCode, 0, win32con.KEYEVENTF_KEYUP, 0)

    def disable_ime(self):
        if platform.system() == 'Windows':
            import win32api
            import win32con
            self.key_board_layout = win32api.GetKeyboardLayout()
            win32api.LoadKeyboardLayout('0x0409', win32con.KLF_ACTIVATE)

    def enable_ime(self):
        if platform.system() == 'Windows':
            import win32api
            import win32con
            if platform.release() == '10':
                win32api.keybd_event(91, 0, 0, 0)  # win
                win32api.keybd_event(32, 0, 0, 0)  # space
                win32api.keybd_event(91, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(32, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                win32api.keybd_event(16, 0, 0, 0)  # shift
                win32api.keybd_event(17, 0, 0, 0)  # ctrl
                win32api.keybd_event(16, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

    def get_ime(self):
        if platform.system() == 'Windows':
            import win32api
            import win32con

    def set_menu_info(self, menu='No Value'):
        BrowserView.menu_map[self.uid] = menu

    def get_menu_info(self, uid='master'):
        if uid in BrowserView.menu_map.keys():
            return BrowserView.menu_map[uid]

    @staticmethod
    def update_3rd_party_info():
        for browser in BrowserView.instances.values():
            if hasattr(browser, 'view'):
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'nestClientInfo',
                                             BrowserView.cid_hwnd_map)
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'cidLists',
                                             list(BrowserView.cid_map.values()))
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'widLists',
                                             list(BrowserView.cid_map.keys()))

    def reload_ignore_cache(self):
        self.view.ReloadIgnoreCache()

    def show_dev_tool(self, cid=None):
        if cid is None:
            self.view.ShowDevTools()
        else:
            uid = self.get_uid_by_cid(cid)
            if uid in BrowserView.instances.keys():
                BrowserView.instances[uid].view.ShowDevTools()

    def set_window_title(self, title=default_window_title):
        self.setWindowTitle(title)

    def reload_url_by_cid(self, cid, url):
        uid = self.get_uid_by_cid(cid)
        if uid in BrowserView.instances.keys():
            BrowserView.instances[uid].view.LoadUrl(url)

    def close_process(self, pid):
        # print(time.time(), ':',  '【try to close process pid = ', pid, '】')
        try:
            # os.popen('taskkill /pid {pid} -f'.format(pid=pid))
            os.kill(pid, 0)
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            # print(pid, ' is not exist')
            logging.debug('{pid} is not exist'.format(pid=pid))

    def load_url(self, url='about:blank'):
        if hasattr(self, 'view'):
            self.view.LoadUrl(url)

    def reload_sdk(self):
        logging.debug('[Reload SDK]')
        self.view.ExecuteJavascript('console.log("%c U will reload cef sdk.", "font-weight: 600;color: #31136a")')
        self.view.ExecuteJavascript('window.CEF_HAS_INITIALIZED = false;')
        self.view.ExecuteJavascript(cef_sdk)
        self.update_browser_info_one_by_one()


class ThirdPartyWindow(QWidget):
    def __init__(self, child_window):
        super(ThirdPartyWindow, self).__init__()
        embed = self.createWindowContainer(child_window, self)
        window_layout = QHBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(embed)
        self.setLayout(window_layout)


class CustomRequestHandler:
    def OnBeforeResourceLoad(self, browser, frame, request):
        """在资源加载前修改请求头"""
        # 1. 设置自定义请求头
        if request.GetMethod() != "GET":
            return

        # 过滤本地以及cdn的相关请求
        if request.GetUrl().startswith('http://127.0.0.1') or request.GetUrl().startswith('http://at.alicdn.com'):
            return

        if "Attach2" not in request.GetUrl():
            return

        try:
            header_map = request.GetHeaderMap()
            accept = header_map.get("Accept") or header_map.get("accept")
            if not (accept and "image/" in accept):
                # 非图片请求
                return
            # 图片请求添加
            header_map["X-File-Access"] = "allow_access"
            request.SetHeaderMap(header_map)

        except Exception as e:
            print("OnBeforeResourceLoad>>>>>" + str(e))

        # 继续加载资源
        return
        # return cef.RETURN_CONTINUE


class ClientHandler:
    def GetResourceHandler(self, browser, frame, request):
        if request.GetUrl().startswith('http://127.0.0.1') or request.GetUrl().startswith('http://at.alicdn.com'):   # 过滤本地以及cdn的相关请求
            return
        _filter_request = ["portal-min",
                           "/html/nds/object/object.jsp",
                           "/html/nds/objext/copyto.jsp",
                           "/html/nds/print/options.jsp",
                           "/html/nds/cxtab/viewcube.jsp",
                           "/html/common/null.html",
                           "batchImport/shelfnoIndex.html",
                           "My97DatePicker.htm",
                           "/control/command?command=CopyTo"]
        _filter_request_in = False
        # 判断_filter_request中的元素是否都没有在字符串request中出现
        if [element for element in _filter_request if element in request.GetUrl()]:
            _filter_request_in = True
        if(not _filter_request_in):
            return
        print("GetResourceHandler : url = %s" % request.GetUrl())
        self.res = ResourceHandler()
        self.res._clientHandler = self
        self.res._browser = browser
        self.res._frame = frame
        self.res._request = request
        self._AddStrongReference(self.res)
        return self.res

    def _OnResourceResponse(self, browser, frame, request, requestStatus,requestError, response, data):
        print("_OnResourceResponse")
        return data


    _resourceHandlers = {}
    _resourceHandlerMaxId = 0

    def _AddStrongReference(self, resHandler):
        self._resourceHandlerMaxId += 1
        resHandler._resourceHandlerId = self._resourceHandlerMaxId
        self._resourceHandlers[resHandler._resourceHandlerId] = resHandler

    def _ReleaseStrongReference(self, resHandler):
        if resHandler._resourceHandlerId in self._resourceHandlers:
            del self._resourceHandlers[resHandler._resourceHandlerId]
        else:
            print("_ReleaseStrongReference() FAILED: resource handler " \
                  "not found, id = %s" % (resHandler._resourceHandlerId))

class ResourceHandler:
    _resourceHandlerId = None
    _clientHandler = None
    _browser = None
    _frame = None
    _request = None
    _responseHeadersReadyCallback = None
    _webRequest = None
    _webRequestClient = None
    _offsetRead = 0

    def ProcessRequest(self, request, callback):
        # 1. Start the request using WebRequest
        # 2. Return True to handle the request
        # 3. Once response headers are ready call
        #    callback.Continue()
        self._responseHeadersReadyCallback = callback
        self._webRequestClient = WebRequestClient()
        self._webRequestClient._resourceHandler = self
        # Need to set AllowCacheCredentials and AllowCookies for
        # the cookies to work during POST requests (Issue 127).
        # To skip cache set the SkipCache request flag.
        request.SetFlags(cef.Request.Flags["AllowCachedCredentials"] \
                         | cef.Request.Flags["AllowCookies"])
        # A strong reference to the WebRequest object must kept.
        self._webRequest = cef.WebRequest.Create(
            request, self._webRequestClient)
        return True

    def GetResponseHeaders(self, response, length, redirect):
        print("GetResponseHeaders")
        assert self._webRequestClient._response, "Response object empty"
        wrcResponse = self._webRequestClient._response
        response.SetStatus(wrcResponse.GetStatus())
        response.SetStatusText(wrcResponse.GetStatusText())
        response.SetMimeType(wrcResponse.GetMimeType())
        if wrcResponse.GetHeaderMultimap():
            headers = wrcResponse.GetHeaderMap()
            if "X-Frame-Options" in headers:
                headers["X-Frame-Options"] = "ALLOWALL"
            if "Access-Control-Allow-Origin" in headers:
                headers["Access-Control-Allow-Origin"] = "*"
            if "Feature-Policy" in headers:
                del headers["Feature-Policy"]
            if "Content-Security-Policy" in headers:
                del headers["Content-Security-Policy"]
            response.SetHeaderMap(headers)
        length[0] = self._webRequestClient._dataLength
        if not length[0]:
            # Probably a cached page? Or a redirect?
            pass

    def ReadResponse(self, data_out, bytes_to_read, bytes_read_out, callback):
        if self._offsetRead < self._webRequestClient._dataLength:
            dataChunk = self._webRequestClient._data[ \
                        self._offsetRead:(self._offsetRead + bytes_to_read)]
            self._offsetRead += len(dataChunk)
            data_out[0] = dataChunk
            bytes_read_out[0] = len(dataChunk)
            return True
        #     if self._offsetRead >= self._webRequestClient._dataLength:
        #         self._clientHandler._ReleaseStrongReference(self)
        #         return False
        #     else:
        #         return True
        self._clientHandler._ReleaseStrongReference(self)
        print("no more data, return False")
        return False

    def CanGetCookie(self, cookie):
        return True

    def CanSetCookie(self, cookie):
         return True

    def Cancel(self):
         pass

class WebRequestClient:
    _resourceHandler = None
    _data = ""
    _dataLength = -1
    _response = None

    def OnUploadProgress(self, web_request, current, total):
        pass

    def OnDownloadProgress(self, web_request, current, total):
        pass

    def OnDownloadData(self, web_request, data):
        self._data += data

    def OnRequestComplete(self, web_request):
        # cefpython.WebRequest.Status = {"Unknown", "Success",
        #         "Pending", "Canceled", "Failed"}
        statusText = "Unknown"
        webRequest = web_request
        if webRequest.GetRequestStatus() in cef.WebRequest.Status:
            statusText = cef.WebRequest.Status[\
                    webRequest.GetRequestStatus()]
        #print("status = %s" % statusText)
        #print("error code = %s" % webRequest.GetRequestError())
        # Emulate OnResourceResponse() in ClientHandler:
        self._response = webRequest.GetResponse()
        # Are webRequest.GetRequest() and
        # self._resourceHandler._request the same? What if
        # there was a redirect, what will GetUrl() return
        # for both of them?
        self._data = self._resourceHandler._clientHandler._OnResourceResponse(
                self._resourceHandler._browser,
                self._resourceHandler._frame,
                webRequest.GetRequest(),
                webRequest.GetRequestStatus(),
                webRequest.GetRequestError(),
                webRequest.GetResponse(),
                self._data)
        self._data = self._data.encode("utf-8")
        self._dataLength = len(self._data)
        # ResourceHandler.GetResponseHeaders() will get called
        # after _responseHeadersReadyCallback.Continue() is called.
        self._resourceHandler._responseHeadersReadyCallback.Continue()

def update_third_party_client_info(cid='un_know_client_cid', info={}):
    for uid in BrowserView.instances.keys():
        if hasattr(BrowserView.instances[uid], 'view'):
            BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateThirdPartyClientInfo',
                                                            cid, info)


def listen_process_by_hwnd(hwnd, cid, client_window, pid, application_path):
    # print(time.time(), ':',  'listen pid = ', pid)
    if hwnd == 0:
        return
    else:
        if platform.system() == 'Windows':
            import win32event
            try:
                if win32event.WaitForSingleObject(hwnd, win32event.INFINITE) == win32event.WAIT_OBJECT_0:
                    app_tag = hashlib.md5(application_path.encode(encoding='UTF-8')).hexdigest()
                    third_party_client_launch_status[app_tag] = -1
                    update_third_party_client_info(cid, {'pid': pid, 'status': 'closed'})  # 在所有浏览器窗口中更新某个第三方应用的打开状态
                    # print(pid, ' is be killed')
                    # client_window.close()  # 不再执行窗口关闭动作
                    BrowserView.instances['master'].view.ExecuteFunction('window.__cef__.close', [cid])
                    # print(client_window.cid, 'is closed')
                    # print('--------------- end ------------------', pid)
            except Exception as e:
                logging.error(e)


def find_main_window_hwnd(class_name=qt_class_name, title=""):
    if platform.system() == 'Windows':
        import win32gui
        hwnd = win32gui.FindWindow(class_name, title)
        logging.debug(
            '[ pid = {pid} ]  FindWindow class_name = {class_name}, title = {title}'.format(class_name=class_name,
                                                                                            title=title,
                                                                                            pid=os.getpid()))
        logging.debug('[ pid = {pid} ] FindWindow hwnd = {hwnd}'.format(hwnd=hwnd, pid=os.getpid()))
        return hwnd
    else:
        return 0


def get_uid_by_cid(cid):
    for (uid, value) in BrowserView.cid_map.items():
        if value == cid:
            return uid


def get_system_language():
    language_code = QLocale().language()
    if str(language_code) in language_locale.keys():
        return language_locale[str(language_code)]['locale']
    else:
        return 'en_US'


def validate_3rd_client_alive(third_party_application_title):
    if platform.system() == 'Windows':
        import win32gui
        hit_client_list = []

        def call_back(item_hwnd, window_title):
            if win32gui.GetWindowText(item_hwnd).find(window_title) != -1:
                nonlocal hit_client_list
                hit_client_list.append(win32gui.GetWindowText(item_hwnd))

        win32gui.EnumWindows(call_back, third_party_application_title)
        return hit_client_list


def get_handle_id(third_party_application_title):
    logging.debug('[Get Client Handle Id]')
    if platform.system() == 'Windows':
        import win32gui
        hwnd = 0

        def call_back(item_hwnd, window_title):
            if win32gui.GetWindowText(item_hwnd) == window_title:
                nonlocal hwnd
                hwnd = item_hwnd

        if hwnd == 0:
            start = time.time()
            while hwnd == 0:
                time.sleep(0.1)

                # 利用EnumWindows枚举形式发现第三方窗口应用句柄
                win32gui.EnumWindows(call_back, third_party_application_title)

                # 利用FindWindow窗口形式，直接获取第三方应用窗口句柄
                # temp_hwnd = win32gui.FindWindow(None, third_party_application_title)
                # if temp_hwnd != 0:
                #     hwnd = temp_hwnd

                end = time.time()
                if hwnd != 0 or end - start > 10:
                    return hwnd

        return hwnd


def launch_third_party_client(application_title,
                              application_path,
                              launch_params,
                              target_window,
                              client_window,
                              cid):
    logging.debug('[Launch Third Party Client] target_window cid = {cid}'.format(cid=target_window.cid))
    if platform.system() == 'Windows':
        import win32api
        import win32con
        exe_path = application_path + ' -t:' + application_title + ' -p:' + str(os.getpid()) + ' -b:false'
        for (k, v) in launch_params.items():
            exe_path = exe_path + ' ' + '--' + k + ':' + v + ''
        child_process = subprocess.Popen(exe_path)
        logging.debug('[Launch Third Party Client] Client Pid = {pid}'.format(pid=child_process.pid))
        child_process_hwnd = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, child_process.pid)
        update_third_party_client_info(cid, {'pid': child_process.pid, 'status': 'alive'})  # 处理第三方应用在所有窗口的进程状态
        t = Thread(target=listen_process_by_hwnd,
                   args=(child_process_hwnd, cid, client_window, child_process.pid, application_path))
        t.start()
        BrowserView.cid_3rd_client_process_map[cid] = child_process.pid
        third_party_client_pid_lists.append(child_process.pid)
        target_window.third_party_pid_list.append(child_process.pid)


def nest_third_party_application(target_uid='master',
                                 cid='',
                                 third_party_window_geometry={'top': 0, 'right': 0, 'bottom': 0, 'left': 0},
                                 application_path='',
                                 launch_params={},
                                 show=True):
    logging.debug('[Nest Third Party Application]')
    app_tag = hashlib.md5(application_path.encode(encoding='UTF-8')).hexdigest()
    if not third_party_client_launch_status.__contains__(app_tag):
        third_party_client_launch_status[app_tag] = 0  # 启动中
    elif third_party_client_launch_status[app_tag] != -1:
        # 如果某个第三方应用已经启动或正在启动中，则不执行启动程序
        return

    third_party_application_title = 'third_party_application_title_' + os.path.basename(application_path)  # 窗口名使用应用程序名
    third_party_wrapper_window = create_qt_view(default_show=False, window_type='qt', cid=cid)
    global pixel_ratio
    if platform.system() == 'Windows':
        pixel_ratio = dpi_dict[str(third_party_wrapper_window.logicalDpiX())]
    geometry = third_party_window_geometry
    target_window = BrowserView.instances[target_uid]
    offset_top = pixel_ratio * geometry['top']
    offset_right = pixel_ratio * geometry['right']
    offset_bottom = pixel_ratio * geometry['bottom']
    offset_left = pixel_ratio * geometry['left']
    t = Thread(target=launch_third_party_client,
               args=(third_party_application_title, application_path, launch_params, target_window,
                     third_party_wrapper_window, cid), daemon=True)
    t.start()
    t.join()
    hwnd = get_handle_id(third_party_application_title)
    logging.debug('[Nest Third Party Application] Client Hwnd = {hwnd}'.format(hwnd=hwnd))
    if hwnd != 0:
        third_party_client_launch_status[app_tag] = 1
        if cid != '':
            BrowserView.cid_hwnd_map[cid] = hwnd
            BrowserView.hwnd_subprocess_map[hwnd] = BrowserView.cid_3rd_client_process_map[cid]
            BrowserView.update_3rd_party_info()
        temp_window = 0
        while temp_window == 0:
            temp_window = QWindow.fromWinId(hwnd)
        temp_window.setFlags(
            Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint | Qt.WA_TranslucentBackground)
        third_party_window = ThirdPartyWindow(temp_window)

        third_party_wrapper_window.setCentralWidget(third_party_window)
        third_party_wrapper_window.setWindowFlags(Qt.FramelessWindowHint)
        target_window.third_party_wrapper_window = third_party_wrapper_window  # 设置内嵌【第三方内嵌应用】引用
        target_window.third_party_window_geometry = third_party_window_geometry  # 设置内【第三方内嵌应用】在父窗口size发生改变时的同步规则
        third_party_wrapper_window.setParent(target_window)  # 将【第三方内嵌应用】作为target_window的子控件
        third_party_wrapper_window.move(offset_left, offset_top)  # 移动【第三方内嵌应用】 窗口位置（相对于target_window）
        if show:
            third_party_wrapper_window.show()  # 将【第三方内嵌应用】显示出来
        # 根据【第三方内嵌应用】的应用场景同步其应具备的宽和高
        third_party_wrapper_window.resize(target_window.width() - offset_left - offset_right,
                                          target_window.height() - offset_top - offset_bottom)


def launch_third_party_application(params={}):
    if params is None:
        params = {}
    params.setdefault('targetCid', 'master')
    params.setdefault('newCid', generate_guid())
    params.setdefault('top', 0)
    params.setdefault('right', 0)
    params.setdefault('bottom', 0)
    params.setdefault('left', 0)
    params.setdefault('applicationPath', '')
    params.setdefault('launchParams', {})
    params.setdefault('show', True)
    nest_third_party_application(target_uid=get_uid_by_cid(params['targetCid']),
                                 cid=params['newCid'],
                                 third_party_window_geometry={
                                     'top': params['top'],
                                     'right': params['right'],
                                     'bottom': params['bottom'],
                                     'left': params['left']
                                 },
                                 application_path=params['applicationPath'],
                                 launch_params=params['launchParams'],
                                 show=params['show']
                                 )


def html_to_data_uri(html):
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    return ret


def generate_guid(prefix='child'):
    return prefix + '_' + uuid4().hex[:8]


def open_new_window(url, title=default_window_title, payload=None, maximized=False, minimized=False, cid='',
                    width=default_window_width, height=default_window_height, enable_max=True, extendScreen="false"):
    logging.debug('[Open New Window] : url={url}, cid={cid}'.format(url=url, cid=cid))
    create_browser_view(uid=generate_guid(), url=url, title=title, payload=payload, maximized=maximized,
                        minimized=minimized, cid=cid, width=width, height=height, enable_max=enable_max,
                        inject_obj=app_inject_obj, application_version=app_version_info, extend_Screen=extendScreen)


def create_qt_view(default_show=True, window_type='cef', url='', cid='', payload={}, popup_validate=None):
    """
    基于Qt创建新窗口
    :param default_show:  默认是否显示窗口
    :param window_type:  窗口类型：cef => 浏览器窗口 , qt => qt窗口
    :param url:  创建浏览器窗口时候，可以指定默认打开链接地址
    :param cid:  创建的新窗口的customer window id
    :param payload:  创建浏览器新窗口的时候需要向窗口注入的挂载数据
    :param popup_validate:  当创建窗口为浏览器窗口的时候，设置此窗口关于弹框相关的校验逻辑
    :return:
    """
    # print('[create_qt_window]')
    # print('cid = ', cid)
    # print('BrowserView.cid_map = ', BrowserView.cid_map)
    # print('window_type = ', window_type)
    qt_view = None
    has_exist = False  # 是否已经存在cid相同的window
    for (UID, CID) in BrowserView.cid_map.items():
        if CID == cid:
            has_exist = True
            qt_view = BrowserView.instances[UID]
            break

    if not qt_view:
        uid = generate_guid()
        qt_view = BrowserView(uid, window_type=window_type, url=url, cid=cid, popup_validate=popup_validate)
        qt_view.update_browser_info_one_by_one()

    if window_type == 'cef' and not has_exist:
        set_javascript_bindings(uid, payload=payload)
        set_client_handler(uid, payload=payload, cid=cid, browser=qt_view, popup_validate=popup_validate)

    if default_show:
        qt_view.show()

    return qt_view


def create_browser_view(uid, title="", url=None, width=default_window_width, height=default_window_height,
                        resizable=True, full_screen=False,
                        min_size=(min_window_width, min_window_height),
                        background_color="#ffffff", web_view_ready=None, payload=None, maximized=False,
                        minimized=False, cid='', call_back=None, enable_max=True, inject_obj=app_inject_obj,
                        quit_app_when_main_window_close=True, application_version=app_version_info,
                        popup_validate=None, extend_Screen="false", inject_custom_request=False):
    browser = BrowserView(uid, title, url, width, height, resizable, full_screen, min_size,
                          background_color, web_view_ready, cid=cid, enable_max=enable_max,
                          quit_app_when_main_window_close=quit_app_when_main_window_close,
                          popup_validate=popup_validate, extendScreen=extend_Screen)
    if maximized and extend_Screen == 'false':
        browser.showMaximized()

    if minimized and extend_Screen == 'false':
        browser.showMinimized()

    if extend_Screen == "true":
        browser.showMaximized()
    elif full_screen:
        # 全屏显示
        browser.showFullScreen()
    else:
        browser.show()

    global splash
    if splash is not None:
        splash.finish(browser)

    if hasattr(call_back, '__call__'):
        call_back(browser)
    set_javascript_bindings(uid, inject_obj=inject_obj, application_version=application_version, payload=payload)
    set_client_handler(uid, payload, cid, browser, popup_validate, inject_custom_request)


def launch_main_window(uid, title, url, width, height, resizable, full_screen, min_size,
                       background_color, web_view_ready, context_menu=False, maximized=True, minimized=False,
                       user_agent=None, icon_path='', call_back=None, single_instance=True,
                       app_name="Qt Application Made By Burgeon Developer", inject_obj=app_inject_obj,
                       quit_app_when_main_window_close=True, application_version=app_version_info,
                       enable_cef_cache=True, main_window_class_name=qt_class_name, popup_validate=None,
                       splash_screen=False, splash_text='',
                       splash_style='font-size: 20px; font-family: Microsoft YaHei;', inject_custom_request=False, *args):
    logging.debug('\r\n ---------- Application will launch ----------')
    global app_inject_obj
    global app_version_info
    global global_icon_path
    global_icon_path = icon_path
    app_version_info = application_version
    app_inject_obj = inject_obj
    global app
    app = CefApplication(sys.argv)
    app.setApplicationName(app_name)

    # 第一层拦截，应用单实例层面拦截
    singleton = QSharedMemory(app.applicationName())
    logging.debug('Application Pid = {pid} , Application has not launched before = {tag}'.format(pid=os.getpid(),
                                                                                                 tag=singleton.create(
                                                                                                     1)))
    if platform.system() == 'Windows' and single_instance and not singleton.create(1):
        # 第二层拦截，如果找到窗口句柄，则唤起
        hwnd = find_main_window_hwnd(class_name=main_window_class_name, title=title)
        if single_instance and hwnd != 0 and platform.system() == 'Windows':
            import win32gui, win32con
            logging.debug('[ pid = {pid} ] 唤起已经打开应用'.format(pid=os.getpid()))
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            logging.debug('[ pid = {pid} ]【退出本次启动】'.format(pid=os.getpid()))
            exit_python()
            return
        exit_python()
        return

    # show splash 启动界面控制  --在主浏览器窗口弹出前，弹出启动加载提示窗口
    if splash_screen:
        global splash
        splash = QSplashScreen()
        splash.showMessage(splash_text, Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter | Qt.AlignTop)
        splash.setStyleSheet(splash_style)
        splash.resize(300, 185.4)
        splash.move(QApplication.desktop().availableGeometry().center() - splash.rect().center())
        splash.show()

    cef_work_path = ''
    if platform.system() == 'Windows':
        cef_work_path = os.environ['ALLUSERSPROFILE']
    elif platform.system() == 'Darwin':
        cef_work_path = os.environ['HOME']
    global app_cef_cache_path
    if enable_cef_cache:
        app_cef_cache_path = os.path.join(cef_work_path, 'Burgeon', 'CEF', title)
    else:
        app_cef_cache_path = ''
    settings = {
        'context_menu': {'enabled': context_menu},
        'auto_zooming': 0.0,
        'user_agent': user_agent,
        'cache_path': app_cef_cache_path,
        'persist_user_preferences': True,
        'remote_debugging_port': 3333,
        'locale': 'zh-CN',
        'log_file': os.path.join(constant.debug_log_dir, time.strftime('%Y-%m-%d', time.localtime()) + '.log'),
    }

    '''
        # external_message_pump 开启，在cefpython3=57.0版本会遇到退出后弹出系统异常提示框情况。
        if platform.system() == 'Darwin' and cef.__version__ != '66.0':
        # 实测cefpython3 为66.0时，如果开启external_message_pump，则页面如果出现原生<select><select/>标签，则会发生闪退现象，底层原因尚未找到。
        # 在解决问题之前，需要进行版本判断。
        print('[ CEF LOG ] cefpython3 version = ', cef.__version__)
        settings['external_message_pump'] = True
    '''

    switches = {
        'disable-gpu': '',
        'disable-gpu-compositing': ''
    }

    framework_dir_path = ""
    browser_subprocess_path = ""
    # 发布mac包用到的
    if platform.system() == 'Darwin':
        # 获取当前python的版本号
        python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)

        # framework_dir_path路径获取 研发模式和打包后的APP路径不一致
        # 研发模式下，venv目录下的路径
        if os.environ.get('VIRTUAL_ENV') and os.path.exists(os.environ['VIRTUAL_ENV']):
            framework_dir_path_venv = os.path.abspath(
                os.environ["VIRTUAL_ENV"] +"/lib/python" + python_version + "/site-packages/cefpython3/Chromium Embedded Framework.framework")
            browser_subprocess_path_venv = os.path.abspath(
                os.environ["VIRTUAL_ENV"] +"/lib/python" + python_version + "/site-packages/cefpython3/subprocess")

        # py2app 生产编译模式下，Contents/Resources下的路径
        framework_dir_path_py2app = os.path.abspath("./lib/python" + python_version + "/cefpython3/Chromium Embedded Framework.framework")
        browser_subprocess_path_py2app = os.path.abspath("./lib/python" + python_version + "/cefpython3/subprocess")
        exist_py2app = os.path.exists(framework_dir_path_py2app)

        # py2app 本地编译打包 -A 参数控制的alias模式下，应使用系统环境路径
        framework_dir_path_system = os.path.abspath(sys.base_prefix + "/lib/python" + python_version + "/site-packages/cefpython3/Chromium Embedded Framework.framework")
        browser_subprocess_path_system = os.path.abspath(sys.base_prefix + "/lib/python" + python_version + "/site-packages/cefpython3/subprocess")
        exist_system = os.path.exists(framework_dir_path_system)

        framework_dir_path_pyinstaller = os.path.abspath(sys.base_prefix + "/Chromium Embedded Framework.framework")
        browser_subprocess_path_pyinstaller = os.path.abspath(sys.base_prefix + "/subprocess")
        exist_pyinstaller = os.path.exists(framework_dir_path_pyinstaller)

        if exist_py2app:
            print("[ CEF LOG ] 当前应用为生产模式，使用py2app打包构建")
            framework_dir_path = framework_dir_path_py2app
            browser_subprocess_path = browser_subprocess_path_py2app
        elif exist_system:
            print("[ CEF LOG ] 当前应用为研发模式，使用py2app -a 模式进行调试")
            framework_dir_path = framework_dir_path_system
            browser_subprocess_path = browser_subprocess_path_system
        elif exist_pyinstaller:
            print("[ CEF LOG ] 当前应用为生产模式，使用pyinstaller打包构建")
            framework_dir_path = framework_dir_path_pyinstaller
            browser_subprocess_path = browser_subprocess_path_pyinstaller
        else:
            print("[ CEF LOG ] 当前应用为研发模式，使用研发环境venv目录")
            framework_dir_path = framework_dir_path_venv
            browser_subprocess_path = browser_subprocess_path_venv

        print("[ CEF LOG ] framework_dir_path : ", framework_dir_path)
        print("[ CEF LOG ] browser_subprocess_path : ", browser_subprocess_path)

        settings["framework_dir_path"] = framework_dir_path
        settings["browser_subprocess_path"] = browser_subprocess_path

    cef.Initialize(settings=settings, switches=switches)
    create_browser_view(uid=uid, title=title, url=url, width=width, height=height, resizable=resizable,
                        full_screen=full_screen, min_size=min_size,
                        background_color=background_color, web_view_ready=web_view_ready, maximized=maximized,
                        minimized=minimized, call_back=call_back, inject_obj=inject_obj,
                        quit_app_when_main_window_close=quit_app_when_main_window_close,
                        application_version=application_version, popup_validate=popup_validate, inject_custom_request=inject_custom_request)
    logging.debug('Application Main Window Launched.')
    app.exec_()
    app.stop_timer()
    del app
    cef.Shutdown()


def set_client_handler(uid, payload, cid, browser, popup_validate, inject_custom_request):
    BrowserView.instances[uid].view.SetClientHandler(LoadHandler(uid, payload, cid, browser))
    BrowserView.instances[uid].view.SetClientHandler(LifeSpanHandler(popup_validate))
    BrowserView.instances[uid].view.SetClientHandler(KeyboardHandler(browser))
    # BrowserView.instances[uid].view.SetClientHandler(CustomRequestHandler())
    if inject_custom_request:
        BrowserView.instances[uid].view.SetClientHandler(ClientHandler())


def set_javascript_bindings(uid, inject_obj=app_inject_obj, application_version=app_version_info, payload={}):
    bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
    bindings.SetProperty('clientWorkDirectory', os.getcwd())
    bindings.SetProperty('currentClientVersion', application_version)
    bindings.SetProperty("cefPython3", cef.GetVersion())
    bindings.SetProperty('cefCachePath', app_cef_cache_path)
    bindings.SetProperty('windowId', uid)
    bindings.SetProperty('qt5CefVersion', constant.qt5_cef_version)
    bindings.SetProperty('system', platform.system())
    bindings.SetProperty('systemLanguage', get_system_language())
    bindings.SetProperty('__cef__', {
        'cid': BrowserView.instances[uid].cid,
        'cidLists': list(BrowserView.cid_map.values()),
        'wid': uid,
        'widLists': list(BrowserView.cid_map.keys()),
        'payload': payload
    })
    bindings.SetObject('windowInstance', BrowserView.instances[uid])
    for (k, v) in inject_obj.items():
        try:
            v.browser = BrowserView.instances[uid].view
        except Exception as e:
            logging.debug(e)
        if v is None or isinstance(v, str) or isinstance(v, dict):
            bindings.SetProperty(k, v)
        else:
            bindings.SetObject(k, v)
    BrowserView.instances[uid].view.SetJavascriptBindings(bindings)


def append_payload(uid, payload, cid=''):
    if not BrowserView.instances.__contains__(uid):
        return

    BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'wid', uid)
    if cid != '':
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'cid', cid)
    else:
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'cid', uid)
    if payload is None:
        return
    if isinstance(payload, dict):
        fun_list = []
        for (k, v) in payload.items():
            if isinstance(v, cef.JavascriptCallback):
                fun_list.append(k)
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.console',
                                                                '检测到 payload.{key} 是函数类型，启动新窗口时挂载的payload中不允许包含函数'
                                                                .format(key=k),
                                                                'warn')
        for key in fun_list:
            del payload[key]
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
    else:
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.console',
                                                        '启动新窗口时挂载的payload必须为JsonObject，且对象属性不能为函数: payload = {payload}'
                                                        .format(payload=payload))


def execute_javascript(script, uid):
    if uid in BrowserView.instances:
        BrowserView.instances[uid].view.ExecuteJavascript(script)
    else:
        return


def set_cookies(url, cookies):
    cookie_manager = cef.CookieManager().GetGlobalManager()
    cookie_manager.SetCookie(url, cookies)


def delete_cookies(url, name):
    cookie_manager = cef.CookieManager().GetGlobalManager()
    cookie_manager.DeleteCookies(url, name)


def quit_application():
    app.quit()
    t = Thread(target=exit_python)
    t.start()


def exit_python():
    logging.debug('Application Will Be Destroyed.')
    for sub_pid in third_party_client_pid_lists:
        os.popen('taskkill /pid {pid} -f'.format(pid=sub_pid))
    if platform.system() == 'Windows':
        pid = os.getpid()
        os.kill(pid, signal.CTRL_BREAK_EVENT)
    else:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
