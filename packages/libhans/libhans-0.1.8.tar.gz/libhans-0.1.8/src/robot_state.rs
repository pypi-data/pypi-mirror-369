use serde::{Deserialize, Serialize};
use serde_with::{DisplayFromStr, serde_as};

use crate::{robot_error::RobotError, robot_mode::RobotMode};

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct RobotState {
    /// 位置和速度
    #[serde(rename = "PosAndVel")]
    pos_and_vel: PosAndVel,
    /// 末端IO
    #[serde(rename = "EndIO")]
    end_io: EndIO,
    /// 电箱IO
    #[serde(rename = "ElectricBoxIO")]
    electric_box_io: ElectricBoxIO,
    /// 电箱模拟IO
    #[serde(rename = "ElectricBoxAnalogIO")]
    electric_box_analog_io: ElectricBoxAnalogIO,
    /// 状态和错误
    #[serde(rename = "StateAndError")]
    state_and_error: StateAndError,
    /// 硬件负载
    #[serde(rename = "HardLoad")]
    hard_load: HardLoad,
    /// 力控数据
    #[serde(rename = "FTData")]
    ft_data: FTData,
    /// 脚本
    #[serde(rename = "Script")]
    script: Script,
    /// 插件数据
    #[serde(rename = "pluginsdata")]
    plugins_data: PluginsData,
}

#[serde_as]
#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct PosAndVel {
    /// 关节位置，当前用户坐标和工具坐标下的迪卡尔坐标位置
    #[serde(rename = "Actual_Position")]
    #[serde_as(as = "[DisplayFromStr; 12]")]
    position: [f64; 12],

    /// 当前工具坐标下的迪卡尔坐标位置
    #[serde(rename = "Actual_PCS_TCP")]
    #[serde_as(as = "[DisplayFromStr; 6]")]
    pose_f_to_ee: [f64; 6],

    /// 基于基座坐标系下的迪卡尔坐标位置
    #[serde(rename = "Actual_PCS_Base")]
    #[serde_as(as = "[DisplayFromStr; 6]")]
    pose_o_to_ee: [f64; 6],

    /// 当前实际关节运行时电流，单位[A]
    #[serde(rename = "Actual_Joint_Current")]
    #[serde_as(as = "[DisplayFromStr; 6]")]
    joint_current: [f64; 6],

    /// 实际关节速度，单位[rad/s]
    #[serde(rename = "Actual_Joint_Velocity")]
    #[serde_as(as = "[DisplayFromStr; 6]")]
    joint_velocity: [f64; 6],

    /// 实际关节加速度，单位[rad/s^2]
    #[serde(rename = "Actual_Joint_Acceleration")]
    #[serde_as(as = "[DisplayFromStr; 6]")]
    joint_acceleration: [f64; 6],
}

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct EndIO {
    /// 末端数字输入
    #[serde(rename = "EndDI")]
    digital_input: [u8; 4],
    /// 末端数字输出
    #[serde(rename = "EndDO")]
    digital_output: [u8; 4],
    /// 末端按钮状态
    #[serde(rename = "EndButton")]
    button: [u8; 4],
    /// 末端是否启用按钮
    #[serde(rename = "EnableEndBTN")]
    enable_button: u8,
    /// 末端模拟输入
    #[serde(rename = "EndAI")]
    analog_input: [f64; 2],
}

#[serde_as]
#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct ElectricBoxIO {
    /// 电箱数字输入
    #[serde(rename = "BoxCI")]
    digital_input_c: [u8; 8],
    /// 电箱数字输出
    #[serde(rename = "BoxCO")]
    digital_output_c: [u8; 8],
    /// 电箱数字输入
    #[serde(rename = "BoxDI")]
    digital_input_d: [u8; 8],
    /// 电箱数字输出
    #[serde(rename = "BoxDO")]
    digital_output_d: [u8; 8],
    /// 传送带速度
    #[serde(rename = "Conveyor")]
    #[serde_as(as = "DisplayFromStr")]
    conveyor_speed: f64,
    /// 编码器值
    #[serde(rename = "Encode")]
    encoder: u32,
}

