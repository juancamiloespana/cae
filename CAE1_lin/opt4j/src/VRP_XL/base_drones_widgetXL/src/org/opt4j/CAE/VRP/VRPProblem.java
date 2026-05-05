

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



	/**
	 * Constructor del problema VRP
	 * Nota: como veis los métodos etiquetados por @Inject pueden estar alimentados por parámetos de entrada GUI (atributos etiquetados como @Constant)
	 * (ver {@link VRPModule}) 
	 * @param size número de clientes
	 * @param totalVehicles total de vehículos
	 * @param fileName nombre del fichero CSV conteniendo las coordenadas de los clientes
	 */
	@Inject
	public VRPProblem(@Constant(value = "clientes") int size, @Constant(value = "vehiculos") int totalVehicles,  @Constant(value = "nombre fichero") String fileName ) {
		// VRP: todos los vehiculos salen de la misma base que esta controlStation ubicada en el punto (0,0)
		base = new Client(0,0); // estacion de control de los vehiculos

		if(fileName.length() >0)
			// leemos el grafo de puntos desde fichero
			this.readInstance(fileName);
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

	/**
	 * carga una instancia VRP desde un fichero CSV con las coordenadas de los clientes
	 * @param fileName nombre del fichero
	 */
	// cargamos una instancia desde fichero
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