use robot_behavior::{RobotException, RobotResult};

use super::command::{Command, CommandRequest, CommandResponse};
use super::command_serde::CommandSerde;
use crate::RobotMode;
use crate::robot_error::RobotError;
use crate::robot_param::HANS_DOF;

pub type SetOverrideRequest = CommandRequest<{ Command::SetOverride }, (u8, f64)>;
pub type SetToolMotionRequest = CommandRequest<{ Command::SetToolMotion }, (u8, bool)>;
pub type SetPayloadRequest = CommandRequest<{ Command::SetPayload }, (u8, Load)>;
pub type SetJointMaxVelRequest = CommandRequest<{ Command::SetJointMaxVel }, (u8, [f64; HANS_DOF])>;
pub type SetJointMaxAccRequest = CommandRequest<{ Command::SetJointMaxAcc }, (u8, [f64; HANS_DOF])>;
pub type SetLinearMaxVelRequest = CommandRequest<{ Command::SetLinearMaxVel }, (u8, f64)>;
pub type SetLinearMaxAccRequest = CommandRequest<{ Command::SetLinearMaxAcc }, (u8, f64)>;
pub type ReadJointMaxVelRequest = CommandRequest<{ Command::ReadJointMaxVel }, u8>;
pub type ReadJointMaxAccRequest = CommandRequest<{ Command::ReadJointMaxAcc }, u8>;
pub type ReadJointMaxJerkRequest = CommandRequest<{ Command::ReadJointMaxJerk }, u8>;
pub type ReadLinearMaxVelRequest = CommandRequest<{ Command::ReadLinearMaxVel }, u8>;
pub type ReadEmergencyInfoRequest = CommandRequest<{ Command::ReadEmergencyInfo }, u8>;
pub type ReadRobotStateRequest = CommandRequest<{ Command::ReadRobotState }, u8>;
pub type ReadAxisErrorCodeRequest = CommandRequest<{ Command::ReadAxisErrorCode }, u8>;
pub type ReadCurFSMRequest = CommandRequest<{ Command::ReadCurFSM }, u8>;
pub type ReadCmdPosRequest = CommandRequest<{ Command::ReadCmdPos }, u8>;
pub type ReadActPosRequest = CommandRequest<{ Command::ReadActPos }, u8>;
pub type ReadCmdJointVelRequest = CommandRequest<{ Command::ReadCmdJointVel }, u8>;
pub type ReadActJointVelRequest = CommandRequest<{ Command::ReadActJointVel }, u8>;
pub type ReadCmdTcpVelRequest = CommandRequest<{ Command::ReadCmdTcpVel }, u8>;
pub type ReadActTcpVelRequest = CommandRequest<{ Command::ReadActTcpVel }, u8>;
pub type ReadCmdJointCurRequest = CommandRequest<{ Command::ReadCmdJointCur }, u8>;
pub type ReadActJointCurRequest = CommandRequest<{ Command::ReadActJointCur }, u8>;
pub type ReadTcpVelocityRequest = CommandRequest<{ Command::ReadTcpVelocity }, u8>;

pub type SetOverrideResponse = CommandResponse<{ Command::SetOverride }, ()>;
pub type SetToolMotionResponse = CommandResponse<{ Command::SetToolMotion }, ()>;
pub type SetPayloadResponse = CommandResponse<{ Command::SetPayload }, ()>;
pub type SetJointMaxVelResponse = CommandResponse<{ Command::SetJointMaxVel }, ()>;
pub type SetJointMaxAccResponse = CommandResponse<{ Command::SetJointMaxAcc }, ()>;
pub type SetLinearMaxVelResponse = CommandResponse<{ Command::SetLinearMaxVel }, ()>;
pub type SetLinearMaxAccResponse = CommandResponse<{ Command::SetLinearMaxAcc }, ()>;
pub type ReadJointMaxVelResponse = CommandResponse<{ Command::ReadJointMaxVel }, [f64; HANS_DOF]>;
pub type ReadJointMaxAccResponse = CommandResponse<{ Command::ReadJointMaxAcc }, [f64; HANS_DOF]>;
pub type ReadJointMaxJerkResponse = CommandResponse<{ Command::ReadJointMaxJerk }, [f64; HANS_DOF]>;
pub type ReadLinearMaxVelResponse = CommandResponse<{ Command::ReadLinearMaxVel }, [f64; HANS_DOF]>;
pub type ReadEmergencyInfoResponse = CommandResponse<{ Command::ReadEmergencyInfo }, EmergencyInfo>;
pub type ReadRobotStateResponse = CommandResponse<{ Command::ReadRobotState }, RobotFlag>;
pub type ReadAxisErrorCodeResponse =
    CommandResponse<{ Command::ReadAxisErrorCode }, [u16; HANS_DOF]>;