#[serde_as]
#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct ElectricBoxAnalogIO {
    /// 模拟输出1模式
    #[serde(rename = "BoxAnalogOutMode_1")]
    analog_output_mode_1: u8,
    /// 模拟输出2模式
    #[serde(rename = "BoxAnalogOutMode_2")]
    analog_output_mode_2: u8,
    /// 模拟输出1
    #[serde(rename = "BoxAnalogOut_1")]
    #[serde_as(as = "DisplayFromStr")]
    analog_output_1: f64,
    /// 模拟输出2
    #[serde(rename = "BoxAnalogOut_2")]
    #[serde_as(as = "DisplayFromStr")]
    analog_output_2: f64,
    /// 模拟输入1
    #[serde(rename = "BoxAnalogIn_1")]
    #[serde_as(as = "DisplayFromStr")]
    analog_input_1: f64,
    /// 模拟输入2
    #[serde(rename = "BoxAnalogIn_2")]
    #[serde_as(as = "DisplayFromStr")]
    analog_input_2: f64,
}

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct StateAndError {
    /// 机器人状态
    #[serde(rename = "robotState")]
    state: RobotMode,
    /// 机器人是否使能
    #[serde(rename = "robotEnabled")]
    enabled: u8,
    /// 机器人是否暂停
    #[serde(rename = "robotPaused")]
    paused: u8,
    /// 机器人是否运动中
    #[serde(rename = "robotMoving")]
    moving: u8,
    /// 机器人是否平滑过渡完成
    #[serde(rename = "robotBlendingDone")]
    blending_done: u8,
    /// 是否到达目标位置
    #[serde(rename = "InPos")]
    in_position: u8,
    /// 错误轴ID
    #[serde(rename = "Error_AxisID")]
    error_axis_id: u8,
    /// 错误代码
    #[serde(rename = "Error_Code")]
    error_code: RobotError,
    /// 刹车状态
    #[serde(rename = "BrakeState")]
    brake_state: [u8; 6],
    /// 轴状态
    #[serde(rename = "nAxisStatus")]
    axis_status: [u8; 6],
    /// 轴错误代码
    #[serde(rename = "nAxisErrorCode")]
    axis_error_code: [u8; 6],
    /// 重置安全空间
    #[serde(rename = "nResetSafeSpace")]
    reset_safe_space: [u8; 1],
    /// 轴组状态
    #[serde(rename = "nAxisGroupStatus")]
    axis_group_status: [u8; 1],
    /// 轴组错误代码
    #[serde(rename = "nAxisGroupErrorCode")]
    axis_group_error_code: [u8; 1],
}

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct HardLoad {
    /// EtherCAT总帧数
    #[serde(rename = "EtherCAT_TotalFrame")]
    total_frame: u32,
    /// EtherCAT每秒帧数
    #[serde(rename = "EtherCAT_FramesPerSecond")]
    frames_per_second: u32,
    /// EtherCAT总丢帧数
    #[serde(rename = "EtherCAT_TotalLostFrame")]
    total_lost_frame: u32,
    /// EtherCAT发送错误帧数
    #[serde(rename = "EtherCAT_TxErrorFrame")]
    tx_error_frame: u32,
    /// EtherCAT接收错误帧数
    #[serde(rename = "EtherCAT_RxErrorFrame")]
    rx_error_frame: u32,
    /// 48V输入电压
    #[serde(rename = "Box48IN_Voltage")]
    input_voltage: f64,
    /// 48V输入电流
    #[serde(rename = "Box48IN_Current")]
    input_current: f64,
    /// 48V输出电压
    #[serde(rename = "Box48Out_Voltage")]
    output_voltage: f64,
    /// 48V输出电流
    #[serde(rename = "Box48Out_Current")]
    output_current: f64,
    /// 从站温度
    #[serde(rename = "Slave_temperature")]
    slave_temperature: [f64; 3],
    /// 从站电压
    #[serde(rename = "Slave_Voltage")]
    slave_voltage: [f64; 3],
}

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct FTData {
    /// 力控状态
    #[serde(rename = "FTControlState")]
    control_state: u8,
    /// 力控数据
    #[serde(rename = "FTData")]
    data: [f64; 6],
    /// 力控源数据
    #[serde(rename = "FTSrcData")]
    src_data: [f64; 6],
}

#[serde_as]
#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct Script {
    /// 错误代码
    #[serde(rename = "errorCode")]
    #[serde_as(as = "DisplayFromStr")]
    error_code: u16,
    /// 命令ID
    #[serde(rename = "cmdid")]
    cmd_id: [String; 6],
    /// 全局变量
    #[serde(rename = "GlobalVar")]
    global_var: Vec<()>,
}

