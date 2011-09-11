# -*- coding: utf-8 -*-

class Entity(dict):                                 # наследуем класс от __builtin__.dict
    def __getattr__(self, key):                     # этот метод будет вызван, если атрибут
                                                    # с именем key не будет найден у экземпляра класса
        try: 
             return self[key]                       # пытаемся вернуть элемент словаря
        except KeyError, k:                         # если такого элемента нет, то возбуждаем
             raise AttributeError, k                # исключение AttributeError
                                                    # по договоренности __getattr__ 
                                                    # не должно возбуждать других исключений
 
    def __setattr__(self, key, value):              # этот метод будет вызван при присвоении
        self[key] = value                           # атрибуту key значения value
 
    def __delattr__(self, key):                     # а этот при удалении атрибута 
        try:                                        # с помощью del mydict.g
            del self[key]
        except KeyError, k: 
            raise AttributeError, k
 
    def __repr__(self):                             # используется функцией repr 
        return self.__class__.__name__ + "(" + dict.__repr__(self) + ")"
 
d = Entity(a=1)
d.b_100 = 100
assert d.a == d['a'] and d.b_100 == d['b_100']

