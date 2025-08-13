import unittest

import numpy as np

import depth_tools
from depth_tools._logging_internal import LOGGER

from .testutil import TestBase


class TestObjectInsertion(TestBase):
    def setUp(self) -> None:
        self.px_idx = (60, 13)

        self.depth_map = np.full((1, 30, 80), 10, dtype=np.float32)
        self.depth_map[0, self.px_idx[1], self.px_idx[0]] = 4
        self.depth_mask = np.full((1, 30, 80), False)
        self.depth_mask[0, self.px_idx[1], self.px_idx[0]] = True
        self.model_scale_local = (2, 3, 4)
        self.model_x_vs = (0, 0, 5)
        self.model_x_vs_norm = (0, 0, 1)
        self.model_y_vs = (9, 0, 0)
        self.model_y_vs_norm = (1, 0, 0)
        self.cam_params = depth_tools.CameraIntrinsics(f_x=50, f_y=50, c_x=15, c_y=40)

    def test_depth_px_and_model_coords_2_mvm__happy_path(self) -> None:
        depth_value = self.depth_map[0, self.px_idx[1], self.px_idx[0]]
        im_height = self.depth_map.shape[-2]
        depth_map_point = self.cam_params.get_intrinsic_mat_inv() @ np.array(
            [
                [depth_value * self.px_idx[0]],
                [depth_value * (im_height - self.px_idx[1])],
                [depth_value],
            ],
            dtype=np.float32,
        )

        with self.assertNoLogs():
            mvm = depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        model_point = np.array([[1], [2], [3]], dtype=np.float32)

        actual_projected_point = mvm @ np.concatenate([model_point, [[1]]], axis=0)

        model_point_scaled = np.array(
            [
                [1 * self.model_scale_local[0]],
                [2 * self.model_scale_local[1]],
                [3 * self.model_scale_local[2]],
            ],
            dtype=np.float32,
        )
        coord_sys_conv_mat = depth_tools.get_coord_sys_conv_mat(
            from_=depth_tools.CoordSys.RH_ZUp, to=depth_tools.CoordSys.LH_YUp
        )
        model_point_lh_yup = coord_sys_conv_mat @ model_point_scaled

        model_x_vs_norm = np.array([[0], [0], [1]], dtype=np.float32)
        model_y_vs_norm = np.array([[1], [0], [0]], dtype=np.float32)
        model_z_vs_norm = np.array([[0], [1], [0]], dtype=np.float32)
        model_point_rotated: np.ndarray = (
            model_x_vs_norm * model_point_lh_yup[0, 0]
            + model_y_vs_norm * model_point_lh_yup[1, 0]
            + model_z_vs_norm * model_point_lh_yup[2, 0]
        )

        model_point_translated = model_point_rotated.copy()
        model_point_translated[0, 0] += depth_map_point[0, 0]
        model_point_translated[1, 0] += depth_map_point[1, 0]
        model_point_translated[2, 0] += depth_map_point[2, 0]

        expected_projected_point = np.concatenate(
            [model_point_translated, [[1]]], axis=0
        )

        self.assertAllclose(expected_projected_point, actual_projected_point)

    def test_depth_px_and_model_coords_2_mvm__non_orthogonal_axes(self) -> None:
        with self.assertLogs(level="WARN", logger=LOGGER):
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_x_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

    def test_depth_px_and_model_coords_2_mvm__almost_zero_x(self) -> None:
        with self.assertLogs(level="WARN", logger=LOGGER):
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=(1e-16, 0, 0),
                model_y_vs=(0, 1, 0),
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

    def test_depth_px_and_model_coords_2_mvm__almost_zero_y(self) -> None:
        with self.assertLogs(level="WARN", logger=LOGGER):
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=(1, 0, 0),
                model_y_vs=(0, 1e-16, 0),
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

    def test_depth_px_and_model_coords_2_mvm__invalid_depth_map_shape(self) -> None:
        invalid_depth_map = np.expand_dims(self.depth_map, axis=0)
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=invalid_depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        msg = str(cm.exception)
        self.assertIn("depth map does not have format Im_Depth", msg)
        self.assertIn(str(tuple(invalid_depth_map.shape)), msg)

    def test_depth_px_and_model_coords_2_mvm__invalid_depth_map_dtype(self) -> None:
        invalid_depth_map = self.depth_map.astype(np.int32)
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=invalid_depth_map,
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        msg = str(cm.exception)
        self.assertIn("depth map does not have format Im_Depth", msg)
        self.assertIn(str(invalid_depth_map.dtype), msg)

    def test_depth_px_and_model_coords_2_mvm__invalid_depth_mask_shape(self) -> None:
        invalid_depth_mask = np.expand_dims(self.depth_mask, axis=0)
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=invalid_depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        msg = str(cm.exception)
        self.assertIn("depth mask does not have format Im_Mask", msg)
        self.assertIn(str(tuple(invalid_depth_mask.shape)), msg)

    def test_depth_px_and_model_coords_2_mvm__invalid_depth_mask_dtype(self) -> None:
        invalid_depth_mask = self.depth_mask.astype(np.int32)
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map,
                depth_mask=invalid_depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        msg = str(cm.exception)
        self.assertIn("depth mask does not have format Im_Mask", msg)
        self.assertIn(str(invalid_depth_mask.dtype), msg)

    def test_depth_px_and_model_coords_2_mvm__inconsistent_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_px_and_model_coords_2_mvm(
                depth_map=self.depth_map.transpose([0, 2, 1]),
                depth_mask=self.depth_mask,
                cam_params=self.cam_params,
                model_scale_local=self.model_scale_local,
                model_x_vs=self.model_x_vs,
                model_y_vs=self.model_y_vs,
                px_idx=self.px_idx,
                model_coord_sys=depth_tools.CoordSys.RH_ZUp,
            )

        msg = str(cm.exception)
        self.assertIn("and the depth mask are different. Shape", msg)

    def test_depth_px_and_model_coords_2_mvm__oob_px(self) -> None:
        subtests = [
            ((-1, 0), "X", "invalid x"),
            ((0, -1), "Y", "invalid y"),
            ((1000000, 0), "X", "invalid x"),
            ((0, 1000000), "Y", "invalid y"),
        ]
        for px_idx, invalid_axis_name, subtest_name in subtests:
            with self.subTest(subtest_name):
                with self.assertRaises(ValueError) as cm:
                    depth_tools.depth_px_and_model_coords_2_mvm(
                        depth_map=self.depth_map.transpose([0, 2, 1]),
                        depth_mask=self.depth_mask,
                        cam_params=self.cam_params,
                        model_scale_local=self.model_scale_local,
                        model_x_vs=self.model_x_vs,
                        model_y_vs=self.model_y_vs,
                        px_idx=px_idx,
                        model_coord_sys=depth_tools.CoordSys.RH_ZUp,
                    )

                    msg = str(cm.exception)

                    self.assertIn(
                        f"pixel is out of bounds for the {invalid_axis_name} axis", msg
                    )
