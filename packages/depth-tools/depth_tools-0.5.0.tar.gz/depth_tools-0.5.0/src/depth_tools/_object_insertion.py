import numpy as np

from ._camera import CameraIntrinsics
from ._coord_sys import CoordSys, get_coord_sys_conv_mat
from ._format_checks_internal import is_bool_array, is_floating_array
from ._logging_internal import LOGGER


def depth_px_and_model_coords_2_mvm(
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    px_idx: tuple[int, int],
    cam_params: CameraIntrinsics,
    model_x_vs: tuple[float, float, float],
    model_y_vs: tuple[float, float, float],
    model_coord_sys: CoordSys,
    model_scale_local: tuple[float, float, float] = (1, 1, 1),
    verify_args: bool = True,
) -> np.ndarray:
    """
    Calculate the model->view matrix for a model to insert into an RGBD image.

    This function warns the user if ``model_x_vs`` or ``model_y_vs`` are not orthogonal or any of them is 0.

    The function calculates the view-space Z-axis of the model using the following rule: ``z_norm = cross(x_norm, y_norm)``

    Parameters
    ----------
    depth_map
        The depth map. Format: ``Im_Depth``
    depth_mask
        The depth mask. Format: ``Im_Mask``
    px_idx
        The *index* of the pixel to which the ``(0, 0, 0)`` point of the model goes. Unlike many other functions of this package, this function *does not* support negative indices due to their ambiguity in this context.
    model_x_vs
        The local X axis of the model in the view space. Note that this function does not make any assumptions about the coordinate system of the model. However, the view space is assumed to use an Y-up left-handed coordinate system. The vector does not have to be normalized, this function normalizes it before further processing.
    model_y_vs
        The local Y axis of the model in the view space. Note that this function does not make any assumptions about the coordinate system of the model. However, the view space is assumed to use an Y-up left-handed coordinate system. The vector does not have to be normalized, this function normalizes it before further processing. The vector should be orthogonal to ``model_x_vs``.
    model_coord_sys
        The coordinate system of the model.
    model_scale_local
        The scale of the model alongside its local X, Y and Z axes (*before* the coordinate system conversion).
    verify_args
        If true, then the function verifies its arguments. Otherwise the usage of incorrect arguments yields undefined behavior.

    Returns
    -------
    v
        The model->view matrix. Format: ``Matrix_4x4``

    Raises
    ------
    ValueError
        If any of the arrays containing the depth map and the depth mask have incorrect format and the arguments are checked.

        If the shape of the depth map and the array containing the depth mask is different and the arguments are checked.

        If the index of the pixel is out of bounds (note that negative indices are not supported) and the arguments are checked.

    """
    if verify_args:
        _verfiy_depth_px_req(depth_map=depth_map, depth_mask=depth_mask, px_idx=px_idx)

    model_x_vs_norm = _normalize_vector(model_x_vs)
    model_y_vs_norm = _normalize_vector(model_y_vs)

    if abs(np.dot(model_x_vs_norm, model_y_vs_norm)) > 1e-5:
        LOGGER.warning(
            "The X and Y coordinates of the model in the view space are not orthogonal."
        )

    model_z_vs_norm = np.cross(model_x_vs_norm, model_y_vs_norm)

    depth_value = depth_map[0, px_idx[1], px_idx[0]]
    px_x = px_idx[0]
    px_y = depth_map.shape[1] - px_idx[1]

    mat_inv = cam_params.get_intrinsic_mat_inv().astype(depth_map.dtype)

    point_vs = mat_inv @ np.array(
        [[px_x * depth_value], [px_y * depth_value], [depth_value]],
        dtype=depth_map.dtype,
    )

    rotation_transform = np.stack(
        [model_x_vs_norm, model_y_vs_norm, model_z_vs_norm], axis=1
    )
    rotation_transform = np.concat([rotation_transform, [[0, 0, 0]]], axis=0)
    rotation_transform = np.concat([rotation_transform, [[0], [0], [0], [1]]], axis=1)

    translation_transform = np.concat(
        [np.eye(3, dtype=depth_map.dtype), point_vs], axis=1
    )
    translation_transform = np.concat(
        [translation_transform, np.array([[0, 0, 0, 1]], dtype=depth_map.dtype)], axis=0
    )

    coord_sys_conv_mat = get_coord_sys_conv_mat(
        from_=model_coord_sys, to=CoordSys.LH_YUp
    )
    coord_sys_conv_mat = np.concat([coord_sys_conv_mat, [[0, 0, 0]]], axis=0)
    coord_sys_conv_mat = np.concat([coord_sys_conv_mat, [[0], [0], [0], [1]]], axis=1)

    scale_transform = np.diag(
        [model_scale_local[0], model_scale_local[1], model_scale_local[2], 1]
    ).astype(depth_map.dtype)

    return (
        translation_transform
        @ rotation_transform
        @ coord_sys_conv_mat
        @ scale_transform
    )


