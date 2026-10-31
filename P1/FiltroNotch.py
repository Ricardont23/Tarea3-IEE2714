import numpy as np
import matplotlib.pyplot as plt
import rawpy



def cargar_imagen(path: str):

    with rawpy.imread(path) as raw:
        imagen = raw.raw_image_visible.astype(np.float64)
        imagen = (imagen - np.min(imagen)) / (np.max(imagen) - np.min(imagen))

        M, N = imagen.shape

    return imagen, M, N

def padding(imagen: np.ndarray, tipo: str, factor_m: int, factor_n: int):

    if factor_m == 0 and factor_n == 0:
        return imagen.copy()
    elif tipo == 'constant':
        return np.pad(imagen, ((factor_m, factor_m), (factor_n, factor_n)), mode='constant', constant_values=0 )
    else:
        return np.pad(imagen, ((factor_m, factor_m), (factor_n, factor_n)), mode=tipo )


def aplicar_transformada(imagen: np.ndarray):

    fft_imagen = np.fft.fft2(imagen)
    fft_shifted = np.fft.fftshift(fft_imagen)

    
    parte_real = np.real(fft_shifted)
    parte_im = np.imag(fft_shifted)

    c = 10
    magnitud = abs(fft_shifted)
    magnitud_log = c*np.log(1+ magnitud)
    fase = np.angle(fft_shifted)


    return magnitud_log, fase, parte_im, parte_real, fft_shifted

def construir_filtro_notch(imagen: np.ndarray, modo: str, distancia_frecuencia: list, parametro_D_0: float, tamano_original: tuple):

    P, Q = imagen.shape
    M, N = tamano_original

    escala_p = P / M
    escala_q = Q / N


    escala_promedio = (escala_p + escala_q) / 2.0
    D_0_ajustado = parametro_D_0 * escala_promedio


    centro_p, centro_q = P // 2, Q // 2

    malla_p, malla_q = np.ogrid[0:P, 0:Q]

    H = np.ones((P, Q), dtype=np.float64)

    for distancia_frec_p, distancia_frec_q in distancia_frecuencia:

        df_p_ajustada = int(round(distancia_frec_p * escala_p))
        df_q_ajustada = int(round(distancia_frec_q * escala_q))

        centro_p_frec_pos, centro_q_frec_pos = centro_p + df_p_ajustada, centro_q + df_q_ajustada
        centro_p_frec_neg, centro_q_frec_neg = centro_p - df_p_ajustada, centro_q - df_q_ajustada

        distancia_pos = np.sqrt((malla_p - centro_p_frec_pos)**2 + (malla_q - centro_q_frec_pos)**2)
        distancia_neg = np.sqrt((malla_p - centro_p_frec_neg)**2 + (malla_q - centro_q_frec_neg)**2)

        if modo == "ideal":
            H_pos = (distancia_pos > D_0_ajustado).astype(np.float64)
            H_neg = (distancia_neg > D_0_ajustado).astype(np.float64)
        elif modo == "gaussiano":
            H_pos = 1.0 - np.exp(-distancia_pos**2 / (2.0 * D_0_ajustado**2))
            H_neg = 1.0 - np.exp(-distancia_neg**2 / (2.0 * D_0_ajustado**2))

        H *= (H_neg*H_pos) 

    return H


def aplicar_filtro(fft: np.ndarray, funcion_transferencia):

    imagen_filtrada_frec = fft*funcion_transferencia

    imagen_filtrada_despl = np.fft.ifftshift(imagen_filtrada_frec)
    imagen_filtrada = np.fft.ifft2(imagen_filtrada_despl).real

    return imagen_filtrada

def des_padding(imagen_pad:np.ndarray, tamaño_original: tuple, factor_pad: tuple):

    factor_m, factor_n = factor_pad
    M, N = tamaño_original

    return imagen_pad[factor_m : factor_m + M, factor_n : factor_n + N]


pad_m, pad_n = 1024, 1024
frecuencias = [(0, 1072)]
frecuencia_corte = 20.0
desv_est = 20.0

