# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
import byteplay        # специальный модуль для удобной работы с Python-байтокодом
import new             # для создания функции во время исполнения
import functools       # для update_wrapper
import inspect         # для получения информации о параметрах, принимаемых функцией
#-------------------------------------------------------------------------------
class FastFunctor(object):
    def __init__(self,func,code = None):
        self.func = None                # здесь будем хранить результирующую функцию
        self.ofunc = func               # а здесь исходную(original) функцию
        if code is None:     
            # конструируем байтокод для вызова функции
            self.code = [(byteplay.LOAD_CONST,func)]
            rparams = inspect.getargspec(func)[0] # получаем список параметров, принимаемых функцией
            self.code.extend((byteplay.LOAD_FAST,i) for i in rparams)
            self.code.append((byteplay.CALL_FUNCTION,len(rparams)))
        else:
            # если же функтор создан из другого функтора, 
            # то только копируем переданный байтокод
            self.code = code
        # создаем новый объект кода
        self.ocode = bp.Code.from_code(func.func_code)
    def __add__(self,obj):   # этот метод вызывается для операции '+'
        code = self.code[:]  # копируем байтокод
        if isinstance(obj,FastFunctor):  # если прибавляемый объект - функтор
            # просто дописываем его код к нашему
            # после своего исполнения он "оставит" в вершине стека результат
            code.extend(obj.code) 
        else:
            # иначе загружаем объект в стек
            code.append((byteplay.LOAD_CONST,obj))
        # дописываем байтокод, складывающий два верхних элемента в стеке
        code.append((byteplay.BINARY_ADD ,None )) 
        # создаем новый функтор, с байтокодом получения суммы
        return self.__class__(self.ofunc,code = code)
    def __call__(self,*dt,**mp):        # этот метод будет вызван для операции вызова object()
        return self.fast()(*dt,**mp)    # конструируем и вызываем функцию
    def fast(self): # конструируем функцию из байтокода
        if self.func is None:           # если функция не была создана раннее
            code = self.code + [(bp.RETURN_VALUE,None)] # добавляем байтокод возврата
            oc = self.ocode
            # создаем объект кода из байтокода и другой информации
            bin_code =  byteplay.Code(code,
                                oc.freevars,
                                oc.args,
                                oc.varargs,
                                oc.varkwargs,
                                oc.newlocals,
                                "<just_code_%s>" % id(self),
                                "<auto_gen_%s>" % id(self),
                                0,
                                "auto_generated code")
            # конструируем новую функцию из объекта кода
            self.func = new.function(bin_code.to_code(),globals())
            # после этой операции для всех средств интроспекции 
            # созданная функция будет выглядеть как оригинальная
            self.func = functools.update_wrapper(self.func,self.ofunc)
        return self.func

