

package org.opt4j.CAE.VRP;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Random;
import java.util.Scanner;
import org.opt4j.core.start.Constant;
import com.google.inject.Inject;

/**
 * El {@link VRPProblem} modela un VRP básico, i.e., una colección 
 * de {@link Item} que son los {@link Client} ciudades a visitar y los vehículos {@link Vehicle} que deben visitarlos.
 * 
 * @author puente@uniovi.es
 * 
 */
public class VRPProblem {
	/** El conjunto de clientes */
	protected ArrayList<Item> clients = new ArrayList<Item>();
	/** El conjunto de vehiculos */
	protected ArrayList<Item> vehicles = new ArrayList<Item>(); 

	/** Máximo total de vehículos a utilizar */
	protected int totalVehicles; 
	/** la estación de control ({@link Client}) */
	protected Client base;  

	/**
	 * Clase abstracta para modelar clientes y vehículos
	 * @author puente
	 *
	 */
	public abstract class Item {
	}

	/**
	 * Clase vehículo
	 * @author puente
	 *
	 */
	public class Vehicle extends Item {
		private int id;

		public Vehicle(int id){
			this.id = id;
		}

		public int getId() {
			return id;
		}

		@Override
		public String toString(){
			return String.format("(Vehic.)");
		}	
	}

	/**
	 * Clase cliente
	 * @author puente
	 *
	 */
	public class Client extends Item{
		/**
		 * coordenadas del cliente
		 */
		protected final Point p;

		/**
		 * Constructor del cliente
		 * @param x coordenada x
		 * @param y coordenada y
		 */
		public Client(double x, double y) {
			this.p = new Point(x, y);
		}

		public double getX() {
			return p.getX();
		}
		public double getY() {
			return p.getY();
		}
		public Point getPoint() {
			return p;
		}
		

		@Override
		public String toString(){
			return p.toString();
		}
	}

	public class Swept extends Client {
		protected final Point p2;

		public Swept(double x, double y, double x2, double y2) {
			super(x, y);
			this.p2 = new Point(x2, y2);
		}

		public double getY2() {
			return p2.getY();
		}

		public Point getPoint2() {
			return p2;
		}

		@Override
		public String toString() {
			return String.format("[%s,%s]", getPoint(), getPoint2());
		}
	}

	/**
	 * Constructor del problema VRP
	 * Nota: como veis los métodos etiquetados por @Inject pueden estar alimentados por parámetos de entrada GUI (atributos etiquetados como @Constant)
	 * (ver {@link VRPModule}) 
	 * @param size número de clientes
	 * @param totalVehicles total de vehículos
	 * @param fileName nombre del fichero CSV conteniendo las coordenadas de los clientes
	 */
	@Inject
	public VRPProblem(@Constant(value = "clientes") int size, 
		@Constant(value = "vehiculos") int totalVehicles,  
		@Constant(value = "swept file") String fileName,
		@Constant(value = "control station file") String fileNameCS) {
		// VRP: todos los vehiculos salen de la misma base que esta controlStation ubicada en el punto (0,0)
		if (fileNameCS.length() > 0) {
    		readCS(fileNameCS);
		} else {
   			 base = new Client(0, 0); // est
		}
		
		if(fileName.length() >0)
			// leemos los barridos desde fichero
			this.readSwepts(fileName);
		else
		{
			// generamos size items de tipo Point con coordenadas al azar
			Random random = new Random(0);
			for (int i = 0; i < size; i++) {
				final double x = random.nextDouble() * 100;
				final double y = random.nextDouble() * 100;
				final Item point = new Client(x, y);
				clients.add(point);
			}
		}
		// VRP: la aportación es que añadimos totalVehicles items de tipo Vehicle en el array de items 
		this.totalVehicles = totalVehicles;
		for(int x = 0; x < totalVehicles; x++) 
			vehicles.add(new Vehicle(x));
	}

	private void readCS(String fileNameCS) {
		double x1, y1;
		try (Scanner fin = new Scanner(new FileInputStream(fileNameCS))) {
			fin.useLocale(Locale.ENGLISH);
			fin.nextLine();
			x1 = fin.nextDouble();
			y1 = fin.nextDouble();
			base = new Client(x1, y1);
		} catch (IOException e) {
			System.err.println("Error leyendo el fichero de CS: " + e.getMessage());
		}
	}

	private void readSwepts(String fileName) {
		Scanner fin = null;
		try {
			fin = new Scanner(new FileInputStream(fileName));
			fin.useLocale(Locale.ENGLISH);
			fin.nextLine(); // saltamos cabecera X1 Y1 X2 Y2
			while (fin.hasNext()) {
				double x1 = fin.nextDouble();
				double y1 = fin.nextDouble();
				double x2 = fin.nextDouble();
				double y2 = fin.nextDouble();
				clients.add(new Swept(x1, y1, x2, y2));
			}
		} catch (IOException e) {
			System.err.println("Error leyendo el fichero de barridos: " + e.getMessage());
		} finally {
			if (fin != null) fin.close();
		}
	}

	private void readInstance(String fileName) {
		Scanner fin = null;
		int  x1,y1;
		try {
			fin = new Scanner(new FileInputStream(fileName));
			// utilizar '.' como separador decimal
			fin.useLocale(Locale.ENGLISH); 
			fin.nextLine(); // saltamos cabeceras
			while(fin.hasNext()) {
				fin.nextInt(); // leemos id
				x1 = (int)fin.nextFloat();
				y1 = (int)fin.nextFloat();
				clients.add(new Client(x1,y1));
			}

		}catch(IOException e) {
			System.err.println("Error leyendo el fichero del grafo:" + e.getMessage());
		}finally {
			if (fin != null)
				fin.close();
		}

	}
	public ArrayList<Item> getClients() {
		return clients;
	}
	public ArrayList<Item> getVehicles() {
		return vehicles;
	}
	public int getTotalVehiculos() {
		return totalVehicles;
	}
	/** observador de la estación base 
	 * @return la estación base
	 **/
	public Client getBase() {
		return base;
	}
}