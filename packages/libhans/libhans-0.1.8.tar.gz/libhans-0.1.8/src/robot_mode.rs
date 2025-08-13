use serde_repr::{Deserialize_repr, Serialize_repr};

use crate::types::CommandSerde;
use robot_behavior::{RobotResult, deserialize_error};

#[derive(Default, Debug, Serialize_repr, Deserialize_repr, PartialEq, Copy, Clone)]
#[repr(u8)]
pub enum RobotMode {
    #[default]
    UnInitialized,
    Initialized,
    ElectricBoxDisconnect,
    ElectricBoxConnecting,
    EmergencyStopHandling,
    EmergencyStop,
    Blackouting48V,
    Blackout48V,
    Electrifying48V,
    SaftyGuardErrorHandling,
    SaftyGuardError,
    SafetyGuardHandling,
    SaftyGuard,
    ControllerDisconnecting,
    ControllerDisconnect,
    ControllerConnecting,
    ControllerVersionError,
    EtherCATError,
    ControllerChecking,
    Reseting,
    RobotOutofSafeSpace,
    RobotCollisionStop,
    Error,
    RobotEnabling,
    Disable,
    Moving,
    LongJogMoving,
    RobotStopping,
    RobotDisabling,
    RobotOpeningFreeDriver,
    RobotClosingFreeDriver,
    FreeDriver,
    RobotHolding,
    StandBy,
    ScriptRunning,
    ScriptHoldHandling,
    ScriptHolding,
    ScriptStopping,
    ScriptStopped,
    HRAppDisconnected,
    HRAppError,
    RobotLoadIdentify,
    Braking,
}

impl From<u8> for RobotMode {
    fn from(v: u8) -> RobotMode {
        match v {
            0 => RobotMode::UnInitialized,
            1 => RobotMode::Initialized,
            2 => RobotMode::ElectricBoxDisconnect,
            3 => RobotMode::ElectricBoxConnecting,
            4 => RobotMode::EmergencyStopHandling,
            5 => RobotMode::EmergencyStop,
            6 => RobotMode::Blackouting48V,
            7 => RobotMode::Blackout48V,
            8 => RobotMode::Electrifying48V,
            9 => RobotMode::SaftyGuardErrorHandling,
            10 => RobotMode::SaftyGuardError,
            11 => RobotMode::SafetyGuardHandling,
            12 => RobotMode::SaftyGuard,
            13 => RobotMode::ControllerDisconnecting,
            14 => RobotMode::ControllerDisconnect,
            15 => RobotMode::ControllerConnecting,
            16 => RobotMode::ControllerVersionError,
            17 => RobotMode::EtherCATError,
            18 => RobotMode::ControllerChecking,
            19 => RobotMode::Reseting,
            20 => RobotMode::RobotOutofSafeSpace,
            21 => RobotMode::RobotCollisionStop,
            22 => RobotMode::Error,
            23 => RobotMode::RobotEnabling,
            24 => RobotMode::Disable,
            25 => RobotMode::Moving,
            26 => RobotMode::LongJogMoving,
            27 => RobotMode::RobotStopping,
            28 => RobotMode::RobotDisabling,
            29 => RobotMode::RobotOpeningFreeDriver,
            30 => RobotMode::RobotClosingFreeDriver,
            31 => RobotMode::FreeDriver,
            32 => RobotMode::RobotHolding,
            33 => RobotMode::StandBy,
            34 => RobotMode::ScriptRunning,
            35 => RobotMode::ScriptHoldHandling,
            36 => RobotMode::ScriptHolding,
            37 => RobotMode::ScriptStopping,
            38 => RobotMode::ScriptStopped,
            39 => RobotMode::HRAppDisconnected,
            40 => RobotMode::HRAppError,
            41 => RobotMode::RobotLoadIdentify,
            42 => RobotMode::Braking,
            _ => RobotMode::UnInitialized,
        }
    }
}

impl CommandSerde for RobotMode {
    fn to_string(&self) -> String {
        format!("{}", *self as u8)
    }

    fn from_str(data: &str) -> RobotResult<Self> {
        data.parse::<u8>()
            .map_err(deserialize_error::<Self, _>(data))
            .map(RobotMode::from)
    }

    fn try_default() -> Self {
        RobotMode::StandBy
    }
}
