import numpy

from ._dtype import DType


class Backend:

    def __init__(self, name):
        self._name = name

    def __enter__(self):
        from . import _DEFAULT
        _DEFAULT.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import _DEFAULT
        _DEFAULT.pop(-1)

    @property
    def name(self):
        return self._name

    @property
    def precision(self):
        """Short for math.backend.get_precision()"""
        from . import get_precision
        return get_precision()

    @property
    def float_type(self):
        return DType(float, self.precision)

    @property
    def complex_type(self):
        return DType(complex, max(64, self.precision))

    def combine_types(self, *dtypes: DType):
        # all bool?
        if all(dt.kind == bool for dt in dtypes):
            return dtypes[0]
        # all int / bool?
        if all(dt.kind in (bool, int) for dt in dtypes):
            largest = max(dtypes, key=lambda dt: dt.bits)
            return largest
        # all real?
        if all(dt.kind in (float, int, bool) for dt in dtypes):
            return self.float_type
        # complex
        if all(dt.kind in (complex, float, int, bool) for dt in dtypes):
            return self.complex_type
        raise ValueError(dtypes)

    def auto_cast(self, *tensors):
        """
        Determins the appropriate values type resulting from operations involving the tensors as input.
        
        This method is called by the default implementations of basic operators.
        Backends can override this method to prevent unnecessary casting.

        Args:
          *tensors: 

        Returns:

        """
        dtypes = [self.dtype(t) for t in tensors]
        result_type = self.combine_types(*dtypes)
        tensors = [self.cast(t, result_type) for t in tensors]
        return tensors

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def matches_name(self, name):
        return self.name.lower() == name.lower()

    # --- Abstract math functions ---

    def is_tensor(self, x, only_native=False):
        """
        An object is considered a native tensor by a backend if no internal conversion is required by backend methods.
        An object is considered a tensor (nativer or otherwise) by a backend if it is not a struct (e.g. tuple, list) and all methods of the backend accept it as a tensor argument.

        Args:
          x: object to check
          only_native: If True, only accepts true native tensor representations, not Python numbers or others that are also supported as tensors (Default value = False)

        Returns:
          bool: whether `x` is considered a tensor by this backend

        """
        raise NotImplementedError()

    def as_tensor(self, x, convert_external=True):
        """
        Converts a tensor-like object to the native tensor representation of this backend.
        If x is a native tensor of this backend, it is returned without modification.
        If x is a Python number (numbers.Number instance), `convert_numbers` decides whether to convert it unless the backend cannot handle Python numbers.
        
        *Note:* There may be objects that are considered tensors by this backend but are not native and thus, will be converted by this method.

        Args:
          x: tensor-like, e.g. list, tuple, Python number, tensor
          convert_external: if False and `x` is a Python number that is understood by this backend, this method returns the number as is. This can help prevent type clashes like int32 vs int64. (Default value = True)

        Returns:
          tensor representation of `x`

        """
        raise NotImplementedError()

    def is_available(self, tensor) -> bool:
        """
        Tests if the value of the tensor is known and can be read at this point.
        If true, `numpy(tensor)` must return a valid NumPy representation of the value.
        
        Tensors are typically available when the backend operates in eager mode.

        Args:
          tensor: backend-compatible tensor

        Returns:
          bool

        """
        raise NotImplementedError()

    def numpy(self, tensor) -> numpy.ndarray:
        """
        Returns a NumPy representation of the given tensor.
        If `tensor` is already a NumPy array, it is returned without modification.
        
        This method raises an error if the value of the tensor is not known at this point, e.g. because it represents a node in a graph.
        Use `is_available(tensor)` to check if the value can be represented as a NumPy array.

        Args:
          tensor: backend-compatible tensor

        Returns:
          NumPy representation of the values stored in the tensor

        """
        raise NotImplementedError()

    def copy(self, tensor, only_mutable=False):
        raise NotImplementedError()

    def transpose(self, tensor, axes):
        raise NotImplementedError()

    def equal(self, x, y):
        raise NotImplementedError()

    def random_uniform(self, shape):
        raise NotImplementedError(self)

    def random_normal(self, shape):
        raise NotImplementedError(self)

    def stack(self, values, axis=0):
        raise NotImplementedError(self)

    def concat(self, values, axis):
        raise NotImplementedError(self)

    def pad(self, value, pad_width, mode: str = 'constant', constant_values=0):
        """
        Pad a tensor with values as specified by `mode` and `constant_values`.
        
        If the mode is not supported, returns NotImplemented.

        Args:
          value: tensor
          pad_width: 2D tensor specifying the number of values padded to the edges of each axis in the form [[axis 0 lower, axis 0 upper], ...] including batch and component axes.
          mode: constant', 'boundary', 'periodic', 'symmetric', 'reflect'
          constant_values: used for out-of-bounds points if mode='constant' (Default value = 0)
          mode: str:  (Default value = 'constant')

        Returns:
          padded tensor or NotImplemented

        """
        raise NotImplementedError(self)

    def reshape(self, value, shape):
        raise NotImplementedError(self)

    def flip(self, value, axes: tuple or list):
        slices = [slice(None, None, -1 if i in axes else None) for i in range(self.ndims(value))]
        return value[slices]

    def sum(self, value, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def prod(self, value, axis=None):
        raise NotImplementedError(self)

    def divide_no_nan(self, x, y):
        """
        Computes x/y but returns 0 if y=0.

        Args:
          x: 
          y: 

        Returns:

        """
        raise NotImplementedError(self)

    def where(self, condition, x=None, y=None):
        raise NotImplementedError(self)

    def nonzero(self, values):
        """
        

        Args:
          values: 

        Returns:
          

        """
        raise NotImplementedError(self)

    def mean(self, value, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def py_func(self, func, inputs, Tout, shape_out, stateful=True, name=None, grad=None):
        raise NotImplementedError(self)

    def range(self, start, limit=None, delta=1, dtype=None):
        raise NotImplementedError(self)

    def zeros(self, shape, dtype: DType = None):
        raise NotImplementedError(self)

    def zeros_like(self, tensor):
        raise NotImplementedError(self)

    def ones(self, shape, dtype: DType = None):
        raise NotImplementedError(self)

    def ones_like(self, tensor):
        raise NotImplementedError(self)

    def meshgrid(self, *coordinates):
        raise NotImplementedError(self)

    def dot(self, a, b, axes):
        raise NotImplementedError(self)

    def matmul(self, A, b):
        raise NotImplementedError(self)

    def einsum(self, equation, *tensors):
        raise NotImplementedError(self)

    def while_loop(self, cond, body, loop_vars, shape_invariants=None, parallel_iterations=10, back_prop=True,
                   swap_memory=False, name=None, maximum_iterations=None):
        raise NotImplementedError(self)

    def abs(self, x):
        raise NotImplementedError(self)

    def sign(self, x):
        raise NotImplementedError(self)

    def round(self, x):
        raise NotImplementedError(self)

    def ceil(self, x):
        raise NotImplementedError(self)

    def floor(self, x):
        raise NotImplementedError(self)

    def max(self, x, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def min(self, x, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def maximum(self, a, b):
        raise NotImplementedError(self)

    def minimum(self, a, b):
        raise NotImplementedError(self)

    def clip(self, x, minimum, maximum):
        raise NotImplementedError(self)

    def with_custom_gradient(self, function, inputs, gradient, input_index=0, output_index=None, name_base='custom_gradient_func'):
        raise NotImplementedError(self)

    def sqrt(self, x):
        raise NotImplementedError(self)

    def exp(self, x):
        raise NotImplementedError(self)

    def conv(self, tensor, kernel, padding='same'):
        raise NotImplementedError(self)

    def expand_dims(self, a, axis=0, number=1):
        raise NotImplementedError(self)

    def shape(self, tensor):
        raise NotImplementedError(self)

    def staticshape(self, tensor):
        raise NotImplementedError(self)

    def to_float(self, x):
        """
        Converts a tensor to floating point values.
        If this Backend uses a fixed precision, the tensor will be converted to that precision.
        Otherwise, non-float inputs are converted to float32 (unless `float64=True`).
        
        If `x` is mutable and of the correct floating type, returns a copy of `x`.
        
        To convert float tensors to the backend precision but leave non-float tensors untouched, use `Backend.as_tensor()`.

        Args:
          x: tensor

        Returns:

        """
        raise NotImplementedError(self)

    def to_int(self, x, int64=False):
        raise NotImplementedError(self)

    def to_complex(self, x):
        raise NotImplementedError(self)

    def dimrange(self, tensor):
        return range(1, len(tensor.shape) - 1)

    def gather(self, values, indices):
        raise NotImplementedError(self)

    def gather_nd(self, values, indices, batch_dims=0):
        raise NotImplementedError(self)

    def flatten(self, x):
        return self.reshape(x, (-1,))

    def std(self, x, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def boolean_mask(self, x, mask):
        raise NotImplementedError(self)

    def isfinite(self, x):
        raise NotImplementedError(self)

    def scatter(self, indices, values, shape, duplicates_handling='undefined', outside_handling='undefined'):
        """
        This method expects the first dimension of indices and values to be the batch dimension.
        The batch dimension need not be specified in the indices array.

        Args:
          indices: n-dimensional indices corresponding to values
          values: values to scatter at indices
          shape: spatial shape of the result tensor, 1D int array
          duplicates_handling: one of ('undefined', 'add', 'mean', 'any') (Default value = 'undefined')
          outside_handling: one of ('discard', 'clamp', 'undefined') (Default value = 'undefined')

        Returns:

        """
        raise NotImplementedError(self)

    def any(self, boolean_tensor, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def all(self, boolean_tensor, axis=None, keepdims=False):
        raise NotImplementedError(self)

    def fft(self, x):
        """
        Computes the n-dimensional FFT along all but the first and last dimensions.

        Args:
          x: tensor of dimension 3 or higher

        Returns:

        """
        raise NotImplementedError(self)

    def ifft(self, k):
        """
        Computes the n-dimensional inverse FFT along all but the first and last dimensions.

        Args:
          k: tensor of dimension 3 or higher

        Returns:

        """
        raise NotImplementedError(self)

    def imag(self, complex):
        raise NotImplementedError(self)

    def real(self, complex):
        raise NotImplementedError(self)

    def cast(self, x, dtype: DType):
        raise NotImplementedError(self)

    def sin(self, x):
        raise NotImplementedError(self)

    def cos(self, x):
        raise NotImplementedError(self)

    def dtype(self, array) -> DType:
        raise NotImplementedError(self)

    def tile(self, value, multiples):
        """
        Repeats the tensor along each axis the number of times given by multiples.
        If `multiples` has more dimensions than `value`, these dimensions are added to `value` as outer dimensions.

        Args:
          value: tensor
          multiples: tuple or list of integers

        Returns:
          tile tensor

        """
        raise NotImplementedError(self)

    def sparse_tensor(self, indices, values, shape):
        """
        

        Args:
          indices: tuple/list matching the dimensions (pair for matrix)
          values: param shape:
          shape: 

        Returns:

        """
        raise NotImplementedError(self)

    def coordinates(self, tensor, unstack_coordinates=False):
        """
        Returns the coordinates and values of a tensor.
        
        The first returned value is a tensor holding the coordinate vectors in the last dimension if unstack_coordinates=False.
        In case unstack_coordinates=True, the coordiantes are returned as a tuple of tensors, i.e. (row, col) for matrices

        Args:
          tensor: dense or sparse tensor
          unstack_coordinates:  (Default value = False)

        Returns:
          indices (tensor or tuple), values

        """
        raise NotImplementedError(self)

    def conjugate_gradient(self, A, y, x0, relative_tolerance: float = 1e-5, absolute_tolerance: float = 0.0, max_iterations: int = 1000, gradient: str = 'implicit', callback=None):
        """
        Solve the system of linear equations
          A * x = y

        Args:
          A: batch of sparse / dense matrices or or linear function A(x). 3rd order tensor or list of matrices.
          y: target result of A * x. 2nd order tensor (batch, vector) or list of vectors.
          x0: initial guess for x. 2nd order tensor (batch, vector) or list of vectors.
          relative_tolerance: stops when norm(residual) <= max(relative_tolerance * norm(y), absolute_tolerance)
          absolute_tolerance: stops when norm(residual) <= max(relative_tolerance * norm(y), absolute_tolerance)
          max_iterations: maximum number of iterations or None for unlimited
          gradient: one of ('implicit', 'inverse', 'autodiff')
          callback: Function to call after each iteration. It is called with the current solution as callback(x). (Default value = None)
          relative_tolerance: float:  (Default value = 1e-5)
          absolute_tolerance: float:  (Default value = 0.0)
          max_iterations: int:  (Default value = 1000)
          gradient: str:  (Default value = 'implicit')

        Returns:
          converged, solution, iterations

        """
        raise NotImplementedError(self)

    # --- Math function with default implementation ---

    def resample(self, inputs, sample_coords, interpolation='linear', boundary='constant', constant_values=0):
        """
        Interpolates a regular grid at the specified coordinates.

        Args:
          inputs: grid values
          sample_coords: tensor of floating grid indices. The last dimension must match the dimensions of inputs. The first grid point of dimension i lies at position 0, the last at values.shape[i]-1.
          interpolation: only 'linear' is currently supported (Default value = 'linear')
          boundary: values to use for coordinates outside the grid, can be specified for each face, options are 'constant', 'boundary', 'periodic', 'symmetric', 'reflect' (Default value = 'constant')
          constant_values: Value used for constant boundaries, can be specified for each face (Default value = 0)

        Returns:

        """
        return NotImplemented

    def ndims(self, tensor):
        return len(self.staticshape(tensor))

    def size(self, array):
        return self.prod(self.shape(array))

    def batch_gather(self, tensor, batches):
        if isinstance(batches, int):
            batches = [batches]
        return tensor[batches, ...]

    def unstack(self, tensor, axis=0, keepdims=False):
        if axis < 0:
            axis += len(tensor.shape)
        if axis >= len(tensor.shape) or axis < 0:
            raise ValueError("Illegal axis value")
        result = []
        for slice_idx in range(tensor.shape[axis]):
            if keepdims:
                component = tensor[tuple([slice(slice_idx, slice_idx + 1) if d == axis else slice(None) for d in range(len(tensor.shape))])]
            else:
                component = tensor[tuple([slice_idx if d == axis else slice(None) for d in range(len(tensor.shape))])]
            result.append(component)
        return tuple(result)

    def add(self, a, b):
        a, b = self.auto_cast(a, b)
        return a + b

    def sub(self, a, b):
        a, b = self.auto_cast(a, b)
        return a - b

    def mul(self, a, b):
        a, b = self.auto_cast(a, b)
        return a * b

    def div(self, numerator, denominator):
        numerator, denominator = self.auto_cast(numerator, denominator)
        return numerator / denominator

    def pow(self, base, exp):
        base, exp = self.auto_cast(base, exp)
        return base ** exp

    def mod(self, dividend, divisor):
        dividend, divisor = self.auto_cast(dividend, divisor)
        return dividend % divisor