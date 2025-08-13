use super::command::{Command, CommandRequest, CommandResponse};
use super::command_serde::CommandSerde;
use crate::robot_error::RobotError;
use robot_behavior::{RobotException, RobotResult};

pub type ReadBoxInfoRequest = CommandRequest<{ Command::ReadBoxInfo }, u8>;
pub type ReadBoxCIRequest<const N: usize> = CommandRequest<{ Command::ReadBoxCI }, [bool; N]>;
pub type ReadBoxCORequest<const N: usize> = CommandRequest<{ Command::ReadBoxCO }, [bool; N]>;
pub type ReadBoxDIRequest<const N: usize> = CommandRequest<{ Command::ReadBoxDI }, [bool; N]>;
pub type ReadBoxDORequest<const N: usize> = CommandRequest<{ Command::ReadBoxDO }, [bool; N]>;
pub type ReadBoxAIRequest<const N: usize> = CommandRequest<{ Command::ReadBoxAI }, [f64; N]>;
pub type ReadBoxAORequest<const N: usize> = CommandRequest<{ Command::ReadBoxAO }, [f64; N]>;
pub type SetBoxCORequest = CommandRequest<{ Command::SetBoxCO }, (u8, bool)>;
pub type SetBoxDORequest = CommandRequest<{ Command::SetBoxDO }, (u8, bool)>;
pub type SetBoxAOModeRequest = CommandRequest<{ Command::SetBoxAOMode }, (u8, u8)>;
pub type SetBoxAORequest = CommandRequest<{ Command::SetBoxAO }, (u8, f64, u8)>;
pub type SetEndDORequest = CommandRequest<{ Command::SetEndDO }, (u8, u8, bool)>;
pub type ReadEIRequest<const N: usize> = CommandRequest<{ Command::ReadEI }, (u8, [u8; N])>;
pub type ReadEORequest<const N: usize> = CommandRequest<{ Command::ReadEO }, (u8, [u8; N])>;
pub type ReadEAIRequest = CommandRequest<{ Command::ReadEAI }, (u8, u8)>;

pub type ReadBoxInfoResponse = CommandResponse<{ Command::ReadBoxInfo }, BoxInfo>;
pub type ReadBoxCIResponse<const N: usize> = CommandResponse<{ Command::ReadBoxCI }, [bool; N]>;
pub type ReadBoxCOResponse<const N: usize> = CommandResponse<{ Command::ReadBoxCO }, [bool; N]>;
pub type ReadBoxDIResponse<const N: usize> = CommandResponse<{ Command::ReadBoxDI }, [bool; N]>;
pub type ReadBoxDOResponse<const N: usize> = CommandResponse<{ Command::ReadBoxDO }, [bool; N]>;
pub type ReadBoxAIResponse<const N: usize> = CommandResponse<{ Command::ReadBoxAI }, [f64; N]>;
pub type ReadBoxAOResponse<const N: usize> = CommandResponse<{ Command::ReadBoxAO }, [f64; N]>;
pub type SetBoxCOResponse = CommandResponse<{ Command::SetBoxCO }, ()>;
pub type SetBoxDOResponse = CommandResponse<{ Command::SetBoxDO }, ()>;
pub type SetBoxAOModeResponse = CommandResponse<{ Command::SetBoxAOMode }, ()>;
pub type SetBoxAOResponse = CommandResponse<{ Command::SetBoxAO }, ()>;
pub type SetEndDOResponse = CommandResponse<{ Command::SetEndDO }, ()>;
pub type ReadEIResponse<const N: usize> = CommandResponse<{ Command::ReadEI }, [bool; N]>;
pub type ReadEOResponse<const N: usize> = CommandResponse<{ Command::ReadEO }, [bool; N]>;
pub type ReadEAIResponse = CommandResponse<{ Command::ReadEAI }, f64>;

#[derive(Default, libhans_derive::CommandSerde)]
pub struct BoxInfo {
    is_connected: bool,
    is_voltage48v_on: bool,
    voltage48v_out_voltage: f64,
    voltage48v_out_current: f64,
    is_remote_button_on: bool,
    is_three_stage_button_on: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_box_info_serde() {
        let box_info = BoxInfo::default();
        let box_info_str = "0,0,0,0,0,0";
        assert_eq!(box_info.to_string(), box_info_str);
    }
}
