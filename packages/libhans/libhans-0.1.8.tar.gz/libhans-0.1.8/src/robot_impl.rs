use inventory::submit;
use robot_behavior::RobotResult;

use crate::{Network, RobotMode, robot_param::HANS_DOF, types::*};

#[derive(Default)]
pub struct RobotImpl {
    pub network: Network,
}

pub type DispatchFn = fn(&mut RobotImpl, &str) -> RobotResult<String>;
pub struct CommandSubmit {
    pub fn_name: &'static str,
    pub dispatch: DispatchFn,
}
inventory::collect!(CommandSubmit);

macro_rules! submit {
    ($fn_name:ident) => {
        inventory::submit!(CommandSubmit {
            fn_name: stringify!($fn_name),
            dispatch: |robot: &mut RobotImpl, input: &str| -> RobotResult<String> {
                Ok(CommandSerde::to_string(&robot.$fn_name(CommandSerde::from_str(input)?)?))
            }
        });
    };
    ($($fn_name:ident),*) => {
        $(submit!($fn_name);)*
    };
}

macro_rules! cmd_fn {
    ($fn_name:ident, $req_type:ty, $res_type:ty) => {
        pub fn $fn_name(&mut self, _:()) -> RobotResult<()> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(()))?;
            response.status.map_err(Into::into)
        }
    };
    ($fn_name:ident, $req_type:ty, $res_type:ty;; $ret_type:ty) => {
        pub fn $fn_name(&mut self, _:()) -> RobotResult<$ret_type> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(()))?;
            Ok(response.status.unwrap())
        }
    };
    ($fn_name:ident, $req_type:ty, $res_type:ty; $($arg_name:ident: $arg_type:ty),*) => {
        pub fn $fn_name(&mut self, $($arg_name: $arg_type),*) -> RobotResult<()> {
            let _: $res_type = self.network.send_and_recv(&<$req_type>::from(($($arg_name),*)))?;
            Ok(())
        }
    };
    ($fn_name:ident, $req_type:ty, $res_type:ty; $($arg_name:ident: $arg_type:ty),* ; $ret_type:ty) => {
        pub fn $fn_name(&mut self, $($arg_name: $arg_type),*) -> RobotResult<$ret_type> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(($($arg_name),*)))?;
            response.status.map_err(Into::into)
        }
    };
    ($fn_name:ident<$const_ty:ty; $const_name:ident>, $req_type:ty, $res_type:ty) => {
        pub fn $fn_name<const $const_name: usize>(&mut self, argc: [$const_ty; $const_name]) -> RobotResult<[$const_ty; $const_name]> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(argc))?;
            response.status.map_err(Into::into)
        }
    };
    ($fn_name:ident<$const_ty:ty; $const_name:ident>, $req_type:ty, $res_type:ty;;  $ret_type:ty) => {
        pub fn $fn_name<const $const_name: usize>(&mut self, argc: [$const_ty; $const_name]) -> RobotResult<$ret_type> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(argc))?;
            Ok(response.status.unwrap())
        }
    };
    ($fn_name:ident<$const_name:ident>, $req_type:ty, $res_type:ty; $($arg_name:ident: $arg_type:ty),*) => {
        pub fn $fn_name<const $const_name: usize>(&mut self, $($arg_name: $arg_type),*) -> RobotResult<()> {
            let _: $res_type = self.network.send_and_recv(&<$req_type>::from(($($arg_name),*)))?;
            Ok(())
        }
    };
    ($fn_name:ident<$const_name:ident>, $req_type:ty, $res_type:ty; $($arg_name:ident: $arg_type:ty),* ; $ret_type:ty) => {
        pub fn $fn_name<const $const_name: usize>(&mut self, $($arg_name: $arg_type),*) -> RobotResult<$ret_type> {
            let response: $res_type = self.network.send_and_recv(&<$req_type>::from(($($arg_name),*)))?;
            response.status.map_err(Into::into)
        }
    };
}

impl RobotImpl {
    /// 新建一个机器人实例，使用传入的机器人 ip 与默认端口 [PORT_IF](crate::network::PORT_IF)
    pub fn new(ip: &str) -> Self {
        let network = Network::from_defult_port(ip);
        RobotImpl { network }
    }

