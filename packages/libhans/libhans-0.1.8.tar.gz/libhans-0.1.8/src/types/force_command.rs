use super::command::{Command, CommandRequest, CommandResponse};

pub type SetForceControlStateRequest =
    CommandRequest<{ Command::SetForceControlState }, (u8, bool)>;
pub type ReadFTControlStateRequest = CommandRequest<{ Command::ReadFTControlState }, u8>;
pub type SetForceToolCoordinateMotionRequest =
    CommandRequest<{ Command::SetForceToolCoordinateMotion }, (u8, bool)>;
pub type GrpFCInterruptRequest = CommandRequest<{ Command::GrpFCInterrupt }, u8>;
pub type GrpFCContinueRequest = CommandRequest<{ Command::GrpFCContinue }, u8>;
pub type SetForceZeroRequest = CommandRequest<{ Command::SetForceZero }, u8>;
pub type HRSetMaxSearchVelocitiesRequest =
    CommandRequest<{ Command::HRSetMaxSearchVelocities }, (u8, f64, f64)>;
pub type HRSetForceControlStrategyRequest =
    CommandRequest<{ Command::HRSetForceControlStrategy }, (u8, u8)>;
pub type SetFTPositionRequest = CommandRequest<{ Command::SetFTPosition }, (u8, [f64; 6])>;
pub type HRSetPIDControlParamsRequest =
    CommandRequest<{ Command::HRSetPIDControlParams }, (u8, [f64; 6])>;
pub type HRSetMassParamsRequest = CommandRequest<{ Command::HRSetMassParams }, (u8, [f64; 6])>;
pub type HRSetDampParamsRequest = CommandRequest<{ Command::HRSetDampParams }, (u8, [f64; 6])>;
pub type HRSetStiffParamsRequest = CommandRequest<{ Command::HRSetStiffParams }, (u8, [f64; 6])>;
pub type HRSetControlGoalRequest =
    CommandRequest<{ Command::HRSetControlGoal }, (u8, [f64; 6], f64)>;
pub type SetForceFreeDriveModeRequest =
    CommandRequest<{ Command::SetForceFreeDriveMode }, (u8, bool)>;
pub type ReadFTCabDataRequest = CommandRequest<{ Command::ReadFTCabData }, u8>;

pub type SetForceControlStateResponse = CommandResponse<{ Command::SetForceControlState }, ()>;
pub type ReadFTControlStateResponse = CommandResponse<{ Command::ReadFTControlState }, bool>;
pub type SetForceToolCoordinateMotionResponse =
    CommandResponse<{ Command::SetForceToolCoordinateMotion }, ()>;
pub type GrpFCInterruptResponse = CommandResponse<{ Command::GrpFCInterrupt }, ()>;
pub type GrpFCContinueResponse = CommandResponse<{ Command::GrpFCContinue }, ()>;
pub type SetForceZeroResponse = CommandResponse<{ Command::SetForceZero }, ()>;
pub type HRSetMaxSearchVelocitiesResponse =
    CommandResponse<{ Command::HRSetMaxSearchVelocities }, ()>;
pub type HRSetForceControlStrategyResponse =
    CommandResponse<{ Command::HRSetForceControlStrategy }, ()>;
pub type SetFTPositionResponse = CommandResponse<{ Command::SetFTPosition }, ()>;
pub type HRSetPIDControlParamsResponse = CommandResponse<{ Command::HRSetPIDControlParams }, ()>;
pub type HRSetMassParamsResponse = CommandResponse<{ Command::HRSetMassParams }, ()>;
pub type HRSetDampParamsResponse = CommandResponse<{ Command::HRSetDampParams }, ()>;
pub type HRSetStiffParamsResponse = CommandResponse<{ Command::HRSetStiffParams }, ()>;
pub type HRSetControlGoalResponse = CommandResponse<{ Command::HRSetControlGoal }, ()>;
pub type SetForceFreeDriveModeResponse = CommandResponse<{ Command::SetForceFreeDriveMode }, ()>;
pub type ReadFTCabDataResponse = CommandResponse<{ Command::ReadFTCabData }, [f64; 6]>;
