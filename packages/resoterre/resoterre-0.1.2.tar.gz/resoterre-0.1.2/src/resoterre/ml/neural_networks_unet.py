"""UNet architecture implementation with configurable parameters."""

from dataclasses import dataclass, field

import torch
from torch import nn

from resoterre.ml.neural_networks_basic import Conv2d, SEBlock


default_relu_init = "kaiming_uniform_"
default_relu_kwargs = {"nonlinearity": "relu"}


@dataclass(frozen=True, slots=True)
class UNetConfig:
    """
    Configuration for the UNet architecture.

    Attributes
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    depth : int, default=3
        Depth of the UNet, i.e., number of downsampling operations.
    initial_nb_of_hidden_channels : int, default=64
        Number of initial hidden channels.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    resolution_increase_layers : int, default=0
        Number of additional resolution increase layers at the end of the UNet.
    reduction_ratio : int | None, default=None
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    in_channels: int
    out_channels: int
    depth: int = field(metadata={"is_hyperparameter": True, "immutable": True})
    initial_nb_of_hidden_channels: int = field(
        metadata={"is_hyperparameter": True, "immutable": True, "display_name": "init chan"}
    )
    kernel_size: int = 3
    resolution_increase_layers: int = 0
    reduction_ratio: int | None = field(
        default=None, metadata={"is_hyperparameter": True, "immutable": True, "display_name": "reduction ratio"}
    )


@dataclass(frozen=True, slots=True)
class DenseUNetConfig:
    """
    Configuration for the UNet architecture.

    Attributes
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    depth : int, default=3
        Depth of the UNet, i.e., number of downsampling operations.
    out_additional_channels : int, default=16
        Additional output channels for each dense convolution layer.
    num_layers : int, default=2
        Number of dense convolution layers in the block.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    resolution_increase_layers : int, default=0
        Number of additional resolution increase layers at the end of the UNet.
    reduction_ratio : int | None, default=None
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    in_channels: int
    out_channels: int
    depth: int = field(metadata={"is_hyperparameter": True, "immutable": True})
    out_additional_channels: int = field(
        metadata={"is_hyperparameter": True, "immutable": True, "display_name": "add chan"}
    )
    num_layers: int = field(metadata={"is_hyperparameter": True, "immutable": True, "display_name": "num layers"})
    kernel_size: int = 3
    resolution_increase_layers: int = 0
    reduction_ratio: int | None = field(
        default=None, metadata={"is_hyperparameter": True, "immutable": True, "display_name": "reduction ratio"}
    )


class DenseConvolution(nn.Module):  # type: ignore[misc]
    """
    Dense Convolution Layer with Batch Normalization and ReLU activation.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_additional_channels : int
        Number of additional output channels to be concatenated with the input.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    """

    def __init__(self, in_channels: int, out_additional_channels: int, kernel_size: int = 3) -> None:
        super().__init__()
        if (kernel_size % 2) != 1:
            raise ValueError("Only odd kernel sizes are supported.")
        self.sequential_block = nn.Sequential(
            nn.BatchNorm2d(in_channels),
            nn.ReLU(inplace=True),
            Conv2d(
                init_weight_fn_name=default_relu_init,
                init_weight_fn_kwargs=default_relu_kwargs,
                in_channels=in_channels,
                out_channels=out_additional_channels,
                kernel_size=kernel_size,
                padding=(kernel_size - 1) // 2,
                bias=False,
            ),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the dense convolution layer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, in_channels + out_additional_channels, height, width).
        """
        return torch.cat([x, self.sequential_block(x)], dim=1)  # Concatenate along the channel dimension


class DoubleConvolution(nn.Module):  # type: ignore[misc]
    """
    Double Convolution Layer with Batch Normalization and ReLU activation.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    """

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3) -> None:
        super().__init__()
        if (kernel_size % 2) != 1:
            raise ValueError("Only odd kernel sizes are supported.")
        self.sequential_block = nn.Sequential(
            Conv2d(
                init_weight_fn_name=default_relu_init,
                init_weight_fn_kwargs=default_relu_kwargs,
                in_channels=in_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                padding=(kernel_size - 1) // 2,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            Conv2d(
                init_weight_fn_name=default_relu_init,
                init_weight_fn_kwargs=default_relu_kwargs,
                in_channels=out_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                padding=(kernel_size - 1) // 2,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the double convolution layer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, out_channels, height, width).
        """
        return self.sequential_block(x)