    /// 连接网络，使用指定的 ip 与端口
    pub fn connect(&mut self, ip: &str, port: u16) {
        self.network.connect(ip, port).unwrap();
    }

    /// 断开网络连接
    pub fn disconnect(&mut self) {
        self.network.disconnect().unwrap();
    }

    pub fn is_connected(&self) -> bool {
        self.network.is_connected()
    }

    // ! 以下为机器人控制接口
    // ! 初始化指令

    pub fn power_off(&mut self) -> RobotResult<()> {
        let _: OSCmdResponse = self.network.send_and_recv(&OSCmdRequest::from(1))?;
        Ok(())
    }

    pub fn restart(&mut self) -> RobotResult<()> {
        let _: OSCmdResponse = self.network.send_and_recv(&OSCmdRequest::from(2))?;
        Ok(())
    }

    cmd_fn!(connect_to_box, ConnectToBoxRequest, ConnectToBoxResponse);
    cmd_fn!(robot_power_on, ElectrifyRequest, ElectrifyResponse);
    cmd_fn!(robot_power_off, BlackOutRequest, BlackOutResponse);
    cmd_fn!(
        connect_to_controller,
        StartMasterRequest,
        StartMasterResponse
    );
    cmd_fn!(
        disconnect_from_controller,
        CloseMasterRequest,
        CloseMasterResponse
    );
    cmd_fn!(is_simulation, IsSimulationRequest, IsSimulationResponse;; bool);
    cmd_fn!(is_controller_started, ReadControllerStateRequest, ReadControllerStateResponse;; bool);

    // ! 机器人轴组控制指令

    cmd_fn!(robot_model, ReadRobotModelRequest, ReadRobotModelResponse; id: u8; u16);
    cmd_fn!(robot_enable, GrpEnableRequest, GrpEnableResponse; id: u8);
    cmd_fn!(robot_disable, GrpDisableRequest, GrpDisableResponse; id: u8);
    cmd_fn!(robot_reset, GrpResetRequest, GrpResetResponse; id: u8);
    cmd_fn!(robot_move_stop, GrpStopRequest, GrpStopResponse; id: u8);
    cmd_fn!(robot_move_pause, GrpInterruptRequest, GrpInterruptResponse; id: u8);
    cmd_fn!(robot_move_continue, GrpContinueRequest, GrpContinueResponse; id: u8);
    cmd_fn!(robot_free_driver_open, GrpOpenFreeDriverRequest, GrpOpenFreeDriverResponse; id: u8);
    cmd_fn!(robot_free_driver_close, GrpCloseFreeDriverRequest, GrpCloseFreeDriverResponse; id: u8);

    // ! 电箱控制指令
    cmd_fn!(box_info, ReadBoxInfoRequest, ReadBoxInfoResponse; id: u8; BoxInfo);
    cmd_fn!(box_control_input<bool; N>, ReadBoxCIRequest<N>, ReadBoxCIResponse<N>);
    cmd_fn!(box_control_output<bool; N>, ReadBoxCORequest<N>, ReadBoxCOResponse<N>);
    cmd_fn!(box_digital_input<bool; N>, ReadBoxDIRequest<N>, ReadBoxDIResponse<N>);
    cmd_fn!(box_digital_output<bool; N>, ReadBoxDORequest<N>, ReadBoxDOResponse<N>);
    cmd_fn!(box_analog_input<f64; N>, ReadBoxAIRequest<N>, ReadBoxAIResponse<N>);
    cmd_fn!(box_analog_output<f64; N>, ReadBoxAORequest<N>, ReadBoxAOResponse<N>);
    cmd_fn!(box_end_digital_input<N>, ReadEIRequest<N>, ReadEIResponse<N>; id_port: (u8,[u8;N]); [bool;N]);
    cmd_fn!(box_end_digital_output<N>, ReadEORequest<N>, ReadEOResponse<N>; id_port: (u8,[u8;N]); [bool;N]);
    cmd_fn!(box_end_analog_input, ReadEAIRequest, ReadEAIResponse; id: (u8,u8); f64);
    cmd_fn!(box_set_control_output, SetBoxCORequest, SetBoxCOResponse; id_out: (u8,bool));
    cmd_fn!(box_set_digital_output, SetBoxDORequest, SetBoxDOResponse; id_out: (u8,bool));
    cmd_fn!(box_set_analog_output_mode, SetBoxAOModeRequest, SetBoxAOModeResponse; id_mode: (u8,u8));
    cmd_fn!(box_set_analog_output, SetBoxAORequest, SetBoxAOResponse; id_out_mode: (u8,f64,u8));
    cmd_fn!(box_set_end_digital_output, SetEndDORequest, SetEndDOResponse; id_out: (u8,u8,bool));

