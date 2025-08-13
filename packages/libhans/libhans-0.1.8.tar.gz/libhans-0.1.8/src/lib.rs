#![feature(adt_const_params)]

mod network;
mod robot;
mod robot_error;
mod robot_impl;
mod robot_mode;
mod robot_param;
mod robot_state;
mod types;

#[cfg(feature = "ffi")]
mod ffi;

pub use network::*;
pub use robot::HansRobot;
pub use robot_error::RobotError;
pub use robot_impl::{CommandSubmit, DispatchFn};
pub use robot_mode::RobotMode;
pub use robot_param::*;
pub use types::CommandSerde;

#[cfg(feature = "to_py")]
#[pyo3::pymodule]
mod libhans {
    #[pymodule_export]
    use super::ffi::to_py::PyHansRobot;
    #[pymodule_export]
    use robot_behavior::{LoadState, PyArmState, PyControlType, PyMotionType, PyPose};
}