class DenseConvolutionBlock(nn.Module):  # type: ignore[misc]
    """
    Block of multiple Dense Convolution Layers.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_additional_channels : int
        Number of additional output channels for each dense convolution layer.
    num_layers : int
        Number of dense convolution layers in the block.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    multiple_of_additional_channels : bool, default=False
        If True, the first dense convolution layer will output (out_additional_channels - in_channels)
        additional channels to ensure the total output channels is a multiple of out_additional_channels.
    """

    def __init__(
        self,
        in_channels: int,
        out_additional_channels: int,
        num_layers: int,
        kernel_size: int = 3,
        multiple_of_additional_channels: bool = False,
    ) -> None:
        super().__init__()
        sequential_args = []
        current_num_channels = in_channels
        for i in range(num_layers):
            if i == 0 and multiple_of_additional_channels:
                local_out_additional_channels = out_additional_channels - in_channels
            else:
                local_out_additional_channels = out_additional_channels
            sequential_args.append(DenseConvolution(current_num_channels, local_out_additional_channels, kernel_size))
            current_num_channels += local_out_additional_channels
        self.sequential = nn.Sequential(*sequential_args)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the dense convolution block.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor.
        """
        return self.sequential(x)


class MaxPoolingAndDoubleConvolution(nn.Module):  # type: ignore[misc]
    """
    Max Pooling followed by a Double Convolution Layer.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    def __init__(
        self, in_channels: int, out_channels: int, kernel_size: int = 3, reduction_ratio: int | None = None
    ) -> None:
        super().__init__()
        sequential_args = [nn.MaxPool2d(2), DoubleConvolution(in_channels, out_channels, kernel_size)]
        if reduction_ratio is not None:
            sequential_args.append(SEBlock(out_channels, reduction_ratio=reduction_ratio))
        self.sequential_block = nn.Sequential(*sequential_args)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Max Pooling and Double Convolution layer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, out_channels, height // 2, width // 2).
        """
        return self.sequential_block(x)


class MaxPoolingAndDenseConvolutionBlock(nn.Module):  # type: ignore[misc]
    """
    Max Pooling followed by a Dense Convolution Block.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_additional_channels : int
        Number of additional output channels for each dense convolution layer.
    num_layers : int
        Number of dense convolution layers in the block.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    def __init__(
        self,
        in_channels: int,
        out_additional_channels: int,
        num_layers: int,
        kernel_size: int = 3,
        reduction_ratio: int | None = None,
    ) -> None:
        super().__init__()
        sequential_args = [
            nn.MaxPool2d(2),
            DenseConvolutionBlock(in_channels, out_additional_channels, num_layers, kernel_size=kernel_size),
        ]
        if reduction_ratio is not None:
            sequential_args.append(
                SEBlock(in_channels + num_layers * out_additional_channels, reduction_ratio=reduction_ratio)
            )
        self.sequential = nn.Sequential(*sequential_args)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Max Pooling and Dense Convolution block.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor.
        """
        return self.sequential(x)


class MaxPoolingTo1x1(nn.Module):  # type: ignore[misc]
    """
    Max Pooling to reduce the input to 1x1 spatial dimensions.

    Parameters
    ----------
    h_in : int
        Height of the input tensor.
    w_in : int
        Width of the input tensor.
    """

    def __init__(self, h_in: int, w_in: int) -> None:
        super().__init__()
        self.max_pooling = nn.MaxPool2d((h_in, w_in), 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Max Pooling layer to reduce the input to 1x1.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, in_channels, 1, 1).
        """
        return self.max_pooling(x)


