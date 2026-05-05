package org.opt4j.CAE.VRP;

import java.util.ArrayList;
import java.util.Collections;

import org.opt4j.core.Objective.Sign;
import org.opt4j.core.Objectives;
import org.opt4j.core.problem.Evaluator;

/**
 * El {@link VRPEvaluator} genera los valores de las funciones objetivo a partir 
 * del fenotipo {@link VRPRoutes} generado por {@link VRPDecoder}.
 * Genera el conjunto de objetivos {@link Objectives} asociados a la solución 
 * representada por el fenotipo.
 * 
 * @author puente@uniovi.es
 * 
 */
public class VRPEvaluator implements Evaluator<VRPRoutes> {
	
	/**
	 * evalua un fenotipo calculando el vector de funciones objetivo
	 * @param vprRoutes fenotipo a evaluar
	 * @return vector de valores de funciones Objetivo
	 */
	public Objectives evaluate(VRPRoutes vprRoutes) {
		double dist = 0;
		int nVehicles = 0;
		// para cada vehículo calcula las distancias de la ruta de clientes que 
		// tiene que visitar
		ArrayList<Double> distances = new ArrayList<Double>();
		for (VRPRoute vprroute: vprRoutes){
			double distAux = 0;
			for (int i = 0; i < vprroute.size(); i++) {
				Point one = vprroute.get(i);
				Point two = vprroute.get((i + 1) % vprroute.size());
				distAux +=  one.distance(two);
			}
			distances.add(distAux);
			if (distAux > 0)
				nVehicles++;
		}
		
		// se fijan ahora los objetivos a evaluar		
		Objectives objectives = new Objectives();
		
		// máxima distancia
		dist = Collections.max(distances);
		objectives.add("max_distance", Sign.MIN, dist);
		// número de vehiculos utilizados
		objectives.add("num_vehicles", Sign.MIN, nVehicles);
		
		return objectives;
	}
}