## Indexa API Rates

Este modulo utiliza la [api de indexa](https://api.indexa.do/) para actualizar la tasa de cambio de las diferentes monedas.

**Bancos disponibles:**

Banco | Monedas|
--- | --- | 
Banco Popular Dominicano|USD,EUR
Banco de Reservas|USD,EUR
Banco Lopez de Haro|USD,EUR
Banco del Progreso|USD,EUR
Banco Santa Cruz|USD,EUR
Banco BDI|USD,EUR
Banco Promerica|USD
Banco Vimenca|USD,EUR

## Installation

Instalacion como cualquier otro modulo. Nada en especial.

## Configuration

1. ir al menu ajustes/tecnico/parametros del sistema.
   * En la key: indexa_api_token agregar el token suministrado por [indexa.do](https://indexa.do)
2. Ir al menu facturacion/configuracion/configuracion
   * En el apartado **Monedas** Expecificar el Bank de donde desee que se actualize las tazas, el intervalo o frecuencia que desee que se actualize y la fecha cuando seria la proxima actualizacion.
   * Tiene un boton para poder ejecutar manualmente la accion que actualiza las tasas.

## Contributors
* [GrowIT](https://growit.com.do)
* [Indexa](https://indexa.do)

## Issue - Roadmap
* Mostrar check en la configuracion para instalar y desinstalar el modulo
