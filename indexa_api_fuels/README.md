## Indexa API Fuels

Este modulo utiliza la [api de indexa](https://api.indexa.do/) para actualizar los precios de los combustibles.

**Combustibles disponibles:**
* Gasolina Premium
* Gasolina Regular
* Gasoil Optimo
* Gasoil Regular
* Kerosene
* Gas Natural Vehicular (GNV)
* Gas Licuadode Petroleo (GLP)

## Installation

Instalacion como cualquier otro modulo. Nada en especial.

## Configuration

1. ir al menu ajustes/tecnico/parametros del sistema.
   * En la key: indexa_api_token agregar el token suministrado por [indexa.do](https://indexa.do)
2. Ir al menu Ventas/configuracion/Fuels Price
   * Crear un registro:
      * Selecciona el producto que sera actualizado con el precio
      * Fuel type: 
      * update in: donde se actualizara el precio
         * product: en la ficha del producto, 'Precio de Venta'
         * pricelist: crea un registro en la tarifa seleccionada
              el registro creado sera en un periodo de fecha (sabado a viernes) de la semana en curso.
* Una accion automatica corre cada 7 dias, para actualizar los precios.

## Contributors
* [GrowIT](https://growit.com.do)
* [Indexa](https://indexa.do)

## Issue - Roadmap
* Asignar un nombre al registro
* Multi company
