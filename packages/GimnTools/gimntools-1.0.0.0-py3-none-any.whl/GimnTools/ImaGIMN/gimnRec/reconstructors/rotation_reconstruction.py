from GimnTools.ImaGIMN.image import image
from GimnTools.ImaGIMN.gimnRec.backprojectors import *
from GimnTools.ImaGIMN.gimnRec.projectors import *
from GimnTools.ImaGIMN.gimnRec.reconstruction_filters import *
from GimnTools.ImaGIMN.processing.interpolators.reconstruction import *
from GimnTools.ImaGIMN.gimnRec.corrections import *
from scipy.ndimage import gaussian_filter
from matplotlib import pyplot as plt


import numpy as np

class rotation_reconstructor(image):
    """
    @brief Creates a Reconstructor class that will inherit the image class.

    The sinogram order inside our program is:
    - rows: slice
    - columns: distances
    - Z: angles

    The sinogram order list must have the following names, but the order can change:
    - ("slice", "distances", "angles")
    """

    __sinogram_order_recon = ("slice", "distances", "angles")  # Sinogram order inside our program
    __center_of_rotation = None  # Center of rotation
    __sinogram_order = None  # Sinogram Order, used for repositioning the dimensions following the order needed to reconstruct
    __sinogram = None
    __reconstructed_mlem = None
    __reconstructed_osem = None
    __reconstructed_fbp = None

    def __init__(self, path=None, sinogram=None, sinogram_order=("slice", "angles", "distances"), center_of_rotation=None, transpose=None):
        """
        @brief Constructs the reconstructor class, it will initiate the super class of reconstructor, that inherits an image class.

        The image class will be responsible for opening the dicom and retrieving its pixels as a numpy object.

        @param path Path to the image file
        @param sinogram Sinogram data
        @param sinogram_order Order of the sinogram dimensions, default is ("slice", "angles", "distances")
        @param center_of_rotation Center of rotation
        @param transpose Flag to transpose the sinogram
        """
        #super(rotation_reconstructor, self).__init__(path=path, image=sinogram)
        self.__sinogram_order = sinogram_order
        self.__sinogram = self.pixels

    @property
    def sinogram(self):
        """
        @brief Returns the sinogram pixels as a numpy object
        @return Sinogram as a numpy array
        """
        return self.__sinogram

    def set_sinogram(self, sinogram):
        """
        @brief Sets the sinogram data.

        @param sinogram Sinogram data to set
        """
        self.__sinogram = sinogram

    def set_img(self, img):
        """
        @brief Sets the image.

        @param img Image data to set
        """
        self.__img = img

    def set_center_of_rotation(self, center_of_rotation):
        """
        @brief Sets the value for the center of rotation.

        @param center_of_rotation Center of rotation value
        """
        self.__center_of_rotation = center_of_rotation

    def mlem(self, iterations, interpolation, angles, verbose=False):
        """
        @brief Reconstructs the sinogram using the Maximum Likelihood Expectation Maximization (MLEM) algorithm for a given number of iterations.

        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.

        @param iterations Number of iterations
        @param interpolation Interpolator to be used, can be: linear_interpolation, beta_spline_interpolation, bilinear_interpolation, or beta_spline_interpolation_o5
        @param angles Angles for reconstruction, should be a numpy array of angles in radians
        @param verbose Flag to print the iteration number during reconstruction

        @return Reconstructed image using the MLEM algorithm
        """
        if self.sinogram is None:
            print("No sinogram Loaded")
            return -1

        slices = self.sinogram.shape[0]
        pixels = self.sinogram.shape[1]
        rec = np.ones((self.sinogram.shape[0], self.sinogram.shape[1], self.sinogram.shape[1]))

        for slice_z in range(slices):
            sinogram = self.sinogram[slice_z, :, :]
            imagem_estimada = np.ones([pixels, pixels])

            for it in range(iterations):
                if verbose:
                    print("iteration- ", it)

                imagem_estimada = np.nan_to_num(gaussian_filter(imagem_estimada, 0.1), copy=True, nan=1)
                proje_estimada = radon_m(imagem_estimada, angles, interpolation, center=self.__center_of_rotation)
                diff = sinogram / (proje_estimada + 10e-9)
                imagem_estimada = iradon_m(diff, interpolation, angles) * imagem_estimada

            rec[slice_z, :, :] = imagem_estimada

        self.__reconstructed_mlem = rec
        return rec
    

    def osem(self, iterations, subsets_n, interpolation, angles, verbose=False, normalize=False):
        """
        @brief Reconstructs the sinogram using the Ordered Subset Expectation Maximization (OSEM) algorithm.
        
        @param iterations Number of iterations
        @param subsets_n Number of subsets
        @param interpolation Interpolator function
        @param angles Array of projection angles in radians
        @param verbose Print progress information
        @param normalize Normalize output image
        
        @return Reconstructed image
        """
        slices = self.sinogram.shape[0]
        pixels = self.sinogram.shape[1]
        rec = np.ones((slices, pixels, pixels))

        for slice_z in range(slices):
            if verbose:
                print(f"Processing slice {slice_z+1}/{slices}")
                
            sinogram = self.sinogram[slice_z, :, :]
            
            # 1. Randomize projection order for better convergence
            random_indices = np.random.permutation(len(angles))
            shuffled_angles = angles[random_indices]
            shuffled_sinogram = sinogram[:, random_indices]
            
            # 2. Split into subsets
            angles_subsets = np.array_split(shuffled_angles, subsets_n)
            sinogram_subsets = np.array_split(shuffled_sinogram, subsets_n, axis=1)
            
            # 3. Initialize reconstruction and normalization factor (sensibility image)
            reconstruction = np.ones((pixels, pixels))
            norm_factor = np.zeros((pixels, pixels))
            
            # 4. Precompute normalization factor (backprojection of 1s)
            for i in range(subsets_n):
                ones_proj = np.ones_like(sinogram_subsets[i])
                norm_factor += backprojector(ones_proj, angles_subsets[i], 
                                        interpolation, 
                                        center=self.__center_of_rotation)
            
            # Avoid division by zero
            norm_factor[norm_factor == 0] = 1e-6

            # 5. OSEM iterations
            for it in range(iterations):
                if verbose:
                    print(f"Iteration {it+1}/{iterations}")
                    
                for i in range(subsets_n):
                    # Forward projection
                    proj_estimate = projector(reconstruction, 
                                            angles_subsets[i], 
                                            interpolation,
                                            center=self.__center_of_rotation)
                    
                    # Calculate correction factor
                    corr = sinogram_subsets[i] / (proj_estimate + 1e-9)
                    
                    # Backproject correction factor
                    bp_corr = backprojector(corr, angles_subsets[i], 
                                        interpolation,
                                        center=self.__center_of_rotation)
                    
                    # OSEM update
                    reconstruction *= bp_corr / norm_factor
                    
                    # Optional: Display intermediate results
                    if verbose and it % 5 == 0:
                        plt.imshow(reconstruction)
                        plt.title(f"Slice {slice_z} - Iteration {it+1}")
                        plt.colorbar()
                        plt.show()
            
            rec[slice_z, :, :] = reconstruction

        if normalize:
            rec = self.normalize(rec)
        
        self.__reconstructed_osem = rec
        return rec

    def fbp(self, interpolation, filter_type, angles):
        """
        @brief Reconstructs the sinogram using the Filtered Back-Projection (FBP) algorithm.

        @param interpolation Interpolator to be used, can be: linear_interpolation, beta_spline_interpolation, bilinear_interpolation, or beta_spline_interpolation_o5
        @param filter_type Filter to be used in the FBP, can be: cossineFilter or ramLak
        @param angles Angles for reconstruction, should be a numpy array of angles in radians

        @return Reconstructed image using the FBP algorithm
        """
        if self.sinogram is None:
            print("No sinogram Loaded")
            return -1

        slices = self.sinogram.shape[0]
        rec = np.ones((self.sinogram.shape[0], self.sinogram.shape[1], self.sinogram.shape[1]))

        for slice_z in range(slices):
            sinogram = self.sinogram[slice_z, :, :]
            filtered = apply_filter_to_sinogram(filter_type, sinogram)
            rec[slice_z, :, :] = iradon_m(filtered, interpolation, center=self.__center_of_rotation, angles=angles)

        self.__reconstructed_fbp = rec
        return rec

    def slice_n(self):
        """
        @brief Counts the total number of counts for each slice.

        @return Array containing the total counts for each slice
        """
        slice_count = np.zeros(self.sinogram.shape[0])
        for slice_sino in range(self.sinogram.shape[0]):
            slice_count[slice_sino] = self.sinogram[slice_sino, :, :].sum()
        return slice_count

    def normalize(self, image):
        """
        @brief Normalize the sinogram.

        @param image Image to normalize

        @return Normalized image
        """
        norm = np.zeros(image.shape)
        slices_n = self.slice_n()
        image = image[:]
        # Additional normalization logic can be added here
        return norm
