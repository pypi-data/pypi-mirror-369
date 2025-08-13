import numpy as np 
import os 



class ModuloVKI:
    """
    MODULO (MODal mULtiscale pOd) is a software developed at the von Karman Institute
    to perform Multiscale Modal Analysis using Multiscale Proper Orthogonal Decomposition (mPOD)
    on numerical and experimental data.

    References
    ----------
    - Theoretical foundation:
      https://arxiv.org/abs/1804.09646

    - MODULO framework presentation:
      https://arxiv.org/pdf/2004.12123.pdf

    - Hands-on tutorial videos:
      https://youtube.com/playlist?list=PLEJZLD0-4PeKW6Ze984q08bNz28GTntkR

    Notes
    -----
    MODULO operations assume the dataset is uniformly spaced in both space
    (Cartesian grid) and time. For non-cartesian grids, the user must 
    provide a weights vector `[w_1, w_2, ..., w_Ns]` where `w_i = area_cell_i / area_grid`.
    """

    def __init__(self,
                 data: np.ndarray,
                 N_PARTITIONS: int = 1,
                 FOLDER_OUT: str = './',
                 SAVE_K: bool = False,
                 N_T: int = 100,
                 N_S: int = 200,
                 n_Modes: int = 10,
                 dtype: str = 'float32',
                 eig_solver: str = 'eigh',
                 svd_solver: str = 'svd_sklearn_truncated',
                 weights: np.ndarray = np.array([])):
        """
        Initialize the MODULO analysis.

        Parameters
        ----------
        data : np.ndarray
            Data matrix of shape (N_S, N_T) to factorize. If not yet formatted, use the `ReadData`
            method provided by MODULO. When memory saving mode (N_PARTITIONS > 1) is active,
            set this parameter to None and use prepared partitions instead.

        N_PARTITIONS : int, default=1
            Number of partitions used for memory-saving computation. If set greater than 1,
            data must be partitioned in advance and `data` set to None.

        FOLDER_OUT : str, default='./'
            Directory path to store output (Phi, Sigma, Psi matrices) and intermediate
            calculation files (e.g., partitions, correlation matrix).

        SAVE_K : bool, default=False
            Whether to store the correlation matrix K to disk in
            `FOLDER_OUT/correlation_matrix`.

        N_T : int, default=100
            Number of temporal snapshots. Mandatory when using partitions (N_PARTITIONS > 1).

        N_S : int, default=200
            Number of spatial grid points. Mandatory when using partitions (N_PARTITIONS > 1).

        n_Modes : int, default=10
            Number of modes to compute.

        dtype : str, default='float32'
            Data type for casting input data.

        eig_solver : str, default='eigh'
            Solver for eigenvalue decomposition.

        svd_solver : str, default='svd_sklearn_truncated'
            Solver for Singular Value Decomposition (SVD).

        weights : np.ndarray, default=np.array([])
            Weights vector `[w_1, w_2, ..., w_Ns]` to account for non-uniform spatial grids.
            Defined as `w_i = area_cell_i / area_grid`. Leave empty for uniform grids.
        """

        print("MODULO (MODal mULtiscale pOd) is a software developed at the von Karman Institute to perform "
              "data driven modal decomposition of numerical and experimental data. \n")

        if not isinstance(data, np.ndarray) and N_PARTITIONS == 1:
            raise TypeError(
                "Please check that your database is in an numpy array format. If D=None, then you must have memory saving (N_PARTITIONS>1)")

        if N_PARTITIONS > 1:
            self.MEMORY_SAVING = True
        else:
            self.MEMORY_SAVING = False

            # Assign the number of modes
        self.n_Modes = n_Modes
        # If particular needs, override choice for svd and eigen solve
        self.svd_solver = svd_solver.lower()
        self.eig_solver = eig_solver.lower()
        possible_svds = ['svd_numpy', 'svd_scipy_sparse', 'svd_sklearn_randomized', 'svd_sklearn_truncated']
        possible_eigs = ['svd_sklearn_randomized', 'eigsh', 'eigh']

        if self.svd_solver not in possible_svds:
            raise NotImplementedError("The requested SVD solver is not implemented. Please pick one of the following:"
                                      "which belongs to: \n {}".format(possible_svds))

        if self.eig_solver not in possible_eigs:
            raise NotImplementedError("The requested EIG solver is not implemented. Please pick one of the following: "
                                      " \n {}".format(possible_eigs))

        # if N_PARTITIONS >= self.N_T:
        #     raise AttributeError("The number of requested partitions is greater of the total columns (N_T). Please,"
        #                          "try again.")

        self.N_PARTITIONS = N_PARTITIONS
        self.FOLDER_OUT = FOLDER_OUT
        self.SAVE_K = SAVE_K

        if self.MEMORY_SAVING:
            os.makedirs(self.FOLDER_OUT, exist_ok=True)
        
        # Load the data matrix
        if isinstance(data, np.ndarray):
            # Number of points in time and space
            self.N_T = data.shape[1]
            self.N_S = data.shape[0]
            # Check the data type
            self.D = data.astype(dtype)
        else:
            self.D = None  # D is never saved when N_partitions >1
            self.N_S = N_S  # so N_S and N_t must be given as parameters of modulo
            self.N_T = N_T
        
        '''If the grid is not cartesian, ensure inner product is properly defined using weights.'''
        
        if weights.size == 0:
                print('Modulo assumes you have a uniform grid. If not, please provide weights as parameters.')
        else: 
                if len(weights) == self.N_S:
                        print("The weights you have input have the size of the columns of D \n"
                                  "MODULO has considered that you have already duplicated the dimensions of the weights "
                                  "to match the dimensions of the D columns \n")
                        self.weights = weights
                elif len(weights) == 2 * self.N_S:
                        print("Assuming 2D domain. Automatically duplicating the weights to match the dimension of the D columns \n")
                        self.weights = np.concatenate((weights, weights))
                else:
                        raise AttributeError("Make sure the size of the weight array is twice smaller than the size of D")
                
                if isinstance(data, np.ndarray):
                        # Apply the weights only if D exist.
                        # If not (i.e. N_partitions >1), weights are applied in _k_matrix.py when loading partitions of D
                        self.Dstar = np.transpose(np.transpose(self.D) * np.sqrt(self.weights))
                else:
                        self.Dstar = None
                        
    def compute(
        self,
        kind: str,
        **engine_kwargs
        ) -> tuple:
        """
        Unified entry point for all decompositions: POD, SPOD, kPOD, DMD, DFT.
        Any engine‐specific parameters (e.g. F_S, L_B, gamma…) can be passed here
        and will be forwarded to the chosen engine’s constructor.
        """
        engine_cls = self._engines.get(kind.lower())
        if engine_cls is None:
            raise ValueError(f"Unknown decomposition '{kind}'")

        # pick the right data array
        D_use = self.Dstar  # or self.D if you want un-weighted

        engine = engine_cls(
            D=D_use,
            folder_out=self.FOLDER_OUT,
            save_k=self.SAVE_K,
            memory_saving=self.MEMORY_SAVING,
            n_partitions=self.N_PARTITIONS,
            **engine_kwargs
        )
        return engine.run()
                        