    // ! 机器人状态指令
    cmd_fn!(state_set_override, SetOverrideRequest, SetOverrideResponse; id_value: (u8,f64));
    cmd_fn!(state_set_tool_motion, SetToolMotionRequest, SetToolMotionResponse; id_value: (u8,bool));
    cmd_fn!(state_set_payload, SetPayloadRequest, SetPayloadResponse; id_value: (u8,Load));
    cmd_fn!(state_set_joint_max_vel, SetJointMaxVelRequest, SetJointMaxVelResponse; id_value: (u8,[f64;HANS_DOF]));
    cmd_fn!(state_set_joint_max_acc, SetJointMaxAccRequest, SetJointMaxAccResponse; id_value: (u8,[f64;HANS_DOF]));
    cmd_fn!(state_set_linear_max_vel, SetLinearMaxVelRequest, SetLinearMaxVelResponse; id_value: (u8,f64));
    cmd_fn!(state_set_linear_max_acc, SetLinearMaxAccRequest, SetLinearMaxAccResponse; id_value: (u8,f64));
    cmd_fn!(state_read_joint_max_vel, ReadJointMaxVelRequest, ReadJointMaxVelResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_joint_max_acc, ReadJointMaxAccRequest, ReadJointMaxAccResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_joint_max_jerk, ReadJointMaxJerkRequest, ReadJointMaxJerkResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_linear_max_vel, ReadLinearMaxVelRequest, ReadLinearMaxVelResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_emergency_info, ReadEmergencyInfoRequest, ReadEmergencyInfoResponse; id: u8; EmergencyInfo);
    cmd_fn!(state_read_robot_state, ReadRobotStateRequest, ReadRobotStateResponse; id: u8; RobotFlag);
    cmd_fn!(state_read_axis_error_code, ReadAxisErrorCodeRequest, ReadAxisErrorCodeResponse; id: u8; [u16;HANS_DOF]);
    cmd_fn!(state_read_cur_fsm, ReadCurFSMRequest, ReadCurFSMResponse; id: u8; RobotMode);
    cmd_fn!(state_read_cmd_pos, ReadCmdPosRequest, ReadCmdPosResponse; id: u8; CmdPose);
    cmd_fn!(state_read_act_pos, ReadActPosRequest, ReadActPosResponse; id: u8; ActPose);
    cmd_fn!(state_read_cmd_joint_vel, ReadCmdJointVelRequest, ReadCmdJointVelResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_act_joint_vel, ReadActJointVelRequest, ReadActJointVelResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_cmd_tcp_vel, ReadCmdTcpVelRequest, ReadCmdTcpVelResponse; id: u8; [f64; 6]);
    cmd_fn!(state_read_act_tcp_vel, ReadActTcpVelRequest, ReadActTcpVelResponse; id: u8; [f64; 6]);
    cmd_fn!(state_read_cmd_joint_cur, ReadCmdJointCurRequest, ReadCmdJointCurResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_act_joint_cur, ReadActJointCurRequest, ReadActJointCurResponse; id: u8; [f64;HANS_DOF]);
    cmd_fn!(state_read_tcp_vel, ReadTcpVelocityRequest, ReadTcpVelocityResponse; id: u8; (f64,f64));

    // ! 坐标系读写指令
    cmd_fn!(set_pose_o_to_t, SetCurTCPRequest, SetCurTCPResponse; id_pose: (u8,[f64;6]));
    cmd_fn!(set_pose_u_to_t, SetCurUCSRequest, SetCurUCSResponse; id_pose: (u8,[f64;6]));
    cmd_fn!(read_pose_o_to_t, ReadCurTCPRequest, ReadCurTCPResponse; id_pose: u8; [f64;6]);
    cmd_fn!(read_pose_u_to_t, ReadCurUCSRequest, ReadCurUCSResponse; id_pose: u8; [f64;6]);

