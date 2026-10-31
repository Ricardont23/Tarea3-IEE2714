# Tarea3-IEE2714
Repositorio de códigos e imágenes (y demás) usados para el desarrollo de la tarea 2.  

## Pregunta 1

> La imagen `P1.CR2` debe encontrarse dentro de la carpeta `Imagenes/` del repositorio.

El archivo `FiltroNotch_1.py` contiene todas las funciones necesarias para la correcta ejecución del código. Se desarrolla la lectura de la imagen, el padding configurable, la transformada de Fourier 2D, la construcción de los filtros notch reject (ideal y Gaussiano), la aplicación del filtro sobre el espectro complejo y el recorte posterior al tamaño original.

Las funciones principales son:

- `cargar_imagen`: lee el archivo `.CR2` con `rawpy`, normaliza la imagen al rango [0, 1] y entrega su tamaño `(M, N)`.
- `padding` / `des_padding`: extienden la imagen (`constant`, `edge`, `reflect`, etc.) y recortan el resultado al tamaño original después de la IFFT.
- `aplicar_transformada`: calcula la FFT 2D centrada (`fftshift`) y entrega magnitud (escala logarítmica), fase, parte real, parte imaginaria y el espectro complejo.
- `construir_filtro_notch`: construye la función de transferencia `H(u,v)` con uno o más pares simétricos de notches, de tipo `ideal` o `gaussiano`.
- `aplicar_filtro`: multiplica el espectro complejo por `H(u,v)`, aplica `ifftshift` e IFFT 2D y se queda con la parte real.

Posterior a la definición de las funciones se encuentran las líneas del código principal a ser ejecutadas.

```ruby

(...)
pad_m, pad_n = 256, 256
frecuencias = [(0, 1072)]
frecuencia_corte = 40.0
desv_est = 40.0

imagen_gris, M, N = cargar_imagen('Imagenes/P1.CR2')
imagen_gris_pad = padding(imagen_gris, 'reflect', pad_m, pad_n) # constant/edge/reflect

filtro_ideal = construir_filtro_notch(imagen_gris_pad, 'ideal', frecuencias, frecuencia_corte, (M,N))
filtro_gaussiano = construir_filtro_notch(imagen_gris_pad, 'gaussiano', frecuencias, desv_est, (M,N))

magnitud_log, fase, parte_im, parte_real, fft = aplicar_transformada(imagen_gris_pad)

imagen_filtro_p_i = aplicar_filtro(fft, filtro_ideal)
imagen_filtro_p_g = aplicar_filtro(fft, filtro_gaussiano)

imagen_filtro_i = des_padding(imagen_filtro_p_i, (M, N), (pad_m, pad_n))
imagen_filtro_g = des_padding(imagen_filtro_p_g, (M, N), (pad_m, pad_n))
(...)
```

En este fragmento de código se definen los parámetros del procesamiento:

- `pad_m`, `pad_n`: cantidad de píxeles que se extienden en cada borde (filas y columnas). Con `0, 0` no se aplica padding.
- El segundo argumento de `padding` define el tipo de extensión (`'constant'`, `'edge'`, `'reflect'`).
- `frecuencias`: lista con las posiciones de los notches. Cada elemento `(u, v)` es la distancia, medida **en bins del espectro de la imagen original (sin padding)**, desde el centro del espectro hasta uno de los notches. Para cada elemento el código crea automáticamente el notch simétrico en `(-u, -v)`. Se pueden agregar más pares a la lista.
- `frecuencia_corte`: radio $D_0$ del filtro ideal (en bins del espectro sin padding).
- `desv_est`: desviación estándar $\sigma$ del filtro Gaussiano (en bins del espectro sin padding).

> Las posiciones y los anchos se reescalan internamente según el tamaño del padding (`P/M` y `Q/N`), por lo que no es necesario recalcularlos al cambiar `pad_m` y `pad_n`.

Consiguiente a la definición de variables, se calcula el espectro de la imagen filtrada, las imágenes diferencia (imagen ruidosa − imagen filtrada) y se definen una serie de líneas para poder graficar y obtener las distintas imágenes utilizadas para el informe.

```ruby

(...)

'''Para poder visualizar correctamente las diferentes graficas, hay que descomentar la requerida y comentar las demás.'''
#=============================================================================================================

'''Grafica del espectro de la imagen filtrada (ideal o gaussiano)'''
plt.imshow(magnitud_log_filtrada_i[0], cmap='gray')
#plt.imshow(magnitud_log_filtrada_g[0], cmap='gray')

'''Grafica de Parte Real, Parte Imaginaria, Magnitud (log) y Fase del espectro'''
# Bloque comentado entre comillas triples: quitar las comillas para activarlo.

'''Grafica comparativa de la imagen original y las imagenes filtradas'''
fig2, axes = plt.subplots(1,3)

'''Grafica de las imagenes diferencia (escala fija entre -0.010 y 0.010)'''
fig3, axes1 = plt.subplots(1,2)
(...)

plt.tight_layout()
plt.show()
```

Para el uso correcto **se debe descomentar la línea o bloque deseado, mientras los demás siguen comentados** y posteriormente ejecutar el código.

> Al hacer uso de un solo `plt.show()`, las figuras que estén activas se abren simultáneamente (una ventana por figura). Si solo se necesita una, se deben comentar las demás.

> Las imágenes diferencia se grafican con una escala común y simétrica (`vmin=-0.010`, `vmax=0.010`), para que los distintos casos sean comparables. Si se cambia el rango, hay que usar el mismo valor en todas las figuras que se comparen.

Por último, se encuentra el código en el que se evalúa el espectro en una frecuencia afectada por el notch, mostrando el valor complejo antes del filtrado, el valor de $H(u,v)$ aplicado y el valor resultante.

```ruby
u_spot = (imagen_gris_pad.shape[0] // 2) + frecuencias[0][0]
v_spot = (imagen_gris_pad.shape[1] // 2) + frecuencias[0][1]

val_antes = fft[u_spot, v_spot]
val_H = filtro_gaussiano[u_spot, v_spot] 
val_despues = val_antes * val_H
print(f"Antes: {val_antes} | H(u,v): {val_H} | Después: {val_despues}")
```

> Este resultado se muestra en la consola. Si se está visualizando una imagen, se debe cerrar para que se impriman los datos.

### Advertencias y consideraciones

**Para el uso correcto se debe descomentar la línea deseada, mientras las demás siguen comentadas y posteriormente ejecutar el código.**

**Las posiciones de los notches (`frecuencias`) y los anchos (`frecuencia_corte`, `desv_est`) se entregan en bins del espectro de la imagen sin padding. Si se mide la posición de un pico directamente sobre el espectro con padding.**

**El filtro se aplica sobre el espectro complejo (no por separado sobre magnitud y fase). Los espectros mostrados en escala logarítmica son solo para visualización.**

## Pregunta 2

