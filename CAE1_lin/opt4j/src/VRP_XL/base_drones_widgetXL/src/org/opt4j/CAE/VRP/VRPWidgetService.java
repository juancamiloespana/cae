package org.opt4j.CAE.VRP;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import org.opt4j.core.Individual;
import org.opt4j.viewer.IndividualMouseListener;
import org.opt4j.viewer.Viewport;
import org.opt4j.viewer.Widget;
import org.opt4j.viewer.WidgetParameters;

import com.google.inject.Inject;

// The SalesmanWidgetService is an additional feature of this tutorial. It
// enables the visualization
// of a single route in the viewer.
public class VRPWidgetService implements IndividualMouseListener {

	// Panel that paints a single SalesmanRoute (which is the phenotype of an
	// Individual)
	public static class MyPanel extends JPanel {
		private static Color[] myColors= {
				Color.black, Color.blue, Color.cyan, Color.darkGray, Color.gray, Color.green, Color.lightGray, 
				Color.magenta, Color.orange, Color.pink, Color.red, Color.yellow
		};
		private static final long serialVersionUID = 1L;

		protected final Individual individual;

		public MyPanel(Individual individual) {
			super();
			this.individual = individual;
			setPreferredSize(new Dimension(208, 208));
		}

		@Override
		protected void paintComponent(Graphics g) {
			Graphics2D g2d = (Graphics2D) g;
			g2d.setBackground(Color.WHITE);
			g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
			g2d.setStroke(new BasicStroke(2f));
			g2d.clearRect(0, 0, 208, 212);


			// escala
			double maxX = 0;
			double maxY = 0;
			double minX = 0;
			double minY = 0;

			VRPRoutes vrpRoutes = (VRPRoutes) individual.getPhenotype();
			for(int k = 0; k < vrpRoutes.size(); k++) {
				VRPRoute vrpRoute = vrpRoutes.get(k);
				// escala
				if(k == 0) {
					maxX = vrpRoute.get(0).getX();
					maxY = vrpRoute.get(0).getY();
					minX = vrpRoute.get(0).getX();
					minY = vrpRoute.get(0).getY();
				}
				for (int i = 0; i < vrpRoute.size(); i++) {
					Point one = vrpRoute.get(i);
					double x1 = one.getX();
					double y1 = one.getY();
					///System.out.println("City:" + x1+" "+y1);
					if (x1 > maxX) maxX = x1;
					if (y1 > maxY) maxY = y1;
					if (x1 < minX) minX = x1;
					if (y1 < minY) minY = y1;
				}
			}
			double offsetX = (minX < 0 )?-minX:minX;
			double offsetY = (minY < 0 )?-minY:minY;
			double escala = 100.0 / (Math.max(maxX-minX,maxY-minY));

			System.out.println("minX= " + minX);
			System.out.println("minY= " + minY);
			System.out.println("offsetX= " + offsetX);
			System.out.println("offsetY= " + offsetY);
			System.out.println("escala= " + escala);

			// trazado de rutas
			//Random rand = new Random();

			for(int k = 0; k < vrpRoutes.size(); k++) {
				VRPRoute vrpRoute = vrpRoutes.get(k);
				g2d.setColor(myColors[k % myColors.length]);
				for (int i = 0; i < vrpRoute.size(); i++) {
					final int j = (i + 1) % vrpRoute.size();
					Point one = vrpRoute.get(i);
					Point two = vrpRoute.get(j);

					int x1 = (int) ((offsetX + one.getX()) * escala * 2) + 4;
					int y1 = 200 - (int) ((offsetY + one.getY()) * escala * 2) + 4;
					int x2 = (int) ((offsetX + two.getX()) * escala * 2) + 4;
					int y2 = 200 - (int) ((offsetY + two.getY()) * escala * 2) + 4;

					/// System.out.printf("(%d %d) -> (%d %d)\n",x1,y1,x2,y2);

					g2d.drawLine(x1, y1, x2, y2);
					g2d.drawOval(x1 - 2, y1 - 2, 4, 4);

				}
			}
		}
		
	}



	// Use a custom widget
	@WidgetParameters(title = "Route", resizable = false, maximizable = false)
	protected static class VRPWidget implements Widget {

		private final Individual individual;

		public VRPWidget(Individual individual) {
			super();
			this.individual = individual;
		}

		@Override
		public JPanel getPanel() {
			JPanel panel = new MyPanel(individual);
			return panel;
		}

		@Override
		public void init(Viewport viewport) {
		}

	}

	protected final Viewport viewport;

	// The route is shown by a double click of a individual in the archive
	// monitor panel. Thus we need the ArchiveMonitorPanel and the main
	// GUIFrame.
	@Inject
	public VRPWidgetService(Viewport viewport) {
		this.viewport = viewport;
	}

	// If an individual is double clicked, paint the route.
	@Override
	public void onDoubleClick(Individual individual, Component table, java.awt.Point  p) {
		paintRoute(individual);
	}

	// If an individual is clicked with the right mouse button, open a popup
	// menu that contains the option to paint the route.
	@Override
	public void onPopup(final Individual individual, Component table, java.awt.Point  p, JPopupMenu menu) {
		JMenuItem paint = new JMenuItem("show route");
		menu.add(paint);

		paint.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				paintRoute(individual);
			}
		});

	}

	// Paint the route: Construct a JInternalFrame, add the MyPanel and add the
	// frame to the desktop of the main GUIFrame.
	protected void paintRoute(Individual individual) {
		Widget widget = new VRPWidget(individual);
		viewport.addWidget(widget);
	}


}