pub type ReadCurFSMResponse = CommandResponse<{ Command::ReadCurFSM }, RobotMode>;
pub type ReadCmdPosResponse = CommandResponse<{ Command::ReadCmdPos }, CmdPose>;
pub type ReadActPosResponse = CommandResponse<{ Command::ReadActPos }, ActPose>;
pub type ReadCmdJointVelResponse = CommandResponse<{ Command::ReadCmdJointVel }, [f64; HANS_DOF]>;
pub type ReadActJointVelResponse = CommandResponse<{ Command::ReadActJointVel }, [f64; HANS_DOF]>;
pub type ReadCmdTcpVelResponse = CommandResponse<{ Command::ReadCmdTcpVel }, [f64; 6]>;
pub type ReadActTcpVelResponse = CommandResponse<{ Command::ReadActTcpVel }, [f64; 6]>;
pub type ReadCmdJointCurResponse = CommandResponse<{ Command::ReadCmdJointCur }, [f64; HANS_DOF]>;
pub type ReadActJointCurResponse = CommandResponse<{ Command::ReadActJointCur }, [f64; HANS_DOF]>;
pub type ReadTcpVelocityResponse = CommandResponse<{ Command::ReadTcpVelocity }, (f64, f64)>;

#[derive(Default, libhans_derive::CommandSerde, Debug, PartialEq)]
pub struct Load {
    pub mass: f64,
    pub centroid: [f64; 3],
}

#[derive(Default, libhans_derive::CommandSerde, Debug, PartialEq)]
pub struct EmergencyInfo {
    pub is_estop: bool,
    pub esto_code: u8,
    pub is_safety_guard: bool,
    pub safety_guard_code: u8,
}

#[derive(Default, libhans_derive::CommandSerde, Debug, PartialEq)]
pub struct RobotFlag {
    pub is_move: bool,
    pub is_enable: bool,
    pub is_error: bool,
    pub error_code: u8,
    pub error_id: u8,
    pub is_breaking: bool,
    pub is_emergency_stop: bool,
    pub is_safety_guard: bool,
    pub is_power_on: bool,
    pub is_connect_to_box: bool,
    pub is_move_waypoint: bool,
    pub is_arrived: bool,
}

#[derive(Default, libhans_derive::CommandSerde, Debug, PartialEq)]
pub struct ActPose {
    pub joint: [f64; HANS_DOF],
    pub pose_o_to_ee: [f64; 6],
    pub pose_f_to_ee: [f64; 6],
    pub pose_u_to_ee: [f64; 6],
}

#[derive(Default, libhans_derive::CommandSerde, Debug, PartialEq)]
pub struct CmdPose {
    joint: [f64; HANS_DOF],
    pose_o_to_ee: [f64; 6],
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_serde() {
        let load = Load::default();
        let load_str = "0,0,0,0";
        assert_eq!(load.to_string(), load_str);
        assert_eq!(Load::from_str(load_str).unwrap(), load);
    }

    #[test]
    fn test_emergency_info_serde() {
        let emergency_info = EmergencyInfo::default();
        let emergency_info_str = "0,0,0,0";
        assert_eq!(emergency_info.to_string(), emergency_info_str);
        assert_eq!(
            EmergencyInfo::from_str(emergency_info_str).unwrap(),
            emergency_info
        );
    }

    #[test]
    fn test_robot_flag_serde() {
        let robot_flag = RobotFlag::default();
        let robot_flag_str = "0,0,0,0,0,0,0,0,0,0,0,0";
        assert_eq!(robot_flag.to_string(), robot_flag_str);
        assert_eq!(RobotFlag::from_str(robot_flag_str).unwrap(), robot_flag);
    }

    #[test]
    fn test_act_pose_serde() {
        let act_pose = ActPose::default();
        let act_pose_str = ["0"; 24].join(",");
        assert_eq!(act_pose.to_string(), act_pose_str);
        assert_eq!(ActPose::from_str(&act_pose_str).unwrap(), act_pose);
    }

    #[test]
    fn test_cmd_pose_serde() {
        let cmd_pose = CmdPose::default();
        let cmd_pose_str = ["0"; 12].join(",");
        assert_eq!(cmd_pose.to_string(), cmd_pose_str);
        assert_eq!(CmdPose::from_str(&cmd_pose_str).unwrap(), cmd_pose);
    }
}
