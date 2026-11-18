package org.opt4j.CAE.VRP;

import org.opt4j.viewer.VisualizationModule;

/**
 * Módulo para generar una ventana gráfica que muestre las rutas de la solución al VRPProblem
 * @author puente
 *
 */
public class VRPWidgetXLModule extends VisualizationModule {

	public void config() {
		addIndividualMouseListener(VRPWidgetXLService.class);
	}
}
