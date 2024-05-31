import socketserver
import random
import os
import json



import time, win32con, win32api, win32gui,ctypes



#%% 키 전달용 사전 작업

PBYTE256 = ctypes.c_ubyte * 256
_user32 = ctypes.WinDLL("user32")
GetKeyboardState = _user32.GetKeyboardState
SetKeyboardState = _user32.SetKeyboardState
PostMessage = win32api.PostMessage
SendMessage = win32gui.SendMessage
FindWindow = win32gui.FindWindow
IsWindow = win32gui.IsWindow
GetCurrentThreadId = win32api.GetCurrentThreadId
GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
AttachThreadInput = _user32.AttachThreadInput
MapVirtualKeyA = _user32.MapVirtualKeyA
MapVirtualKeyW = _user32.MapVirtualKeyW
MakeLong = win32api.MAKELONG
w = win32con

def PostKeyEx(hwnd, key, shift, specialkey):
    if IsWindow(hwnd):
        ThreadId = GetWindowThreadProcessId(hwnd, None)
        lparam = MakeLong(0, MapVirtualKeyA(key, 0))
        msg_down = w.WM_KEYDOWN
        msg_up = w.WM_KEYUP
        if specialkey:
            lparam = lparam | 0x1000000
        if len(shift) > 0:  # Если есть модификаторы - используем PostMessage и AttachThreadInput
            pKeyBuffers = PBYTE256()
            pKeyBuffers_old = PBYTE256()

            SendMessage(hwnd, w.WM_ACTIVATE, w.WA_ACTIVE, 0)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, True)
            GetKeyboardState(ctypes.byref(pKeyBuffers_old))

            for modkey in shift:
                if modkey == w.VK_MENU:
                    lparam = lparam | 0x20000000
                    msg_down = w.WM_SYSKEYDOWN
                    msg_up = w.WM_SYSKEYUP
                pKeyBuffers[modkey] |= 128

            SetKeyboardState(ctypes.byref(pKeyBuffers))
            time.sleep(0.01)
            PostMessage(hwnd, msg_down, key, lparam)
            time.sleep(0.01)
            PostMessage(hwnd, msg_up, key, lparam | 0xC0000000)
            time.sleep(0.01)
            SetKeyboardState(ctypes.byref(pKeyBuffers_old))
            time.sleep(0.01)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, False)

        else:  # Если нету модификаторов - используем SendMessage
            SendMessage(hwnd, msg_down, key, lparam)
            SendMessage(hwnd, msg_up, key, lparam | 0xC0000000)
            
    
# # 엔터
def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)




#%%


class 카톡보내기(socketserver.BaseRequestHandler):
    
    # def __init__(self,채팅방,위치,내용,딜레이시간):
    #     self.채팅방 = 채팅방
    #     self.위치 = 위치
    #     self.내용 = 내용
    #     self.딜레이시간 = 딜레이시간
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} wrote:")
        
        
        # JSON 데이터 디코딩
        try:
            received_json = json.loads(self.data.decode('utf-8'))
            print("Received JSON:", received_json)
            
            # 처리 후 응답 JSON 생성
            response_json = json.dumps(self.data.decode('utf-8'))
            self.request.sendall(response_json.encode('utf-8'))
            
        except json.JSONDecodeError:
            print("Received non-JSON data:", self.data.decode('utf-8'))
            self.request.sendall(('JSONDecodeError 가 발생하였습니다.').encode('utf-8'))
            return
    
        
        params = received_json.get("params", [])
        
        채팅방 = params[0] if len(params) > 0 else None
        위치 = params[1] if len(params) > 1 else None
        내용 = params[2] if len(params) > 2 else None
        딜레이시간 = params[3] if len(params) > 3 else 0.5
        
        self.작업명 = received_json.get("작업명")
        self.채팅방 = 채팅방
        self.위치 = 위치
        self.내용 = 내용
        self.딜레이시간 = 딜레이시간
        
        
        if self.작업명 == '카톡_보내기':
            self.메시지전송(self.채팅방, self.위치, self.내용, self.딜레이시간)
        elif self.작업명 == '채팅창_닫기':
            print('모든 채팅창을 닫겠습니다.')
            self.close_windows("#32770")
        else:
            print('작업명을 확인해주세요')            
    

    def close_windows(self,class_name):
        def enum_windows(hwnd, lParam):
            class_name = win32gui.GetClassName(hwnd)
            if class_name == lParam:
                win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        win32gui.EnumWindows(enum_windows, class_name)
    
    
    def 메시지전송(self, 채팅방, 위치, 내용, 딜레이시간):
        
        hwndMain = win32gui.FindWindow( None, self.채팅방) #채팅방 검색
        
        
        if hwndMain == 0:
            print(위치,'에서 채팅방을 오픈합니다.')
            if 위치 == '친구목록':
                self.친구목록_오픈()
                time.sleep(self.딜레이시간)
            if 위치 == '채팅목록':
                self.채팅목록_오픈()
                time.sleep(self.딜레이시간)
            hwndMain = win32gui.FindWindow( None, self.채팅방)
        
        else:print('채팅방이 열려있습니다.')
            
        
        hwndMain = win32gui.FindWindow( None, self.채팅방)
        
        hwndEdit = win32gui.FindWindowEx( hwndMain, None, "richedit50W", None)
        # hwndListControl = win32gui.FindWindowEx( hwndMain, None, "EVA_VH_ListControl_Dblclk", None)
        
        win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, self.내용)
        time.sleep(self.딜레이시간)
        SendReturn(hwndEdit)
        

    def 친구목록_오픈(self):
        
        hwndkakao = win32gui.FindWindow(None, "카카오톡")
        
        hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
        hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
        hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_1, None, "Edit", None)
        
        # # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
        win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, "")
        time.sleep(self.딜레이시간)   # 안정성 위해 필요
        win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, self.채팅방)
        time.sleep(self.딜레이시간)   # 안정성 위해 필요
        SendReturn(hwndkakao_edit3)
        time.sleep(self.딜레이시간)
        
    
    def 채팅목록_오픈(self):
        
        hwndkakao = win32gui.FindWindow(None, "카카오톡")
        
        hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
        hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
        hwndkakao_edit2_2 = win32gui.FindWindowEx( hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None)   #챗roomlistview
        hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_2, None, "Edit", None)
        
        # # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
        win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, "")
        time.sleep(self.딜레이시간)   # 안정성 위해 필요
        win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, self.채팅방)
        time.sleep(self.딜레이시간)   # 안정성 위해 필요
        SendReturn(hwndkakao_edit3)
        time.sleep(self.딜레이시간)
        
        




if __name__ == "__main__":
    port = 5000  # 포트 번호를 5000으로 고정

    with socketserver.TCPServer(("localhost", port), 카톡보내기) as server:
        print(f"서버실행중: {port}")
        server.serve_forever()


# def find_free_port():
#     with socketserver.TCPServer(("localhost", 0), 카톡보내기) as server:
#         return server.server_address[1]

# if __name__ == "__main__":
#     port = find_free_port()
#     print(f"Using port: {port}")
    
#     try:
#         os.makedirs("C:\Temp\KAKAUTO")  # 해당 경로에 폴더 생성
#         print(f"폴더 생성")
#     except FileExistsError:
#         print(f"폴더 이미 존재함")

#     with open("C:\Temp\KAKAUTO\port.txt", "w") as f:
#         f.write(str(port))
    
#     with socketserver.TCPServer(("localhost", port), 카톡보내기) as server:
#         print("Server running...")
#         server.serve_forever()
