# -*- coding: utf-8 -*-


from __future__ import with_statement     # задействует оператор with в коде
from contextlib import contextmanager
from threading import Lock
 
# Описание менеджера контекста
@contextmanager
def locked(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
 
# Определение блокировки
myLock = Lock()
 
# Применение оператора
with locked(myLock):
    #
    print "Охраняемый блок кода. Блокировка будет освобождена при любом выходе из этого блока."
    #