    // ! 力控指令
    cmd_fn!(force_control, SetForceControlStateRequest, SetForceControlStateResponse; id_state: (u8,bool));
    cmd_fn!(force_control_mode, ReadFTControlStateRequest, ReadFTControlStateResponse; id: u8; bool);
    cmd_fn!(force_tool_coord, SetForceToolCoordinateMotionRequest, SetForceToolCoordinateMotionResponse; id_mode: (u8,bool));
    cmd_fn!(force_interrupt, GrpFCInterruptRequest, GrpFCInterruptResponse; id: u8);
    cmd_fn!(force_continue, GrpFCContinueRequest, GrpFCContinueResponse; id: u8);
    cmd_fn!(force_zero, SetForceZeroRequest, SetForceZeroResponse; id: u8);
    cmd_fn!(force_max_search_vel, HRSetMaxSearchVelocitiesRequest, HRSetMaxSearchVelocitiesResponse; id_v_w: (u8,f64,f64));
    cmd_fn!(force_control_strategy, HRSetForceControlStrategyRequest, HRSetForceControlStrategyResponse; id_mode: (u8,u8));
    cmd_fn!(force_set_senor_pose_f_to, SetFTPositionRequest, SetFTPositionResponse; id_pos: (u8,[f64;6]));
    cmd_fn!(force_pid_control_params, HRSetPIDControlParamsRequest, HRSetPIDControlParamsResponse; id_params: (u8,[f64; HANS_DOF]));
    cmd_fn!(force_mass_params, HRSetMassParamsRequest, HRSetMassParamsResponse; id_params: (u8,[f64;6]));
    cmd_fn!(force_damp_params, HRSetDampParamsRequest, HRSetDampParamsResponse; id_params: (u8,[f64;6]));
    cmd_fn!(force_stiff_params, HRSetStiffParamsRequest, HRSetStiffParamsResponse; id_params: (u8,[f64;6]));
    cmd_fn!(force_control_goal, HRSetControlGoalRequest, HRSetControlGoalResponse; id_goal: (u8,[f64;6],f64));
    cmd_fn!(force_free_drive, SetForceFreeDriveModeRequest, SetForceFreeDriveModeResponse; id_mode: (u8,bool));
    cmd_fn!(force_senor_data, ReadFTCabDataRequest, ReadFTCabDataResponse; id: u8; [f64;6]);

    // ! 运动生成指令
    cmd_fn!(move_joint_rel, MoveRelJRequest, MoveRelJResponse; id_dir_dis: (u8, RelJ));
    cmd_fn!(move_line_rel, MoveRelLRequest, MoveRelLResponse; id_dir_dis_coord: (u8, RelL));
    cmd_fn!(move_way_point_rel, WayPointRelRequest, WayPointRelResponse; id_way_point_rel: (u8, WayPointRel));
    cmd_fn!(move_way_point_ex, WayPointExRequest, WayPointExResponse; id_way_point_ex: (u8, WayPointEx));
    cmd_fn!(move_way_point, WayPointRequest, WayPointResponse; id_way_point: (u8, WayPoint));
    cmd_fn!(move_way_point2, WayPoint2Request, WayPoint2Response; id_way_point2: (u8, WayPoint2));
    cmd_fn!(move_joint, MoveJRequest, MoveJResponse; id_joint: (u8, MoveJ));
    cmd_fn!(move_line, MoveLRequest, MoveLResponse; id_line: (u8, MoveL));
    cmd_fn!(move_circle, MoveCRequest, MoveCResponse; id_circle: (u8, MoveC));
    cmd_fn!(start_push_move_path_j, StartPushMovePathRequest, StartPushMovePathResponse; id_config: (u8, StartPushMovePathJ));
    cmd_fn!(push_move_path_j, PushMovePathJRequest, PushMovePathJResponse; id_path: (u8, String, [f64;HANS_DOF]));
    cmd_fn!(end_push_move_path, EndPushMovePathRequest, EndPushMovePathResponse; id_path: (u8, String));
    cmd_fn!(move_path_j, MovePathRequest, MovePathResponse; id_path: (u8, String));
    cmd_fn!(read_move_path_state, ReadMovePathStateRequest, ReadMovePathStateResponse; id_path: (u8, String); u8);
    cmd_fn!(update_move_path_name, UpdateMovePathNameRequest, UpdateMovePathNameResponse; id_path_new: (u8, String, String));
    cmd_fn!(del_move_path, DelMovePathRequest, DelMovePathResponse; id_path: (u8, String));
    cmd_fn!(read_soft_motion_process, ReadSoftMotionProcessRequest, ReadSoftMotionProcessResponse; id:u8; (f64, u16));
    cmd_fn!(start_push_move_path_l, InitMovePathLRequest, InitMovePathLResponse; id_config: (u8, StartPushMovePathL));
    cmd_fn!(push_move_path_l, PushMovePathLRequest, PushMovePathLResponse; id_path: (u8, [f64;6]));
    cmd_fn!(push_move_paths, PushMovePathsRequest<HANS_DOF>, PushMovePathsResponse; id_paths: (u8, MovePaths<HANS_DOF>));
    cmd_fn!(move_path_l, MovePathLRequest, MovePathLResponse; id_path: (u8, String));
    cmd_fn!(set_move_path_override, SetMovePathOverrideRequest, SetMovePathOverrideResponse; id_value: (u8, f64));
    cmd_fn!(start_servo, StartServoRequest, StartServoResponse; id_v_a: (u8, f64, f64));
    cmd_fn!(push_servo_j, PushServoJRequest, PushServoJResponse; id_joint: (u8, [f64;HANS_DOF]));
    cmd_fn!(push_servo_p, PushServoPRequest, PushServoPResponse; id_pose_tcp_ucs: (u8, [[f64;6];3]));
}

