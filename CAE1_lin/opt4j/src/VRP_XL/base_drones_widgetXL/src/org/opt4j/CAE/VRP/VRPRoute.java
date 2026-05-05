package org.opt4j.CAE.VRP;
import java.util.ArrayList;
/**
 * Una ruta asociada a un vehículo en el conjunto de rutas que constituye 
 * la solución a un problema VRP básico.
 * 
 * @author puente@uniovi.es
 *
 */
public class VRPRoute extends ArrayList<Point> {

	private static final long serialVersionUID = 1L;
	/**
	 * identificador del vehiculo al que pertenece la ruta
	 */
	private int vehicleId;
	
	/**
	 * crea una ruta vacía para un vehiculo 
	 * @param vehicleId identificador del vehiculo
	 */
	public VRPRoute(int vehicleId){
		this.vehicleId = vehicleId;
	}
	
	public int getVehicleId() {
		return vehicleId;
	}
	@Override
	public String toString(){
		return "ID" + vehicleId + super.toString();
	}
}