class ConvolutionTransposeAndDoubleConvolution(nn.Module):  # type: ignore[misc]
    """
    Convolution Transpose followed by a Double Convolution Layer.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    concat : bool, default=True
        If True, concatenates the skip connection with the transposed convolution output.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    def __init__(
        self, in_channels: int, out_channels: int, concat: bool = True, reduction_ratio: int | None = None
    ) -> None:
        super().__init__()
        self.concat = concat
        self.convolution_transpose = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
        if self.concat:
            post_transpose_channels = in_channels
        else:
            post_transpose_channels = in_channels // 2

        sequential_args = [DoubleConvolution(post_transpose_channels, out_channels)]
        if reduction_ratio is not None:
            sequential_args.append(SEBlock(out_channels, reduction_ratio=reduction_ratio))
        self.sequential_block = nn.Sequential(*sequential_args)

    def forward(self, x: torch.Tensor, skip_connection: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Convolution Transpose and Double Convolution layer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).
        skip_connection : torch.Tensor
            Skip connection tensor of shape (batch_size, in_channels, height // 2, width // 2).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, out_channels, height * 2, width * 2).
        """
        x1 = self.convolution_transpose(x)
        if self.concat:
            x2 = torch.cat([skip_connection, x1], dim=1)
        else:
            x2 = x1
        return self.sequential_block(x2)


