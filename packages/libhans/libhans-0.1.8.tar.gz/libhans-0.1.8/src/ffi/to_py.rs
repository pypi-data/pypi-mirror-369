use pyo3::{PyResult, pyclass, pymethods};
use robot_behavior::{
    behavior::*, py_arm_behavior, py_arm_param, py_arm_preplanned_motion,
    py_arm_preplanned_motion_ext, py_arm_preplanned_motion_impl, py_robot_behavior,
};

use crate::{HANS_DOF, HansRobot};

/// # HansRobot
/// new(ip: str) -> PyHansRobot
#[pyclass(name = "HansRobot")]
pub struct PyHansRobot(HansRobot);

#[pymethods]
impl PyHansRobot {
    #[new]
    fn new(ip: &str) -> Self {
        PyHansRobot(HansRobot::new(ip))
    }

    fn __repr__(&self) -> String {
        "HansRobot".to_string()
    }

    fn connect(&mut self, ip: &str, port: u16) {
        self.0.connect(ip, port)
    }

    fn disconnect(&mut self) {
        self.0.disconnect()
    }

    fn read_joint(&mut self) -> PyResult<[f64; HANS_DOF]> {
        self.0
            .state()
            .map(|s| s.joint.unwrap_or_default())
            .map_err(Into::into)
    }

    fn read_joint_vel(&mut self) -> PyResult<[f64; HANS_DOF]> {
        self.0
            .state()
            .map(|s| s.joint_vel.unwrap_or_default())
            .map_err(Into::into)
    }

    fn read_cartesian_euler(&mut self) -> PyResult<[f64; 6]> {
        self.0
            .state()
            .map(|s| s.pose_o_to_ee.unwrap_or_default().into())
            .map_err(Into::into)
    }

    fn read_cartesian_vel(&mut self) -> PyResult<[f64; 6]> {
        self.0
            .state()
            .map(|s| s.cartesian_vel.unwrap_or_default())
            .map_err(Into::into)
    }
}

py_robot_behavior!(PyHansRobot(HansRobot));
py_arm_behavior!(PyHansRobot<{6}>(HansRobot));
py_arm_param!(PyHansRobot<{6}>(HansRobot));
py_arm_preplanned_motion!(PyHansRobot<{6}>(HansRobot));
py_arm_preplanned_motion_ext!(PyHansRobot<{6}>(HansRobot));
py_arm_preplanned_motion_impl!(PyHansRobot<{6}>(HansRobot));
