use super::command::{Command, CommandRequest, CommandResponse};

pub type SetCurTCPRequest = CommandRequest<{ Command::SetCurTCP }, (u8, [f64; 6])>;
pub type SetCurUCSRequest = CommandRequest<{ Command::SetCurUCS }, (u8, [f64; 6])>;
pub type ReadCurTCPRequest = CommandRequest<{ Command::ReadCurTCP }, u8>;
pub type ReadCurUCSRequest = CommandRequest<{ Command::ReadCurUCS }, u8>;

pub type SetCurTCPResponse = CommandResponse<{ Command::SetCurTCP }, ()>;
pub type SetCurUCSResponse = CommandResponse<{ Command::SetCurUCS }, ()>;
pub type ReadCurTCPResponse = CommandResponse<{ Command::ReadCurTCP }, [f64; 6]>;
pub type ReadCurUCSResponse = CommandResponse<{ Command::ReadCurUCS }, [f64; 6]>;