#[derive(Default, Debug, Serialize, Deserialize, PartialEq)]
pub struct PluginsData {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn check_robot_state_serde() {
        let robot_state_json = r#"{
            "PosAndVel": {
                "Actual_Position": ["0.0","0.0","0.0","0.0","0.0","0.0","0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_PCS_TCP": ["0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_PCS_Base": ["0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_Joint_Current": ["0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_Joint_Velocity": ["0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_Joint_Acceleration": ["0.0","0.0","0.0","0.0","0.0","0.0"],
                "Actual_Override": "0.0"
            },
            "EndIO": {
                "EndDI": [0,0,0,0],
                "EndDO": [0,0,0,0],
                "EndButton": [0,0,0,0],
                "EnableEndBTN": 0,
                "EndAI": [0.00,0.00]
            },
            "ElectricBoxIO": {
                "BoxCI": [0,0,0,0,0,0,0,0],
                "BoxCO": [0,0,0,0,0,0,0,0],
                "BoxDI": [0,0,0,0,0,0,0,0],
                "BoxDO": [0,0,0,0,0,0,0,0],
                "Conveyor": "0.0",
                "Encode": 0
            },
            "ElectricBoxAnalogIO": {
                "BoxAnalogOutMode_1": 0,
                "BoxAnalogOutMode_2": 0,
                "BoxAnalogOut_1": "0.0",
                "BoxAnalogOut_2": "0.0",
                "BoxAnalogIn_1": "0.0",
                "BoxAnalogIn_2": "0.0"
            },
            "StateAndError": {
                "robotState": 0,
                "robotEnabled": 0,
                "robotPaused": 0,
                "robotMoving": 0,
                "robotBlendingDone": 0,
                "InPos": 0,
                "Error_AxisID": 0,
                "Error_Code": 0,
                "BrakeState": [0, 0, 0, 0, 0, 0],
                "nAxisStatus": [0, 0, 0, 0, 0, 0],
                "nAxisErrorCode": [0, 0, 0, 0, 0, 0],
                "nResetSafeSpace": [0],
                "nAxisGroupStatus": [0],
                "nAxisGroupErrorCode": [0]
            },
            "HardLoad": {
                "EtherCAT_TotalFrame": 0,
                "EtherCAT_FramesPerSecond": 0,
                "EtherCAT_TotalLostFrame": 0,
                "EtherCAT_TxErrorFrame": 0,
                "EtherCAT_RxErrorFrame": 0,
                "Box48IN_Voltage": 0.00,
                "Box48IN_Current": 0.00,
                "Box48Out_Voltage": 0.00,
                "Box48Out_Current": 0.00,
                "Slave_temperature": [0.00,0.00,0.00],
                "Slave_Voltage": [0.00,0.00,0.00]
            },
            "FTData": {
                "FTControlState": 0,
                "FTData": [0.00,0.00,0.00,0.00,0.00,0.00],
                "FTSrcData": [0.00,0.00,0.00,0.00,0.00,0.00]
            },
            "Script": {
                "errorCode": "0",
                "cmdid": ["","","","","",""],
                "GlobalVar": []
            },
            "pluginsdata": {}
        }"#;
        let robot_state = RobotState::default();
        assert_eq!(
            robot_state,
            serde_json::from_str::<RobotState>(robot_state_json).unwrap()
        );
        assert_eq!(
            robot_state,
            serde_json::from_value::<RobotState>(serde_json::to_value(&robot_state).unwrap())
                .unwrap()
        )
    }

    use serde::{Deserialize, Serialize};
    use serde_with::{DisplayFromStr, serde_as};

    #[serde_as]
    #[derive(Debug, PartialEq, Serialize, Deserialize)]
    struct TestStruct {
        #[serde(rename = "Value")]
        #[serde_as(as = "DisplayFromStr")]
        value: f64,
    }

    #[test]
    fn check_serde_with() {
        let test_struct = TestStruct { value: 0.0 };
        let test_struct_json = r#"{"Value":"0.0"}"#;

        // 测试 JSON -> Struct
        let parsed: TestStruct = serde_json::from_str(&test_struct_json).unwrap();
        assert_eq!(test_struct, parsed);

        // 测试 Struct -> JSON
        let serialized = serde_json::to_string(&test_struct).unwrap();
        assert_eq!(serialized, r#"{"Value":"0"}"#);
        // 注意：序列化后可能是 "0"，"0.0"，"0.0000" 等，具体格式受 f64 Display 的实现影响
    }

    #[serde_as]
    #[derive(Debug, PartialEq, Serialize, Deserialize)]
    struct TestStructArray {
        #[serde(rename = "Values")]
        #[serde_as(as = "[DisplayFromStr; 3]")]
        values: [f64; 3],
    }

    #[test]
    fn check_serde_with_array() {
        let test_struct_array = TestStructArray {
            values: [0.0, 0.0, 0.0],
        };
        let test_struct_array_json = r#"{"Values":["0.0","0.0","0.0"]}"#;

        // 测试 JSON -> Struct
        let parsed: TestStructArray = serde_json::from_str(&test_struct_array_json).unwrap();
        assert_eq!(test_struct_array, parsed);

        // 测试 Struct -> JSON
        let serialized = serde_json::to_string(&test_struct_array).unwrap();
        assert_eq!(serialized, r#"{"Values":["0","0","0"]}"#);
        // 注意：序列化后可能是 "0"，"0.0"，"0.0000" 等，具体格式受 f64 Display 的实现影响
    }
}