def _normalize_vector(vec: tuple[float, float, float]) -> np.ndarray:
    """
    Normalize the given vector.

    Parameters
    ----------
    vec
        The vector specified by an ``(x, y, z)`` tuple.

    Returns
    -------
    v
        The normalized vector. Format: floating point, shape: ``(3,)``, values: ``[x, y, z]``
    """
    vec_arr = np.array(vec)
    vec_len = np.linalg.norm(vec, ord=2)

    if vec_len < 1e-10:
        LOGGER.warning(
            f"The length of the vector {vec} for a transformed axis is almost 0."
        )

    return vec_arr / vec_len


def _verfiy_depth_px_req(
    depth_map: np.ndarray, depth_mask: np.ndarray, px_idx: tuple[int, int]
) -> None:
    """
    Raises
    ------
    ValueError
        If any of the arrays containing the depth map and the depth mask have incorrect format.

        If the shape of the depth map and the array containing the depth mask is different.

        If the index of the pixel is out of bounds (note that negative indices are not supported).
    """
    if len(depth_map.shape) != 3:
        raise ValueError(
            f"The depth map does not have format Im_Depth. Its shape is not 3-dimensional. Shape: {tuple(depth_map.shape)}"
        )

    if depth_map.shape[0] != 1:
        raise ValueError(
            f"The depth map does not have format Im_Depth. Its number of channels is not equal to 1. Shape: {tuple(depth_map.shape)}"
        )
    if not is_floating_array(depth_map):
        raise ValueError(
            f"The depth map does not have format Im_Depth. It is not a floating point array. Dtype: {depth_map.dtype}"
        )

    if len(depth_mask.shape) != 3:
        raise ValueError(
            f"The depth mask does not have format Im_Mask. Its shape is not 3-dimensional. Shape: {tuple(depth_mask.shape)}"
        )

    if depth_mask.shape[0] != 1:
        raise ValueError(
            f"The depth mask does not have format Im_Mask. Its number of channels is not equal to 1. Shape: {tuple(depth_mask.shape)}"
        )
    if not is_bool_array(depth_mask):
        raise ValueError(
            f"The depth mask does not have format Im_Mask. It is not a floating point array. Dtype: {depth_mask.dtype}"
        )

    if depth_map.shape != depth_mask.shape:
        raise ValueError(
            f"The shapes of the depth map and the depth mask are different. Shape of the depth map: {tuple(depth_map.shape)}; shape of the depth mask: {tuple(depth_mask.shape)}"
        )

    depth_map_width = depth_map.shape[-1]
    depth_map_height = depth_map.shape[-2]

    if not (0 <= px_idx[0] < depth_map_width):
        raise ValueError(
            f"The index of the pixel is out of bounds for the X axis. Image width: {depth_map_width}. Note that this function does not support negative pixel indices due to their ambiguity."
        )
    if not (0 <= px_idx[1] < depth_map_height):
        raise ValueError(
            f"The index of the pixel is out of bounds for the Y axis. Image width: {depth_map_width}. Note that this function does not support negative pixel indices due to their ambiguity."
        )

    if not depth_mask[0, px_idx[1], px_idx[0]]:
        raise ValueError(f"There is no specified depth at the given pixel ({px_idx}).")
