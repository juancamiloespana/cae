package org.opt4j.CAE.VRP;
import java.util.ArrayList;
/**
 * Fenotipo: conjunto de rutas que conforman la solución del problema VRP básico
 * @author puente@uniovi.es
 */
public class VRPRoutes extends ArrayList<VRPRoute> {

	private static final long serialVersionUID = 1L;

	@Override
	public String toString(){
		String s ="";

		for(VRPRoute r: this)
			s += r.toString() + "\n";
		return s;	
	}
}
