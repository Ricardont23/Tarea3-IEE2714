import numpy as np
import matplotlib.pyplot as plt
import cv2



def psf_a_otf(psf: np.ndarray, shape_img: tuple) -> np.ndarray:

    M, N = shape_img
    kh, kw = psf.shape
    
    psf_norm = psf.astype(np.float64) / np.sum(psf)
    
    h_pad = np.zeros((M, N), dtype=np.float64)
    h_pad[:kh, :kw] = psf_norm
    
    centro_h, centro_w = kh // 2, kw // 2
    h_pad = np.roll(h_pad, -centro_h, axis=0)
    h_pad = np.roll(h_pad, -centro_w, axis=1)
    
    H = np.fft.fft2(h_pad)
    return H



def aplicar_H(img: np.ndarray, H: np.ndarray) -> np.ndarray:
    return np.real(np.fft.ifft2(H * np.fft.fft2(img)))


def generar_observacion(x: np.ndarray, H: np.ndarray, sigma_ruido: float, semilla: int = 42) -> np.ndarray:
    
    rng = np.random.default_rng(semilla)
    y_limpia = aplicar_H(x, H)
    ruido = rng.normal(loc=0.0, scale=sigma_ruido, size=x.shape)
    return y_limpia + ruido

def calcular_rmse(x_ideal: np.ndarray, x_est: np.ndarray) -> float:
    return float(np.sqrt(np.mean((x_ideal - x_est) ** 2)))


def filtro_wiener(y: np.ndarray, H: np.ndarray, K: float, eps: float = 1e-15) -> np.ndarray:

    Y = np.fft.fft2(y)
    H_conj = np.conj(H)
    H_mag_sq = np.abs(H) ** 2
    
    denominador = H_mag_sq + K

    denominador = np.where(denominador == 0, eps, denominador)
    
    X_hat = (H_conj * Y) / denominador
    x_restaurada = np.real(np.fft.ifft2(X_hat))
    return x_restaurada


def perturbar_psf(psf: np.ndarray, factor_gamma: float = 0.75) -> np.ndarray:

    psf_pert = np.power(np.maximum(psf, 0), factor_gamma)
    return psf_pert / np.sum(psf_pert)


imgagen_gris = cv2.imread('Imagenes/cameraman.jpg', cv2.IMREAD_GRAYSCALE)
imgagen_gris = imgagen_gris.astype(np.float64) / 255.0

psf =  cv2.imread('Imagenes/psf.png', cv2.IMREAD_GRAYSCALE).astype(np.float64)

M, N = imgagen_gris.shape 

otf = psf_a_otf(psf, (M, N))

imgagen_degradada = aplicar_H(imgagen_gris, otf)