imagen_gris, M, N = cargar_imagen('Imagenes/P1.CR2')
imagen_gris_pad = padding(imagen_gris, 'constant', pad_m, pad_n) # constant/edge/reflect

filtro_ideal = construir_filtro_notch(imagen_gris_pad, 'ideal', frecuencias, frecuencia_corte, (M,N))
filtro_gaussiano = construir_filtro_notch(imagen_gris_pad, 'gaussiano', frecuencias, desv_est, (M,N))

magnitud_log, fase, parte_im, parte_real, fft = aplicar_transformada(imagen_gris_pad)

imagen_filtro_p_i = aplicar_filtro(fft, filtro_ideal)
imagen_filtro_p_g = aplicar_filtro(fft, filtro_gaussiano)


imagen_filtro_i = des_padding(imagen_filtro_p_i, (M, N), (pad_m, pad_n))
imagen_filtro_g = des_padding(imagen_filtro_p_g, (M, N), (pad_m, pad_n))

magnitud_log_filtrada_i = aplicar_transformada(imagen_filtro_i)
magnitud_log_filtrada_g = aplicar_transformada(imagen_filtro_g)

diferencia_ideal = imagen_gris-imagen_filtro_i
diferencia_gauss = imagen_gris-imagen_filtro_g


print(M,N)

#=============================================================================================================

#plt.imshow(magnitud_log_filtrada_i[0]  , cmap='gray')

#plt.imshow(magnitud_log   , cmap='gray')

#==============================================================================================================
'''
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

im1 = ax1.imshow(parte_real, cmap='gray')
ax1.set_title('Parte Real')
fig.colorbar(im1, ax=ax1)
ax1.axis('off')

im2 = ax2.imshow(parte_im, cmap='gray')
ax2.set_title('Parte Imaginaria')
fig.colorbar(im2, ax=ax2)
ax2.axis('off')

im3 = ax3.imshow(magnitud_log, cmap='gray')
ax3.set_title('Magnitud (Escala Logaritmica)')
fig.colorbar(im3, ax=ax3)
ax3.axis('off')

im4 = ax4.imshow(fase, cmap='gray')
ax4.set_title('Fase')
fig.colorbar(im4, ax=ax4)
ax4.axis('off')
'''

#====================================================================================================================

'''fig2, axes = plt.subplots(1,3)

im1 = axes[0].imshow(imagen_gris, cmap='gray')
axes[0].set_title('Imagen Original')
axes[0].axis('off')

im2 = axes[1].imshow(imagen_filtro_i, cmap='gray')
axes[1].set_title(f'Imagen Filtrada (Ideal -> D_0 = {frecuencia_corte})')
axes[1].axis('off')

im3 = axes[2].imshow(imagen_filtro_g, cmap='gray')
axes[2].set_title(f'Imagen Filtrada (Gauss -> Sigma = {desv_est})')
axes[2].axis('off')'''
#=======================================================================================================================


fig3, axes1 = plt.subplots(1,2)

im1 = axes1[0].imshow(diferencia_ideal, cmap='gray', vmin=-0.010, vmax=0.010)
axes1[0].set_title(f'Imagen Diferencia: Filtro Ideal (Ideal -> D_0 = {frecuencia_corte})')
fig3.colorbar(im1, ax=axes1[0])


im2 = axes1[1].imshow(diferencia_gauss, cmap='gray', vmin=-0.010, vmax=0.010)
axes1[1].set_title(f'Imagen Diferencia: Filtro Gaussiano (Sigma -> D_0 = {desv_est})')
fig3.colorbar(im1, ax=axes1[1])


#===========================================================================================================================

u_spot = imagen_gris_pad.shape[0] // 2 + int(round(frecuencias[0][0] * imagen_gris_pad.shape[0] / M))
v_spot = imagen_gris_pad.shape[1] // 2 + int(round(frecuencias[0][1] * imagen_gris_pad.shape[1] / N))

val_antes = fft[u_spot, v_spot]
val_H = filtro_gaussiano[u_spot, v_spot] 
val_despues = val_antes * val_H
print(f"Antes: {val_antes} | H(u,v): {val_H} | Después: {val_despues}")

plt.tight_layout()
plt.show()