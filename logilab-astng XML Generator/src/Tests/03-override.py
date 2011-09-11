# -*- coding: utf-8 -*-


import sys                                   # для получения объектов из вышележащих фрэймов стека
 
class CannotResolve(Exception):                     # класс исключения для случая ненахождения функции
    pass          
 
class Resolver(object):                      # класс, реализующий разрешение на этапе исполнения
    emess = "Can't found appropriate signature of func %s() for call with" + \
            " params %r"                     # сообщение об ошибке
    def __init__(self,name):                 # конструктор
        self.function_map = {}               # словарь, отображающий типы параметров на функции
        self.default = None                  # функция по умолчанию
        self.name = name                     # имя функции для вывода сообщений об ошибках
    def __call__(self,*dt):                  # имитируем функцию, принимающую любое количество 
                                             # позиционных параметров
        cls = tuple(map(type,dt))            # создаем tuple из типов переданных аргументов
                                             # функция type возвращает тип своего параметра
                                             # map вызовет type для каждого элемента из dt
        try:                                 
            x = self.function_map[cls]       # пытаемся получить функцию из словаря
        except KeyError:                     # если подходящей нет,
            if self.default is not None:     # используем функцию по умолчанию
                x = self.default             
            else:                            # если её нет - возбуждаем исключение
                raise CannotResolve(self.emess % (self.name,cls))
        return x(*dt)                        # вызываем функцию и возвращаем результат
def overload(*dt):                           # декоратор для перегрузки в качестве параметров
                                             # принимает типы параметров
    def closure(func):                       
        name = func.__name__                 # получаем имя функции
        fr = sys._getframe(1).f_locals.get(name,Resolver(name)) 
                                             # опускаемся на один шаг вниз по стеку и находим
                                             # локальную переменную с именем функции
                                             # если же ее нет, то используем новый 
                                             # Resolver-объект
        fr.function_map[dt] = func           # добавляем новую функцию к словарю 
                                             # разрешения вызовов
        return fr                             
    return closure
def overdef(func):                           # для создания функции по умолчанию
    name = func.__name__                     # аналогично как и в функции overload
    fr = sys._getframe(1).f_locals.get(name,Resolver(name))
    fr.default = func
    return fr
# теперь воспользуемся полученными декораторами
@overdef                                     # это будет функция по умолчанию
def f(*dt,**mp):                             
    print "Default call"                     # если нет явного return, то вернется None
@overload(int)                               # единственный параметр - целое
def f(x):
    return x + 1                             
@overload(str)                               # единственный параметр - строка
def f(x):
    return x + "1"
@overload(str,int)                           # строка и целое
def f(x,y):
    return x + str(y)
print f(1)           # напечатает : 2
print f("1")         # напечатает : 11
f(2,2)               # напечатает : Default call

