import pyautogui
import time

class Sensors:
    @staticmethod
    def move(X, Y):
        #Перемещает курсор по XY координатам
        pyautogui.moveTo(X, Y)
    
    @staticmethod
    def click(which):
        #Выполняет клик кнопкой мыши
        # match (which):
        #     case 0:
        #         pyautogui.click(button='left')
        #     case 1:
        #         pyautogui.click(button='right')
        #     case _:
        #         raise ValueError(f"Неизвестный тип клика: {which}.")
        if which==0:
            pyautogui.click(button='left')
        elif which==1:
            pyautogui.click(button='right')
        else:
            raise ValueError(f"Неизвестный тип клика: {which}.")
    
    @staticmethod
    def types(string):
        #Печатает строку
        pyautogui.write(string)
    
    @staticmethod
    def scroll(value, where):
        #Прокручивает колесо мыши вниз или вверх
        if where.lower() == "up":
            pyautogui.scroll(value)
        elif where.lower() == "down":
            pyautogui.scroll(-value)
        else:
            raise ValueError(f"Неизвестое направление прокрутки: {where}.")
    @staticmethod
    def doubleclick():
        pyautogui.doubleClick()