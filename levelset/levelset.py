import numpy as np
from scipy.ndimage import gaussian_filter, laplace

class LevelSet:
    rho = 6.0
    mu = 0.04
    nu = 1.0
    lamb = 5.0
    tau = 5.0
    epsilon = 1.5

    def __init__(self, src):
        self.img = src
        self.phi = np.zeros(self.img.shape)
        self.edge_func = self.calcEdgeFunc()
        self.initContour()
        
        self.min_phi = np.zeros(self.phi.shape)
        self.min_energy = self.calcEnergy(self.phi)
        self.min_phi[:, :] = self.phi[:, :]

    def initContour(self):
        width = self.phi.shape[1]
        height = self.phi.shape[0]

        left = width // 4
        right = width - left
        top = height // 4
        bottom = height - top

        self.phi[top + 1:bottom, left + 1:right] = -self.rho
        self.phi[:top, :] = self.phi[bottom + 1:] = self.phi[:, :left] = self.phi[:, right + 1:] = self.rho

    def calcEdgeFunc(self):
        gauss = gaussian_filter(self.img, 5)
        dx, dy = np.gradient(gauss)
        return 1.0 / (1.0 + np.hypot(dx, dy))

    def iterate(self):
        delta = np.zeros(self.phi.shape)
        delta[np.where(np.abs(self.phi) < self.epsilon)] = 1 / (2 * self.epsilon) * (
            1 + np.cos(self.phi[np.where(np.abs(self.phi) < self.epsilon)] * np.pi / self.epsilon))
        dx, dy = np.gradient(self.phi)
        norm_inv = 1.0 / (np.hypot(dx, dy) + 0.001)

        dinner = self.calcDeltaInnerEnergy2(dx, dy, norm_inv)
        dline = self.calcDeltaLineEnergy(dx, dy, norm_inv, delta)
        dregion = self.calcDeltaRegionEnergy(delta)

        dphi = self.mu * dinner + self.lamb * dline + self.nu * dregion
        tmp_phi = self.phi + self.tau * dphi
        tmp_energy = self.calcEnergy(tmp_phi)
        self.phi += self.tau * dphi

        if (tmp_energy < self.min_energy):
            self.min_energy = tmp_energy
            self.min_phi[:, :] = self.phi[:, :]
            
        return tmp_phi, dinner, dline, dregion, dphi

    def calcDeltaInnerEnergy(self, dx, dy, norm_inv):
        phi_lap = laplace(self.phi)
        norm_dx = dx * norm_inv
        norm_dy = dy * norm_inv
        dxx, dxy = np.gradient(norm_dx)
        dyx, dyy = np.gradient(norm_dy)
        return phi_lap - (dxx + dyy)

    def calcDeltaInnerEnergy2(self, dx, dy, norm_inv):
        norm_dx = (1.0 - norm_inv) * dx
        norm_dy = (1.0 - norm_inv) * dy
        dxx, dxy = np.gradient(norm_dx)
        dyx, dyy = np.gradient(norm_dy)
        return dxx + dyy

    def calcDeltaLineEnergy(self, dx, dy, norm_inv, delta):
        edged_norm = self.edge_func * norm_inv
        dxx, dxy = np.gradient(edged_norm * dx)
        dyx, dyy = np.gradient(edged_norm * dy)
        return delta * (dxx + dyy)

    def calcDeltaRegionEnergy(self, delta):
        return self.edge_func * delta

    def calcInnerEnergy(self, levelset):
        dx, dy = np.gradient(levelset)
        return np.sum(((dx * dx + dy * dy) ** 0.5 - 1) ** 2)

    def calcLineEnergy(self, levelset):
        delta = np.zeros(levelset.shape)
        delta[np.where(np.abs(levelset) < self.epsilon)] = 1 / (2 * self.epsilon) * (
            1 + np.cos(levelset[np.where(np.abs(levelset) < self.epsilon)] * np.pi / self.epsilon))
        dx, dy = np.gradient(levelset)
        norm_inv = 1.0 / (np.hypot(dx, dy) + 0.001)
        return np.sum(self.edge_func * delta * (dx * dx + dy * dy) ** 0.5)

    def calcRegionEnergy(self, levelset):
        return np.sum(self.edge_func * np.heaviside(-levelset, 0.5))

    def calcEnergy(self, levelset):
        return self.mu * self.calcInnerEnergy(levelset) + self.lamb * self.calcLineEnergy(levelset) + self.nu * self.calcRegionEnergy(levelset)
