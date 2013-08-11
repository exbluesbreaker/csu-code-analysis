package ru.csu.stan.ui.code;

import java.util.Comparator;

/**
 * Компаратор двух якорей в коде.
 * Сортирует якоря <b>по возрастанию номеров строк</b>.
 * Внутри одной строки якоря сортируются <b>по убыванию номера позиции</b> в строке.
 * 
 * @author mz
 *
 */
public class AnchorComparator implements Comparator<Anchor> {

	@Override
	public int compare(Anchor o1, Anchor o2) {
		if (o1 == null && o2 != null)
			return -1;
		if (o1 != null && o2 == null)
			return 1;
		if (o1 == null && o2 == null)
			return 0;
		if (o1.getLine() > o2.getLine())
			return 1;
		if (o1.getLine() < o2.getLine())
			return -1;
		if (o1.getCol() > o2.getCol())
			return -1;
		if (o1.getCol() < o2.getCol())
			return 1;
		return 0;
	}

}
