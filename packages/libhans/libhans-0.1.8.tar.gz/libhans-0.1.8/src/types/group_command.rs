use super::command::{Command, CommandRequest, CommandResponse};

pub type GrpEnableRequest = CommandRequest<{ Command::GrpEnable }, u8>;
pub type GrpDisableRequest = CommandRequest<{ Command::GrpDisable }, u8>;
pub type GrpResetRequest = CommandRequest<{ Command::GrpReset }, u8>;
pub type GrpStopRequest = CommandRequest<{ Command::GrpStop }, u8>;
pub type GrpInterruptRequest = CommandRequest<{ Command::GrpInterrupt }, u8>;
pub type GrpContinueRequest = CommandRequest<{ Command::GrpContinue }, u8>;
pub type GrpCloseFreeDriverRequest = CommandRequest<{ Command::GrpCloseFreeDriver }, u8>;
pub type GrpOpenFreeDriverRequest = CommandRequest<{ Command::GrpOpenFreeDriver }, u8>;

pub type GrpEnableResponse = CommandResponse<{ Command::GrpEnable }, ()>;
pub type GrpDisableResponse = CommandResponse<{ Command::GrpDisable }, ()>;
pub type GrpResetResponse = CommandResponse<{ Command::GrpReset }, ()>;
pub type GrpStopResponse = CommandResponse<{ Command::GrpStop }, ()>;
pub type GrpInterruptResponse = CommandResponse<{ Command::GrpInterrupt }, ()>;
pub type GrpContinueResponse = CommandResponse<{ Command::GrpContinue }, ()>;
pub type GrpCloseFreeDriverResponse = CommandResponse<{ Command::GrpCloseFreeDriver }, ()>;
pub type GrpOpenFreeDriverResponse = CommandResponse<{ Command::GrpOpenFreeDriver }, ()>;