class ConvolutionTransposeAndDenseConvolutionBlock(nn.Module):  # type: ignore[misc]
    """
    Convolution Transpose followed by a Dense Convolution Block.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_additional_channels : int
        Number of additional output channels for each dense convolution layer.
    num_layers : int
        Number of dense convolution layers in the block.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    concat_size : int, default=0
        If greater than 0, concatenates the skip connection with the transposed convolution output.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.
    """

    def __init__(
        self,
        in_channels: int,
        out_additional_channels: int,
        num_layers: int,
        kernel_size: int = 3,
        concat_size: int = 0,
        reduction_ratio: int | None = None,
    ) -> None:
        super().__init__()
        self.concat_size = concat_size
        self.convolution_transpose = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
        post_transpose_channels = in_channels // 2 + concat_size

        sequential_args = [
            DenseConvolutionBlock(post_transpose_channels, out_additional_channels, num_layers, kernel_size=kernel_size)
        ]
        if reduction_ratio is not None:
            sequential_args.append(
                SEBlock(post_transpose_channels + num_layers * out_additional_channels, reduction_ratio=reduction_ratio)
            )
        self.sequential_block = nn.Sequential(*sequential_args)

    def forward(self, x: torch.Tensor, skip_connection: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Convolution Transpose and Dense Convolution block.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).
        skip_connection : torch.Tensor, optional
            Skip connection tensor of shape (batch_size, concat_size, height // 2, width // 2).
            Required if concat_size > 0.

        Returns
        -------
        torch.Tensor
            Output tensor.
        """
        x1 = self.convolution_transpose(x)
        if self.concat_size > 0:
            x2 = torch.cat([skip_connection, x1], dim=1)
        else:
            x2 = x1
        return self.sequential_block(x2)


class ConvolutionTransposeOutOf1x1(nn.Module):  # type: ignore[misc]
    """
    Convolution Transpose to output from a 1x1 layer.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    h_out : int
        Height of the output tensor.
    w_out : int
        Width of the output tensor.
    """

    def __init__(self, in_channels: int, out_channels: int, h_out: int, w_out: int) -> None:
        # h_out and w_out are used to get out of a 1x1 layer at the bottom
        super().__init__()
        self.convolution_transpose = nn.ConvTranspose2d(in_channels, out_channels, kernel_size=(h_out, w_out))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Convolution Transpose layer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, 1, 1).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, out_channels, h_out, w_out).
        """
        return self.convolution_transpose(x)


class UNetBase(nn.Module):  # type: ignore[misc]
    """Base class for UNet architectures."""

    def forward(self, x: torch.Tensor, x_linear: torch.Tensor | None = None) -> torch.Tensor:
        """
        Forward pass through the UNet architecture.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, in_channels, height, width).
        x_linear : torch.Tensor, optional
            Linear input tensor of shape (batch_size, linear_size). Required if `go_to_1x1` is True.

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, out_channels, height_out, width_out).
        """
        downward_layers = [self.initial_operation(x)]
        for downward_operation in self.downward_operations:
            downward_layers.append(downward_operation(downward_layers[-1]))
        if x_linear is not None:
            if (self.to_1x1_operation is None) or (self.out_of_1x1_operation is None):
                raise ValueError("x_linear can only be provided if go_to_1x1 is True.")
            x = self.to_1x1_operation(downward_layers[-1])
            x_linear = x_linear.unsqueeze(-1).unsqueeze(-1)
            x = torch.cat([x, x_linear], dim=1)
            x = self.out_of_1x1_operation(x)
        else:
            x = downward_layers[-1]
        for i, upward_operation in enumerate(self.upward_operations):
            if i < self.depth:
                x = upward_operation(x, downward_layers[-2 - i])
            else:
                x = upward_operation(x, None)
        x = self.last_operation(x)
        return x


class UNet(UNetBase, nn.Module):  # type: ignore[misc]
    """
    UNet architecture with configurable parameters.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    initial_nb_of_hidden_channels : int, default=64
        Number of initial hidden channels.
    depth : int, default=3
        Depth of the UNet, i.e., number of downsampling operations.
    resolution_increase_layers : int, default=0
        Number of additional resolution increase layers at the end of the UNet.
    go_to_1x1 : bool, default=False
        If True, the UNet will go to a 1x1 layer at the bottom.
    h_in : int, optional
        Height of the input tensor. Required if `go_to_1x1` is True.
    w_in : int, optional
        Width of the input tensor. Required if `go_to_1x1` is True.
    linear_size : int, optional
        Size of the linear input tensor. Required if `go_to_1x1` is True.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.

    References
    ----------
    .. [1] Ronneberger, O., et al. (2015). U-Net: Convolutional Networks for Biomedical Image Segmentation
       arXiv:1505.04597
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        initial_nb_of_hidden_channels: int = 64,
        depth: int = 3,
        resolution_increase_layers: int = 0,
        go_to_1x1: bool = False,
        h_in: int | None = None,
        w_in: int | None = None,
        linear_size: int | None = None,
        reduction_ratio: int | None = None,
    ) -> None:
        super().__init__()
        if go_to_1x1:
            if (h_in is None) or (w_in is None) or (linear_size is None):
                raise ValueError("h_in, w_in, and linear_size must be provided if go_to_1x1 is True.")
            for _ in range(depth):
                if h_in % 2 != 0 or w_in % 2 != 0:
                    raise ValueError("h_in and h_out must be divisible by 2 up to the depth of the UNET.")
                h_in //= 2
                w_in //= 2
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        hidden_channels = initial_nb_of_hidden_channels
        self.depth = depth
        self.resolution_increase_layers = resolution_increase_layers

        self.initial_operation = DoubleConvolution(in_channels, hidden_channels)

        self.downward_operations = nn.ModuleList()
        for _ in range(self.depth):
            self.downward_operations.append(
                MaxPoolingAndDoubleConvolution(
                    hidden_channels, hidden_channels * 2, kernel_size=kernel_size, reduction_ratio=reduction_ratio
                )
            )
            hidden_channels *= 2

        self.to_1x1_operation = None
        self.out_of_1x1_operation = None
        if go_to_1x1:
            if (h_in is None) or (w_in is None) or (linear_size is None):
                raise ValueError("h_in, w_in, and linear_size must be provided if go_to_1x1 is True.")
            self.to_1x1_operation = MaxPoolingTo1x1(h_in, w_in)
            self.out_of_1x1_operation = ConvolutionTransposeOutOf1x1(
                hidden_channels + linear_size, hidden_channels, h_out=h_in, w_out=w_in
            )

        self.upward_operations = nn.ModuleList()
        for i in range(self.depth + self.resolution_increase_layers):
            if i < self.depth:
                concat = True
            else:
                concat = False
            self.upward_operations.append(
                ConvolutionTransposeAndDoubleConvolution(
                    hidden_channels, hidden_channels // 2, concat=concat, reduction_ratio=reduction_ratio
                )
            )
            hidden_channels = hidden_channels // 2

        self.last_operation = nn.Conv2d(hidden_channels, out_channels, kernel_size=kernel_size, padding=1)


class DenseUNet(UNetBase, nn.Module):  # type: ignore[misc]
    """
    UNet architecture with configurable parameters.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    out_additional_channels : int, default=16
        Number of additional output channels for each dense convolution layer.
    num_layers : int, default=2
        Number of dense convolution layers in the block.
    kernel_size : int, default=3
        Size of the convolution kernel. Must be an odd number.
    depth : int, default=3
        Depth of the UNet, i.e., number of downsampling operations.
    resolution_increase_layers : int, default=0
        Number of additional resolution increase layers at the end of the UNet.
    go_to_1x1 : bool, default=False
        If True, the UNet will go to a 1x1 layer at the bottom.
    h_in : int, optional
        Height of the input tensor. Required if `go_to_1x1` is True.
    w_in : int, optional
        Width of the input tensor. Required if `go_to_1x1` is True.
    linear_size : int, optional
        Size of the linear input tensor. Required if `go_to_1x1` is True.
    reduction_ratio : int, optional
        Reduction ratio for the Squeeze and Excitation block. If None, no SE block is added.

    References
    ----------
    .. [1] Huang, G., et al. (2016). Densely Connected Convolutional Networks.
       arXiv:1608.06993
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        out_additional_channels: int = 16,
        num_layers: int = 2,
        kernel_size: int = 3,
        depth: int = 3,
        resolution_increase_layers: int = 0,
        go_to_1x1: bool = False,
        h_in: int | None = None,
        w_in: int | None = None,
        linear_size: int | None = None,
        reduction_ratio: int | None = None,
    ) -> None:
        super().__init__()
        if go_to_1x1:
            if (h_in is None) or (w_in is None) or (linear_size is None):
                raise ValueError("h_in, w_in, and linear_size must be provided if go_to_1x1 is True.")
            for _ in range(depth):
                if h_in % 2 != 0 or w_in % 2 != 0:
                    raise ValueError("h_in and h_out must be divisible by 2 up to the depth of the UNET.")
                h_in //= 2
                w_in //= 2
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.depth = depth
        self.resolution_increase_layers = resolution_increase_layers
        self.channel_tracker = []

        if out_additional_channels <= in_channels:
            raise ValueError("out_additional_channels must be larger than in_channels.")
        out_additional_channels_check = out_additional_channels
        for _ in range(depth):
            if out_additional_channels_check % 2 != 0:
                raise ValueError("out_additional_channels must be a multiple of 2 up to depth.")
            out_additional_channels_check //= 2
        self.initial_operation = DenseConvolutionBlock(
            in_channels,
            out_additional_channels,
            num_layers,
            kernel_size=kernel_size,
            multiple_of_additional_channels=True,
        )
        self.channel_tracker.append(num_layers * out_additional_channels)

        self.downward_operations = nn.ModuleList()
        for _ in range(self.depth):
            self.downward_operations.append(
                MaxPoolingAndDenseConvolutionBlock(
                    self.channel_tracker[-1],
                    out_additional_channels=out_additional_channels,
                    num_layers=num_layers,
                    kernel_size=kernel_size,
                    reduction_ratio=reduction_ratio,
                )
            )
            self.channel_tracker.append(self.channel_tracker[-1] + num_layers * out_additional_channels)

        self.to_1x1_operation = None
        self.out_of_1x1_operation = None
        if go_to_1x1:
            if (h_in is None) or (w_in is None) or (linear_size is None):
                raise ValueError("h_in, w_in, and linear_size must be provided if go_to_1x1 is True.")
            self.to_1x1_operation = MaxPoolingTo1x1(h_in, w_in)
            self.out_of_1x1_operation = ConvolutionTransposeOutOf1x1(
                self.channel_tracker[-1] + linear_size, self.channel_tracker[-1], h_out=h_in, w_out=w_in
            )

        self.upward_operations = nn.ModuleList()
        for i in range(self.depth + self.resolution_increase_layers):
            if i < self.depth:
                concat = True
            else:
                concat = False
            concat_size = self.channel_tracker[-2 * (i + 1)] if concat else 0
            self.upward_operations.append(
                ConvolutionTransposeAndDenseConvolutionBlock(
                    self.channel_tracker[-1],
                    out_additional_channels=out_additional_channels,
                    num_layers=num_layers,
                    concat_size=concat_size,
                    reduction_ratio=reduction_ratio,
                )
            )
            self.channel_tracker.append(
                self.channel_tracker[-1] // 2 + concat_size + num_layers * out_additional_channels
            )

        self.last_operation = nn.Conv2d(self.channel_tracker[-1], out_channels, kernel_size=kernel_size, padding=1)