submit!(
    connect_to_box,
    robot_power_on,
    robot_power_off,
    connect_to_controller,
    disconnect_from_controller,
    is_simulation,
    is_controller_started
);
submit!(
    robot_model,
    robot_enable,
    robot_disable,
    robot_reset,
    robot_move_stop,
    robot_move_pause,
    robot_move_continue,
    robot_free_driver_open,
    robot_free_driver_close
);
submit!(
    box_info,
    box_end_analog_input,
    box_set_control_output,
    box_set_digital_output,
    box_set_analog_output_mode,
    box_set_analog_output,
    box_set_end_digital_output
);
submit!(
    state_set_override,
    state_set_tool_motion,
    state_set_payload,
    state_set_joint_max_vel,
    state_set_joint_max_acc,
    state_set_linear_max_vel,
    state_set_linear_max_acc,
    state_read_joint_max_vel,
    state_read_joint_max_acc,
    state_read_joint_max_jerk,
    state_read_linear_max_vel,
    state_read_emergency_info,
    state_read_robot_state,
    state_read_axis_error_code,
    state_read_cur_fsm,
    state_read_cmd_pos,
    state_read_act_pos,
    state_read_cmd_joint_vel,
    state_read_act_joint_vel,
    state_read_cmd_tcp_vel,
    state_read_act_tcp_vel,
    state_read_cmd_joint_cur,
    state_read_act_joint_cur,
    state_read_tcp_vel
);
submit!(
    set_pose_o_to_t,
    set_pose_u_to_t,
    read_pose_o_to_t,
    read_pose_u_to_t
);
submit!(
    force_control,
    force_control_mode,
    force_tool_coord,
    force_interrupt,
    force_continue,
    force_zero,
    force_max_search_vel,
    force_control_strategy,
    force_set_senor_pose_f_to,
    force_pid_control_params,
    force_mass_params,
    force_damp_params,
    force_stiff_params,
    force_control_goal,
    force_free_drive,
    force_senor_data
);
submit!(
    move_joint_rel,
    move_line_rel,
    move_way_point_rel,
    move_way_point_ex,
    move_way_point,
    move_way_point2,
    move_joint,
    move_line,
    move_circle,
    start_push_move_path_j,
    push_move_path_j,
    end_push_move_path,
    move_path_j,
    read_move_path_state,
    update_move_path_name,
    del_move_path,
    read_soft_motion_process,
    start_push_move_path_l,
    push_move_path_l,
    push_move_paths,
    move_path_l,
    set_move_path_override,
    start_servo,
    push_servo_j,
    push_servo_p
);
