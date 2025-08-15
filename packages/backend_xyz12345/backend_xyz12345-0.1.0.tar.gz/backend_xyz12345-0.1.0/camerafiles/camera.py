import sys 
import ctypes
from ctypes import c_int, c_bool
import traceback 

from PyQt5.QtWidgets import QErrorMessage
from PyQt5 import QtWidgets

from .MvImport.MvCameraControl_class import * 
from .MvImport.MvErrorDefine_const import * 
from .MvImport.CameraParams_header import *

from .CamOperation_class import CameraOperation 

from .tools import TxtWrapBy, ToHexStr

import tkinter

class MachineVisionCamera:
    """
    Class to interact with the HikRobot's MVS camera: 
    the CE series and CS series Area scan cameras
    """
    def __init__(self) -> None:
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.cam = MvCamera()
        self.nSelCamIndex = 0
        self.obj_cam_operation:CameraOperation = str(0)
        # self.obj_cam_operation: CameraOperation = 0
        self.isOpen = False
        self.isGrabbing = False
        self.isCalibMode = True # Whether it is calibration mode (get the original image)
        self.trigger_mode = None
        self.callback = None 
        self.ui_update_callback = None

    def set_ui(self, ui):
        self.ui = ui 

    
    def xFunc(self, event) -> None:
        """
        Bind the drop-down list to the device information index
        """
        self.nSelCamIndex = TxtWrapBy("[", "]", self.ui.ComboDevices.get())

    def set_device_information_index(self, camera_name): # same as xFunc
        # camera_name : self.ui.ComboDevices.get()
        self.nSelCamIndex = TxtWrapBy("[", "]", camera_name)

    # decoding characters
    def decoding_char(self, c_ubyte_value) -> str:
        c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
        try:
            decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
        except UnicodeDecodeError:
            decode_str = str(c_char_p_value.value)
        return decode_str

    # ch:枚举相机 | en:enum devices
    def enum_devices(self, combobox: QtWidgets.QComboBox = None) -> list | int:
        """
        List all the camera devices connected to the host

        Parameters
        -----------------------------
        combobox: QtWidgets.QComboBox
            the combobox variable to display the list of devices 

        Returns
        ------------------------------
        devList: List 
            list of all devices connected to host,
        error_code: int
            returns the error code
        """
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            self.message_box("Error", strError)
            return ret

        if self.deviceList.nDeviceNum == 0:
            self.message_box( "Info", "Find no device")
            return ret
        print("Find %d devices!" % self.deviceList.nDeviceNum)

        devList = []
        for i in range(0, self.deviceList.nDeviceNum):
            mvcc_dev_info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                user_defined_name = self.decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = self.decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                user_defined_name = self.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = self.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        try:
            if type(combobox) != type(None):
                combobox.clear()
                combobox.addItems(devList)
                combobox.setCurrentIndex(0)
        except Exception as e:
            print('[-] Error enum devices')
            print(traceback.format_exc())
        return devList
    
    # ch:打开相机 | en:open device
    def open_device(self, combobox: QtWidgets.QComboBox = None) -> int:
        """ 
        Opens the camera, that is establish the connection with the camera. 
        But does not caputers of does any operation, it is just to establish the connection between the host and camera
            
        Parameters
        ---------------------------
        combobox: QtWidgets.QComboBox
            the combobox variable to display the list of devices 
        Returns
        ---------------------------
        error_code: int
            the error codes occured when there is any fault in opening the device
        """
        if self.isOpen:
            self.message_box( "Error", 'Camera is Running!')
            return MV_E_CALLORDER

        try:
            if type(combobox) != type(None):
                self.nSelCamIndex = combobox.currentIndex()
        except Exception as e:
            self.message_box( "Error", 'Please select a camera!')
            print('[-] Error Opening device')
            print(traceback.format_exc())
    
        if self.nSelCamIndex < 0:
            self.message_box( "Error", 'Please select a camera!')
            return MV_E_CALLORDER

        self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, self.nSelCamIndex)
        ret = self.obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            self.message_box( "Error", strError)
            self.isOpen = False
        else:
            # self.set_continue_mode()
            # self.set_hardware_trigger_mode()
            self.get_param()
            # self.set_param()

            self.isOpen = True
            # self.enable_controls()
    
    # ch:开始取流 | en:Start grab image
    def start_grabbing(self, widgetDisplay: QtWidgets.QLabel) -> None:
        """
        Begins to grab image from the camera, 
        notice the trigger set on the camera as it contains: continuous, hardware trigger and software trigger modes
        """

        self.obj_cam_operation.image_captured_callback = self.callback
        if self.ui_update_callback is not None:
            self.obj_cam_operation.ui_status_callback = self.ui_update_callback
        # self.set_image_callback_on_trigger(self.callback)
        
        ret = self.obj_cam_operation.Start_grabbing(widgetDisplay.winId())
        if ret != 0:
            strError = "Start grabbing failed ret:" + ToHexStr(ret)
            self.message_box( "Error", strError)
        else:
            self.isGrabbing = True

            # self.enable_controls()

    def To_hex_str(num):
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2 ** 32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr
        return hexStr
       
    def single_reject(self):
        # winsound.Beep(1500,1000)
        ret = self.obj_cam_operation.obj_cam.MV_CC_SetEnumValue("LineSelector", 1)
        if ret != 0:
            tkinter.messagebox.showerror('show error',
                                        'Selector failed1! ret = '
                                        +self.To_hex_str(ret))
        else:
            print("Line Selection Done")
        ret = self.obj_cam_operation.obj_cam.MV_CC_SetCommandValue("LineTriggerSoftware")
        if ret != 0:
            tkinter.messagebox.showerror('show error',
                                        'set linetriggersoftware fail! ret = '
                                        +self.To_hex_str(ret)) 
        else:
            print("Rejection triggered")
    
    # ch:停止取流 | en:Stop grab image
    def stop_grabbing(self) -> None:
        """
        stops the image capture even if there are triggers to the camera
        """
        ret = self.obj_cam_operation.Stop_grabbing()
        if ret != 0:
            strError = "Stop grabbing failed ret:" + ToHexStr(ret)
            self.message_box( "Error", strError)
        else:
            self.isGrabbing = False
            # self.enable_controls()
        
    
    # ch:关闭设备 | Close device
    def close_device(self, *args):
        """
        Closes the camera and disables the connection between host and camera
        
        Parameters 
        ------------------
        *args: Any
            kept for event receiving while exiting the whole program
        """
        
        if self.isOpen:
            self.obj_cam_operation.Close_device()
            self.isOpen = False

        self.isGrabbing = False
        # self.enable_controls()    

    # ch:设置触发模式 | en:set trigger mode
    def set_continue_mode(self):
        try:
            strError = None
            # stEnumInt = c_int()
            # current_trigger_mode = self.obj_cam_operation.obj_cam.MV_CC_GetEnumValue("TriggerMode", stEnumInt)
            trigger_mode = ['Off', 'On']
            ret = self.obj_cam_operation.Set_trigger_mode('continous')
            if ret != 0:
                strError = "Set continue mode failed ret:" + ToHexStr(ret) + "Trigger mode is " #  + str(trigger_mode[current_trigger_mode])
                self.message_box( "Error", strError)
        except Exception as e:
            self.message_box("Error","Please Open the Camera First")
    # ch:设置软触发模式 | en:set software trigger mode
    def set_software_trigger_mode(self):
        try:
            ret = self.obj_cam_operation.Set_trigger_mode('trigger')
            if ret != 0:
                strError = "Set trigger mode failed ret:" + ToHexStr(ret)
                self.message_box( "Error", strError)
            else : 
                print('software trigger success')
        except Exception as e:
            self.message_box("Error","Please Open the Camera First")
       
    # ch:设置触发命令 | en:set trigger software
    def trigger_once(self):
        try:
            ret = self.obj_cam_operation.Trigger_once()
            if ret != 0:
                strError = "TriggerSoftware failed ret:" + ToHexStr(ret)
                self.message_box( "Error", strError)
        except Exception as e:
            self.message_box("Error","Please Open the Camera First")
            
    def set_hardware_trigger_mode(self):
        try:
            ret = self.obj_cam_operation.Set_trigger_mode('trigger', hardware_trigger=True)
            if ret != 0:
                strError = "Set trigger mode failed ret:" + ToHexStr(ret)
                self.message_box( "Error", strError)
        except Exception as e:
            self.message_box("Error","Please Open the Camera First")
    # ch:存图 | en:save image
    def save_bmp(self):
        ret = self.obj_cam_operation.Save_Bmp()
        if ret != MV_OK:
            strError = "Save BMP failed ret:" + ToHexStr(ret)
            self.message_box( "Error", strError)
        else:
            print("Save image success")

    def is_float(self, str):
        try:
            float(str)
            return True
        except ValueError:
            return False
    
    # ch: 获取参数 | en:get param
    def get_param(self) -> list[int, int, int]:
        '''
        returns the current parameter of the camera  
        Returns
        ----------------------------
        exposure_time: int | float
        gain:  int | float 
        frame_rate: int | float

        ------
        current exposure time, gain and frame rate of the camera 
        '''
        try:
            ret = self.obj_cam_operation.Get_parameter()
            if ret != MV_OK:
                strError = "Get param failed ret:"
                self.message_box( "Error", strError)
            else:
                # self.ui.edtExposureTime.setText("{0:.2f}".format(self.obj_cam_operation.exposure_time))
                # self.ui.edtGain.setText("{0:.2f}".format(self.obj_cam_operation.gain))
                # self.ui.edtFrameRate.setText("{0:.2f}".format(self.obj_cam_operation.frame_rate))
                exposure_time = round(self.obj_cam_operation.exposure_time, 2)
                gain = round(self.obj_cam_operation.gain, 2)
                frame_rate = round(self.obj_cam_operation.frame_rate, 2)
                
                return [exposure_time, gain, frame_rate]
        except Exception as e:
            self.message_box("Notice","Please Open the Camera")

    # ch: 设置参数 | en:set param
    def set_param(self, exposure = 1000, gain = 15, frame_rate = 10):
        # frame_rate = self.ui.edtFrameRate.text()
        # exposure = self.ui.edtExposureTime.text()
        # gain = self.ui.edtGain.text()
        try:
            if self.is_float(frame_rate)!=True or self.is_float(exposure)!=True or self.is_float(gain)!=True:
                strError = "Set param failed ret:"
                self.message_box( "Error", strError)
                return MV_E_PARAMETER
            
            ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
            if ret != MV_OK:
                strError = "Set param failed ret:" + ToHexStr(ret)
                self.message_box("Error", strError)
            return MV_OK
        except Exception as e:
            self.message_box("Notice","Please Open the Camera")

    # ch: 设置控件状态 | en:set enable status
    def enable_controls(self):
        # Set the status of the group first, and then set the status of each control individually.
        self.ui.groupGrab.setEnabled(self.isOpen)
        self.ui.groupParam.setEnabled(self.isOpen)

        self.ui.bnOpen.setEnabled(not self.isOpen)
        self.ui.bnClose.setEnabled(self.isOpen)

        self.ui.bnStart.setEnabled(self.isOpen and (not self.isGrabbing))
        self.ui.bnStop.setEnabled(self.isOpen and self.isGrabbing)
        self.ui.bnSoftwareTrigger.setEnabled(self.isGrabbing and self.ui.radioTriggerMode.isChecked())
  
        self.ui.bnSaveImage.setEnabled(self.isOpen and self.isGrabbing)

    def message_box(self, title: str, text: str, value = None):
        error_dialog = ErrorMessage(title) 
        print(error_dialog.showMessage(text))
        print(error_dialog.exec())

    def set_image_callback_on_trigger(self, callback):
        """
        pass a callback function that has image as an argument in it
        """
        self.obj_cam_operation.image_captured_callback = callback
        ...
    
    def set_ui_events_callback_on_trigger(self, ui_update_callback):
        """
        pass a callback function that has image as an argument in it
        """
        self.obj_cam_operation.ui_status_callback = ui_update_callback
    
    def get_current_image(self):
        return self.obj_cam_operation.current_image



class ErrorMessage(QErrorMessage):
    def __init__(self, title:str ) -> None:
        super().__init__()
        self.setWindowTitle(title)
        # TODO: add an icon to the error message
        # self.windowIcon(QErrorMessage.)