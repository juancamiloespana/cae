package org.opt4j.CAE.VRP;

import java.util.Locale;

public class Point {
	private double x;
	private double y;
	/**
	 * @param x
	 * @param y
	 */
	public Point(double x, double y) {
		this.x = x;
		this.y = y;
	}

	public double getX() {
		return x;
	}
	public void setX(double x) {
		this.x = x;
	}
	public double getY() {
		return y;
	}
	public void setY(double y) {
		this.y = y;
	}

	@Override
	public String toString() {
		return String.format(Locale.ENGLISH, "(%.2f, %.2f)", getX(), getY());
	}

	/**
	 * distancia euclidea al punto two
	 * @param two objeto Point 
	 * @return distancia euclidea del punto actual al punto two
	 */
	public double distance(Point two) {		
		return Math.sqrt(Math.pow(this.getX()-two.getX(), 2) + 
				Math.pow(this.getY()-two.getY(), 2));
	}
}
