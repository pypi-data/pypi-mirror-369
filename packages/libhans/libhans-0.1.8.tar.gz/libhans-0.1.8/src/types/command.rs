use robot_behavior::{RobotResult, deserialize_error};
use serde::{Deserialize, Serialize};
use std::marker::ConstParamTy;

use super::command_serde::CommandSerde;
use crate::robot_error::RobotError;

#[derive(ConstParamTy, PartialEq, Eq, Serialize, Deserialize, Debug)]
pub enum Command {
    // ! 初始化指令
    OSCmd,
    ConnectToBox,
    Electrify,
    BlackOut,
    StartMaster,
    CloseMaster,
    IsSimulation,
    ReadControllerState,
    ReadRobotModel,
    // ! 轴组控制指令
    GrpEnable,
    GrpDisable,
    GrpReset,
    GrpStop,
    GrpInterrupt,
    GrpContinue,
    GrpCloseFreeDriver,
    GrpOpenFreeDriver,
    // ! 脚本控制指令
    // ! 电箱控制指令
    ReadBoxInfo,
    ReadBoxCI,
    ReadBoxDI,
    ReadBoxCO,
    ReadBoxDO,
    ReadBoxAI,
    ReadBoxAO,
    SetBoxCO,
    SetBoxDO,
    SetBoxAOMode,
    SetBoxAO,
    SetEndDO,
    ReadEI,
    ReadEO,
    ReadEAI,
    // ! 状态读取与设置指令
    SetOverride,
    SetToolMotion,
    SetPayload,
    SetJointMaxVel,
    SetJointMaxAcc,
    SetLinearMaxVel,
    SetLinearMaxAcc,
    ReadJointMaxVel,
    ReadJointMaxAcc,
    ReadJointMaxJerk,
    ReadLinearMaxVel,
    ReadEmergencyInfo,
    ReadRobotState,
    ReadAxisErrorCode,
    ReadCurFSM,
    // ! 位置、速度、电流读取指令
    ReadCmdPos,
    ReadActPos,
    ReadCmdJointVel,
    ReadActJointVel,
    ReadCmdTcpVel,
    ReadActTcpVel,
    ReadCmdJointCur,
    ReadActJointCur,
    ReadTcpVelocity,
    // ! 坐标转换计算指令
    // TODO 验证坐标转换计算函数
    // ! 工具坐标与用户坐标读写指令
    SetCurTCP,
    SetCurUCS,
    ReadCurTCP,
    ReadCurUCS,
    // ! 力控控制指令
    SetForceControlState,
    ReadFTControlState,
    SetForceToolCoordinateMotion,
    GrpFCInterrupt,
    GrpFCContinue,
    SetForceZero,
    HRSetMaxSearchVelocities,
    HRSetForceControlStrategy,
    SetFTPosition,
    HRSetPIDControlParams,
    HRSetMassParams,
    HRSetDampParams,
    HRSetStiffParams,
    HRSetControlGoal,
    SetForceFreeDriveMode,
    ReadFTCabData,
    // ! 通用运动类控制指令
    MoveRelJ,
    MoveRelL,
    WayPointRel,
    WayPointEx,
    WayPoint,
    WayPoint2,
    MoveJ,
    MoveL,
    MoveC,
    // ! 连续轨迹运动类控制指令
    StartPushMovePath,
    PushMovePathJ,
    EndPushMovePath,
    MovePath,
    ReadMovePathState,
    UpdateMovePathName,
    DelMovePath,
    ReadSoftMotionProcess,
    InitMovePathL,
    PushMovePathL,
    PushMovePaths,
    MovePathL,
    SetMovePathOverride,
    // ! Servo运动类控制指令
    StartServo,
    PushServoJ,
    PushServoP,
    // ! 相对跟踪运动类控制指令
    // ! 其他指令
}

#[derive(Debug, PartialEq, Default)]
pub struct CommandHander<const C: Command> {}

#[derive(Debug, PartialEq)]
pub struct CommandRequest<const C: Command, D> {
    _handler: CommandHander<C>,
    pub data: D,
}

