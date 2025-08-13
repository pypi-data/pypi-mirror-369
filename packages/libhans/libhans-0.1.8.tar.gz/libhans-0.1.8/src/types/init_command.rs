use super::command::{Command, CommandRequest, CommandResponse};

pub type OSCmdRequest = CommandRequest<{ Command::OSCmd }, u8>;
pub type ConnectToBoxRequest = CommandRequest<{ Command::ConnectToBox }, ()>;
pub type ElectrifyRequest = CommandRequest<{ Command::Electrify }, ()>;
pub type BlackOutRequest = CommandRequest<{ Command::BlackOut }, ()>;
pub type StartMasterRequest = CommandRequest<{ Command::StartMaster }, ()>;
pub type CloseMasterRequest = CommandRequest<{ Command::CloseMaster }, ()>;
pub type IsSimulationRequest = CommandRequest<{ Command::IsSimulation }, ()>;
pub type ReadControllerStateRequest = CommandRequest<{ Command::ReadControllerState }, ()>;
pub type ReadRobotModelRequest = CommandRequest<{ Command::ReadRobotModel }, u8>;

pub type OSCmdResponse = CommandResponse<{ Command::OSCmd }, ()>;
pub type ConnectToBoxResponse = CommandResponse<{ Command::ConnectToBox }, ()>;
pub type ElectrifyResponse = CommandResponse<{ Command::Electrify }, ()>;
pub type BlackOutResponse = CommandResponse<{ Command::BlackOut }, ()>;
pub type StartMasterResponse = CommandResponse<{ Command::StartMaster }, ()>;
pub type CloseMasterResponse = CommandResponse<{ Command::CloseMaster }, ()>;
pub type IsSimulationResponse = CommandResponse<{ Command::IsSimulation }, bool>;
pub type ReadControllerStateResponse = CommandResponse<{ Command::ReadControllerState }, bool>;
pub type ReadRobotModelResponse = CommandResponse<{ Command::ReadRobotModel }, u16>;
