# -*- coding: utf-8 -*-

from pprint import pprint # модуль pprint используется для удобного вывода на экран
matrix = [[0.5,   0,   0,   0,   0],
          [  1, 0.5,   0,   0,   0],
          [  1,   1, 0.5,   0,   0],
          [  1,   1,   1, 0.5,   0],
          [  1,   1,   1,   1, 0.5]]
 
matrix_t = list(zip(*matrix)) # непосредственно транспонирование
 
pprint(matrix)
pprint(matrix_t)