#[derive(Debug, PartialEq)]
pub struct CommandResponse<const C: Command, S> {
    _handler: CommandHander<C>,
    pub status: Result<S, RobotError>,
}

impl<const C: Command> CommandSerde for CommandHander<C> {
    fn to_string(&self) -> String {
        format!("{C:?}")
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        if data == format!("{C:?}") {
            Ok(CommandHander {})
        } else {
            Err(deserialize_error::<CommandHander<C>, _>(data)(()))
        }
    }
    fn try_default() -> Self {
        CommandHander {}
    }
    fn num_args() -> usize {
        0
    }
}

impl<const C: Command, D: 'static> CommandSerde for CommandRequest<C, D>
where
    D: CommandSerde,
{
    fn to_string(&self) -> String {
        if std::any::TypeId::of::<D>() == std::any::TypeId::of::<()>() {
            format!("{C:?},;")
        } else {
            format!("{:?},{},;", C, self.data.to_string())
        }
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        let command = format!("{C:?}");
        if data.starts_with(&command) {
            let data = D::from_str(&data[command.len()..data.len() - 2])?;
            Ok(CommandRequest {
                _handler: CommandHander {},
                data,
            })
        } else {
            Err(deserialize_error::<CommandRequest<C, D>, _>(data)(()))
        }
    }
    fn try_default() -> Self {
        CommandRequest {
            _handler: CommandHander {},
            data: D::try_default(),
        }
    }
    fn num_args() -> usize {
        D::num_args()
    }
}

impl<const C: Command, S> CommandSerde for CommandResponse<C, S>
where
    S: CommandSerde,
{
    fn to_string(&self) -> String {
        format!("{:?},{},;", C, self.status.as_ref().unwrap().to_string())
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        let command = format!("{C:?}");
        if data.starts_with(&(command.clone() + ",OK,")) {
            let data = &data[&command.len() + 3..data.len() - 2];
            let data = S::from_str(if data.is_empty() { "" } else { &data[1..] })?;
            Ok(CommandResponse {
                _handler: CommandHander {},
                status: Ok(data),
            })
        } else if data.starts_with(&(command.clone() + ",Fail,")) {
            let data = &data[&command.len() + 5..data.len() - 2];
            let data = RobotError::from_str(if data.is_empty() { "" } else { &data[1..] })?;
            Ok(CommandResponse {
                _handler: CommandHander {},
                status: Err(data),
            })
        } else {
            println!("data: {data:?}");
            Err(deserialize_error::<CommandResponse<C, S>, _>(data)(()))
        }
    }
    fn try_default() -> Self {
        CommandResponse {
            _handler: CommandHander {},
            status: Ok(S::try_default()),
        }
    }
    fn num_args() -> usize {
        S::num_args()
    }
}

impl<const C: Command, D> From<D> for CommandRequest<C, D> {
    fn from(data: D) -> Self {
        CommandRequest {
            _handler: CommandHander {},
            data,
        }
    }
}

impl<const C: Command, S> From<Result<S, RobotError>> for CommandResponse<C, S> {
    fn from(status: Result<S, RobotError>) -> Self {
        CommandResponse {
            _handler: CommandHander {},
            status,
        }
    }
}

impl<const C: Command, D: Default> Default for CommandRequest<C, D> {
    fn default() -> Self {
        CommandRequest {
            _handler: CommandHander {},
            data: D::default(),
        }
    }
}

impl<const C: Command, S: Default> Default for CommandResponse<C, S> {
    fn default() -> Self {
        CommandResponse {
            _handler: CommandHander {},
            status: Ok(S::default()),
        }
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_command_serde() {
        let request = CommandRequest::<{ Command::GrpEnable }, ()> {
            _handler: CommandHander {},
            data: (),
        };
        let request_str = "GrpEnable,;";
        assert_eq!(request.to_string(), request_str);
        assert_eq!(
            CommandRequest::<{ Command::GrpEnable }, ()>::from_str(request_str).unwrap(),
            request
        );
    }
}
