use std::fmt::Display;

use robot_behavior::RobotException;
use serde_repr::{Deserialize_repr, Serialize_repr};

#[derive(Default, Debug, Serialize_repr, Deserialize_repr, PartialEq)]
#[repr(u16)]
pub enum RobotError {
    #[default]
    NoError,
    NoNameError,

    RECOnMoving = 20004,

    ControllerNotInit = 40000,
    RECParametersError = 40034,
    RECCmdFormatError = 40056,

    IoError = 65535,
}

impl Display for RobotError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RobotError::NoError => write!(f, "No error"),
            RobotError::NoNameError => write!(f, "No name error"),
            RobotError::RECOnMoving => write!(f, "REC on moving"),
            RobotError::ControllerNotInit => write!(f, "Controller not init"),
            RobotError::RECParametersError => write!(f, "REC parameters error"),
            RobotError::RECCmdFormatError => write!(f, "REC cmd format error"),
            RobotError::IoError => write!(f, "Io error"),
        }
    }
}

impl From<RobotError> for RobotException {
    fn from(e: RobotError) -> Self {
        RobotException::UnprocessableInstructionError(e.to_string())
    }
}
